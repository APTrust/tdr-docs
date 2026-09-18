#!/usr/bin/env python3
"""Convert the TDR docs Markdown into Word documents for review in Google Drive.

Run it from anywhere:

    python3 scripts/docs_to_docx.py

By default it writes one .docx per section into review/. See scripts/README.md for
the full review workflow.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

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
        help="write one Word file per page instead of one per section",
    )
    args = parser.parse_args()

    require_pandoc()

    out_root = Path(args.out)
    if not out_root.is_absolute():
        out_root = REPO_ROOT / out_root

    sections = collect_sections()
    if args.section:
        sections = [s for s in sections if s["slug"] == args.section]
        if not sections:
            known = ", ".join(s["slug"] for s in collect_sections())
            fail(f"no section named '{args.section}'. Try one of: {known}")

    stamp = build_stamp()
    base_url = repo_url()
    written = []

    for section in sections:
        resource_dirs = [DOCS, section["directory"]]

        if args.per_page:
            for page in section["pages"]:
                block, _ = split_front_matter(page.read_text(encoding="utf-8"))
                title = front_matter_value(block, "title") or page.stem
                output = out_root / section["slug"] / f"{page.stem}.docx"
                run_pandoc(
                    prepare_body(page, base_url), output, title, stamp,
                    resource_dirs, toc=False,
                )
                written.append(output)
            continue

        markdown = PAGE_BREAK.join(
            prepare_body(page, base_url) for page in section["pages"]
        )
        output = out_root / f"{section['sequence']}-{section['slug']}.docx"
        run_pandoc(markdown, output, section["title"], stamp, resource_dirs, toc=True)
        written.append(output)

    print(f"\n{stamp}\n")
    for path in written:
        print(f"  {display_path(path)}")
    print(f"\n{len(written)} file(s) written. Upload them to Google Drive to start a review.\n")


if __name__ == "__main__":
    main()
