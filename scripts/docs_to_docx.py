#!/usr/bin/env python3
"""Convert the TDR docs Markdown into Word documents for review in Google Drive.

Run it from anywhere:

    python3 scripts/docs_to_docx.py

By default it writes one folder per section into review/, each holding one .docx per
three-number criterion (4.1.1, 4.1.2, ...) with that criterion's sub-criteria folded
in, plus a tracking spreadsheet listing every page and the document it landed in.
See scripts/README.md for the full review workflow.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"

# Source links point at the branch rather than the commit the review copy was made
# from, so they always open the page as it stands now — which is the version a
# reviewer's change has to be applied to. The commit the copy came from is recorded
# on each document's title page.
BRANCH = "main"
FALLBACK_REPO_URL = "https://github.com/APTrust/tdr-docs"

# Folders under docs/ that hold assets rather than pages.
NOT_SECTIONS = {"img", "stylesheets"}

# The two pages that sit at the top of docs/ rather than in a section folder.
ROOT_BUNDLE = {"slug": "overview", "sequence": "01", "title": "Overview"}

# How many numbers of the ISO criterion number a review document is split on: 3 puts
# 4.2.4 and everything beneath it (4.2.4.1, 4.2.4.1.1, ...) into one file.
GROUP_DEPTH = 3

# Characters that Windows, macOS or Google Drive refuse or mangle in a file name.
UNSAFE_IN_FILENAME = re.compile(r'[\\/:*?"<>|]')

# The tracking spreadsheet: one row per page, filled in by hand during the review.
TRACKER_COLUMNS = [
    # (heading, width in characters)
    ("Status", 16),
    ("Section Title", 70),
    ("1st Review Date", 16),
    ("Group Review Date", 18),
    ("Applied to Markdown", 22),
    ("Document", 60),
    ("Notes", 50),
]

# Shown in the Document column for a page that shares the document named above it.
DITTO = '"'

FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)

# A page break, so each criterion starts on a fresh page in Word.
PAGE_BREAK = (
    '\n```{=openxml}\n'
    '<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n'
    '```\n\n'
)


def fail(message):
    sys.exit(f"\nerror: {message}\n")


def require_pandoc():
    if shutil.which("pandoc"):
        return
    fail(
        "pandoc is not installed, and this script needs it to write Word files.\n\n"
        "  On a Mac:    brew install pandoc\n"
        "  On Windows:  download the installer from https://pandoc.org/installing.html\n\n"
        "Install it, open a new terminal, and run this script again."
    )


def split_front_matter(text):
    """Return (front_matter_block, body) — front matter is '' when there is none."""
    match = FRONT_MATTER.match(text)
    if not match:
        return "", text
    return match.group(1), text[match.end():]


def front_matter_value(block, key):
    match = re.search(rf'^{key}:[ \t]*(.*?)[ \t]*$', block, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().strip('"').strip("'")


def page_order(path):
    """Sort key putting a section's index.md first, then plain alphabetical.

    Filenames carry a zero-padded sequence prefix, so alphabetical order is already
    ISO criterion order. Only index.md needs lifting out of it.
    """
    return (path.name != "index.md", path.name)


def display_path(path):
    """Repo-relative when the file is inside the repo, absolute when --out is elsewhere."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def repo_url():
    """The repository's web address, taken from repo_url in mkdocs.yml."""
    match = re.search(
        r"^repo_url:[ \t]*(\S+)", (REPO_ROOT / "mkdocs.yml").read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    return match.group(1).rstrip("/") if match else FALLBACK_REPO_URL


def source_note(path, base_url):
    """A link back to the page on GitHub, shown as its path so it reads as one."""
    relative = path.relative_to(REPO_ROOT).as_posix()
    return f"*Source: [{relative}]({base_url}/blob/{BRANCH}/{relative})*"


def prepare_body(path, base_url):
    """Strip front matter and add the source-file note under the page's H1."""
    _, body = split_front_matter(path.read_text(encoding="utf-8"))
    lines = body.strip().split("\n")
    note = source_note(path, base_url)

    for index, line in enumerate(lines):
        if line.startswith("# "):
            lines.insert(index + 1, "\n" + note)
            return "\n".join(lines)

    return note + "\n\n" + "\n".join(lines)


def build_stamp():
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit = "unknown"
    return f"Review copy generated {date.today().isoformat()} from commit {commit}"


def run_pandoc(markdown, output, title, stamp, resource_dirs, toc):
    output.parent.mkdir(parents=True, exist_ok=True)
    resource_path = os.pathsep.join(str(d) for d in resource_dirs)

    command = [
        "pandoc",
        "--from=markdown",
        "--to=docx",
        "--standalone",
        f"--resource-path={resource_path}",
        "--metadata", f"title={title}",
        "--metadata", "subtitle=APTrust ISO 16363 self-assessment",
        "--metadata", f"date={stamp}",
        "--output", str(output),
    ]
    if toc:
        command += ["--toc", "--toc-depth=1"]

    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", encoding="utf-8", delete=False
    ) as handle:
        handle.write(markdown)
        temp_path = handle.name

    try:
        result = subprocess.run(
            command + [temp_path], cwd=REPO_ROOT, capture_output=True, text=True
        )
    finally:
        os.unlink(temp_path)

    if result.returncode != 0:
        fail(f"pandoc could not convert {title}:\n\n{result.stderr.strip()}")


