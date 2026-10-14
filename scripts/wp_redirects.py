#!/usr/bin/env python3
"""Generate the aptrust.org redirect table for the TDR pages that moved to docs.aptrust.org.

Run it from anywhere:

    python3 scripts/wp_redirects.py

Every page migrated from WordPress records its old address in `source_url:` front matter.
This turns those into a PHP file that the aptrust.org theme loads to send each old URL to
its new page with a 301. By default it writes straight into a sibling checkout of the theme
repo; see scripts/README.md for deploying it.

Re-run it whenever a page in docs/ is renamed or moved. Otherwise the old WordPress URL
still redirects to the page's previous address, which is now a 404.
"""

import argparse
import sys
from pathlib import Path
from urllib.parse import urlsplit

from docs_to_docx import DOCS, REPO_ROOT, display_path, front_matter_value, split_front_matter

NEW_BASE = "https://docs.aptrust.org/tdr/"

# The top-level WordPress slugs the TDR section lived under. Any URL under one of these that
# is not in the table still redirects, to the TDR landing page. Nothing else on aptrust.org
# uses them.
PREFIXES = [
    "trusted-digital-repository",
    "oais-documents",
    "tdr-3-0-organizational-infrastructure",
    "tdr-4-0-digital-object-management",
    "tdr-5-0-governance",
]

# The number of pages scraped from WordPress that still exist there. A different count means
# a source_url was added, lost or edited, and the table should be checked before it ships.
EXPECTED = 119

DEFAULT_OUT = (
    REPO_ROOT.parent
    / "aptrust-wordpress-theme/wp-content/themes/aptrust/includes/tdr_redirects.php"
)


def fail(message):
    sys.exit(f"\nwp_redirects.py: {message}\n")


def old_path(url):
    """https://aptrust.org/documentation-page/a/b/ -> documentation-page/a/b"""
    parts = urlsplit(url)
    if parts.netloc != "aptrust.org":
        fail(f"source_url is not on aptrust.org: {url}")
    path = parts.path.strip("/")
    segments = path.split("/")
    if len(segments) < 2 or segments[0] != "documentation-page" or segments[1] not in PREFIXES:
        fail(f"source_url is outside the TDR section: {url}")
    return path


def new_path(md_file):
    """docs/tdr-4/04.02.04-slug.md -> tdr-4/04.02.04-slug/ ; docs/tdr-4/index.md -> tdr-4/"""
    rel = md_file.relative_to(DOCS).with_suffix("")
    if rel.name == "index":
        rel = rel.parent
    return "" if str(rel) == "." else f"{rel.as_posix()}/"


def build_map():
    table = {}
    for md_file in sorted(DOCS.rglob("*.md")):
        block, _ = split_front_matter(md_file.read_text(encoding="utf-8"))
        url = front_matter_value(block, "source_url")
        if not url:
            continue
        key = old_path(url)
        if key in table:
            fail(f"{display_path(md_file)} repeats a source_url already used: {url}")
        table[key] = new_path(md_file)
    if len(table) != EXPECTED:
        fail(f"found {len(table)} pages with a source_url, expected {EXPECTED}.")
    return table


def php_string(value):
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def render(table):
    lines = [
        "<?php",
        "/*",
        " * Old aptrust.org TDR documentation URLs and where each now lives on",
        " * docs.aptrust.org. Loaded by aptrust_tdr_redirect() in functions.php.",
        " *",
        " * GENERATED FILE - do not edit by hand. Regenerate from the source_url front",
        " * matter in APTrust/tdr-docs with `python3 scripts/wp_redirects.py`.",
        " */",
        "",
        "return array(",
        f"\t'base'     => {php_string(NEW_BASE)},",
        "\t'prefixes' => array(",
        *[f"\t\t{php_string(p)}," for p in PREFIXES],
        "\t),",
        "\t'map'      => array(",
        *[f"\t\t{php_string(k)} => {php_string(v)}," for k, v in sorted(table.items())],
        "\t),",
        ");",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_OUT,
        help="where to write the PHP file (default: the theme's includes/tdr_redirects.php "
             "in a sibling aptrust-wordpress-theme checkout)",
    )
    args = parser.parse_args()

    if not args.out.parent.is_dir():
        fail(f"{args.out.parent} does not exist. Pass --out, or clone aptrust-wordpress-theme "
             "next to this repo.")
    table = build_map()
    args.out.write_text(render(table), encoding="utf-8")
    print(f"Wrote {len(table)} redirects to {display_path(args.out)}")


if __name__ == "__main__":
    main()