def page_front_matter(path):
    block, _ = split_front_matter(path.read_text(encoding="utf-8"))
    return block


def plain_number(sequence):
    """Turn a zero-padded sequence into a criterion number: 04.02.10 -> 4.2.10."""
    return ".".join(str(int(part)) for part in sequence.split("."))


def group_pages(section):
    """Split a section's pages into review documents, one per three-number criterion.

    A page joins the group named by the first GROUP_DEPTH numbers of its sequence, so
    a criterion and all its sub-criteria travel together. Pages with a one-number
    sequence or none at all — the section landing page, and both root pages — form the
    section's overview document.
    """
    groups = {}
    for page in section["pages"]:
        sequence = front_matter_value(page_front_matter(page), "sequence") or ""
        parts = sequence.split(".") if sequence else []
        key = ".".join(parts[:GROUP_DEPTH]) if len(parts) > 1 else ""
        groups.setdefault(key, []).append(page)

    documents = []
    for key in sorted(groups):
        pages = groups[key]
        if not key:
            title = f"{plain_number(section['sequence'])}.0 Overview"
        else:
            # The first page is the three-number criterion itself: its filename is
            # the shortest in the group, so it sorts ahead of its sub-criteria.
            block = page_front_matter(pages[0])
            number = front_matter_value(block, "number") or plain_number(key)
            name = front_matter_value(block, "title") or pages[0].stem
            if name.startswith(number + " "):
                name = name[len(number) + 1:]
            combined = "Combined - " if len(pages) > 1 else ""
            title = f"{number} {combined}{name}"
        documents.append({"title": title, "pages": pages})

    return documents


def page_documents(section):
    """The --per-page equivalent of group_pages: every page is its own document."""
    return [{"title": page.stem, "pages": [page]} for page in section["pages"]]


def page_label(page):
    """A page's name for the tracking spreadsheet, led by its criterion number."""
    block, body = split_front_matter(page.read_text(encoding="utf-8"))
    title = front_matter_value(block, "title")
    if not title:
        heading = re.search(r"^# +(.+)$", body, re.MULTILINE)
        title = heading.group(1).strip() if heading else page.stem

    # TDR titles already open with their number; OAIS titles do not.
    sequence = front_matter_value(block, "sequence") or ""
    if "." in sequence and not title[0].isdigit():
        title = f"{plain_number(sequence)} {title}"
    return title


def tracker_rows(bundles):
    """Rows for the tracking sheet as (kind, cells), kind being 'band' or 'page'."""
    rows = []
    for section, documents in bundles:
        rows.append(("band", [section["title"]]))
        for document in documents:
            for index, page in enumerate(document["pages"]):
                # The file's name, so it matches what reviewers see in Drive.
                name = safe_filename(document["title"]) if index == 0 else DITTO
                rows.append(("page", ["", page_label(page), "", "", "", name, ""]))
    return rows


def column_letter(index):
    return chr(ord("A") + index)


def sheet_xml(title, rows):
    """The worksheet: a title row, the column headings, then one row per page."""
    last = column_letter(len(TRACKER_COLUMNS) - 1)
    merges = [f"A1:{last}1"]

    def cell(column, row, text, style):
        ref = f"{column_letter(column)}{row}"
        if text == "":
            return f'<c r="{ref}" s="{style}"/>'
        return (
            f'<c r="{ref}" s="{style}" t="inlineStr">'
            f'<is><t xml:space="preserve">{escape(text)}</t></is></c>'
        )

    def row_xml(number, cells, style):
        padded = cells + [""] * (len(TRACKER_COLUMNS) - len(cells))
        body = "".join(cell(i, number, text, style) for i, text in enumerate(padded))
        return f'<row r="{number}">{body}</row>'

    lines = [
        row_xml(1, [title], 1),
        row_xml(2, [heading for heading, _ in TRACKER_COLUMNS], 2),
    ]
    for number, (kind, cells) in enumerate(rows, start=3):
        if kind == "band":
            merges.append(f"A{number}:{last}{number}")
            lines.append(row_xml(number, cells, 3))
        else:
            lines.append(row_xml(number, cells, 4))

    columns = "".join(
        f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>'
        for i, (_, width) in enumerate(TRACKER_COLUMNS, start=1)
    )
    merge_cells = "".join(f'<mergeCell ref="{ref}"/>' for ref in merges)

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        # Keep the title and column headings in view while scrolling.
        '<sheetViews><sheetView workbookViewId="0">'
        '<pane ySplit="2" topLeftCell="A3" activePane="bottomLeft" state="frozen"/>'
        '</sheetView></sheetViews>'
        f'<cols>{columns}</cols>'
        f'<sheetData>{"".join(lines)}</sheetData>'
        f'<mergeCells count="{len(merges)}">{merge_cells}</mergeCells>'
        '</worksheet>'
    )


# Cell styles, by index: 0 default, 1 sheet title, 2 column heading, 3 section band,
# 4 page row.
STYLES_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
    '<fonts count="3">'
    '<font><sz val="11"/><name val="Arial"/></font>'
    '<font><b/><sz val="11"/><name val="Arial"/></font>'
    '<font><b/><sz val="14"/><name val="Arial"/></font>'
    '</fonts>'
    '<fills count="4">'
    '<fill><patternFill patternType="none"/></fill>'
    '<fill><patternFill patternType="gray125"/></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FFD9D9D9"/></patternFill></fill>'
    '<fill><patternFill patternType="solid"><fgColor rgb="FFEFEFEF"/></patternFill></fill>'
    '</fills>'
    '<borders count="2">'
    '<border><left/><right/><top/><bottom/><diagonal/></border>'
    '<border>'
    '<left style="thin"><color rgb="FFBFBFBF"/></left>'
    '<right style="thin"><color rgb="FFBFBFBF"/></right>'
    '<top style="thin"><color rgb="FFBFBFBF"/></top>'
    '<bottom style="thin"><color rgb="FFBFBFBF"/></bottom>'
    '<diagonal/></border>'
    '</borders>'
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
    '<cellXfs count="5">'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
    '<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
    '<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1"'
    ' applyFill="1" applyBorder="1" applyAlignment="1">'
    '<alignment vertical="top" wrapText="1"/></xf>'
    '<xf numFmtId="0" fontId="1" fillId="3" borderId="1" xfId="0" applyFont="1"'
    ' applyFill="1" applyBorder="1"/>'
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1"'
    ' applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>'
    '</cellXfs>'
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
    '</styleSheet>'
)


def write_tracker(output, title, rows):
    """Write the tracking spreadsheet. An .xlsx is a zip of XML, so no library is needed."""
    main = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    package = "http://schemas.openxmlformats.org/package/2006"
    kind = "application/vnd.openxmlformats-officedocument.spreadsheetml"
    declaration = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'

    parts = {
        "[Content_Types].xml": (
            f'{declaration}<Types xmlns="{package}/content-types">'
            '<Default Extension="rels"'
            ' ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            f'<Override PartName="/xl/workbook.xml" ContentType="{kind}.sheet.main+xml"/>'
            f'<Override PartName="/xl/worksheets/sheet1.xml" ContentType="{kind}.worksheet+xml"/>'
            f'<Override PartName="/xl/styles.xml" ContentType="{kind}.styles+xml"/>'
            '</Types>'
        ),
        "_rels/.rels": (
            f'{declaration}<Relationships xmlns="{package}/relationships">'
            f'<Relationship Id="rId1" Type="{rel}/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>'
        ),
        "xl/workbook.xml": (
            f'{declaration}<workbook xmlns="{main}" xmlns:r="{rel}">'
            '<sheets><sheet name="Tracking" sheetId="1" r:id="rId1"/></sheets>'
            '</workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            f'{declaration}<Relationships xmlns="{package}/relationships">'
            f'<Relationship Id="rId1" Type="{rel}/worksheet" Target="worksheets/sheet1.xml"/>'
            f'<Relationship Id="rId2" Type="{rel}/styles" Target="styles.xml"/>'
            '</Relationships>'
        ),
        "xl/styles.xml": STYLES_XML,
        "xl/worksheets/sheet1.xml": sheet_xml(title, rows),
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)


def safe_filename(title):
    # A title that ends in a full stop would otherwise give "name..docx".
    return UNSAFE_IN_FILENAME.sub("-", title).strip().rstrip(".")


def collect_sections():
    """Return the review bundles, in ISO order: the root pages, then each folder."""
    root_pages = sorted(
        (p for p in DOCS.glob("*.md")), key=page_order
    )
    sections = [{**ROOT_BUNDLE, "pages": root_pages, "directory": DOCS}]

    for directory in sorted(d for d in DOCS.iterdir() if d.is_dir()):
        if directory.name in NOT_SECTIONS:
            continue

        pages = sorted(directory.glob("*.md"), key=page_order)
        if not pages:
            continue

        landing = directory / "index.md"
        block = ""
        if landing.exists():
            block, _ = split_front_matter(landing.read_text(encoding="utf-8"))

        sections.append({
            "slug": directory.name,
            "sequence": front_matter_value(block, "sequence") or "99",
            "title": front_matter_value(block, "section") or directory.name,
            "pages": pages,
            "directory": directory,
        })

    return sections


def main():
    parser = argparse.ArgumentParser(
        description="Convert the TDR docs Markdown into Word files for review."
    )
    parser.add_argument(
        "--out", default="review", metavar="DIR",
        help="where to write the Word files (default: review)",
    )
    parser.add_argument(
        "--section", metavar="NAME",
        help="convert one section only, e.g. tdr-3 or overview",
    )
    parser.add_argument(
        "--per-page", action="store_true",
        help="write one Word file per page instead of one per three-number criterion",
    )
    args = parser.parse_args()

    require_pandoc()

    out_root = Path(args.out)
    if not out_root.is_absolute():
        out_root = REPO_ROOT / out_root

    split = page_documents if args.per_page else group_pages
    all_bundles = [(section, split(section)) for section in collect_sections()]
    bundles = all_bundles
    if args.section:
        bundles = [b for b in all_bundles if b[0]["slug"] == args.section]
        if not bundles:
            known = ", ".join(section["slug"] for section, _ in all_bundles)
            fail(f"no section named '{args.section}'. Try one of: {known}")

    stamp = build_stamp()
    base_url = repo_url()
    written = []

    for section, documents in bundles:
        resource_dirs = [DOCS, section["directory"]]
        # The sequence prefix makes Google Drive sort the folders in ISO order.
        section_out = out_root / f"{section['sequence']}-{section['slug']}"

        for document in documents:
            pages = document["pages"]
            title = document["title"]
            if args.per_page:
                title = front_matter_value(page_front_matter(pages[0]), "title") or title
            markdown = PAGE_BREAK.join(prepare_body(page, base_url) for page in pages)
            output = section_out / f"{safe_filename(document['title'])}.docx"
            run_pandoc(
                markdown, output, title, stamp, resource_dirs, toc=len(pages) > 1,
            )
            written.append(output)

    # The tracker always lists every section, so converting a single section with
    # --section never replaces it with a partial one.
    tracker_title = f"TDR Review {date.today().year} Tracking"
    tracker = out_root / f"{tracker_title}.xlsx"
    write_tracker(tracker, tracker_title, tracker_rows(all_bundles))

    print(f"\n{stamp}\n")
    for path in written:
        print(f"  {display_path(path)}")
    print(f"\n{len(written)} Word file(s) written, plus the tracking spreadsheet:\n")
    print(f"  {display_path(tracker)}")
    print("\nUpload the folders and the spreadsheet to Google Drive to start a review.\n")


if __name__ == "__main__":
    main()
