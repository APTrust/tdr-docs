# Scripts

Two scripts live here, outside the documentation itself — nothing in this folder is published
to the site:

- `docs_to_docx.py` — Word files for review rounds, described first below.
- `wp_redirects.py` — the aptrust.org redirect table, described at the end under
  [Redirects from aptrust.org](#redirects-from-aptrustorg).

# Review tooling

`docs_to_docx.py` converts the 127 Markdown pages in `docs/` into Word documents that can be
uploaded to Google Drive for a collaborative review round, along with a spreadsheet for tracking
the review's progress.

## What you need

**Python 3.9 or newer**, which macOS already has, and **pandoc**, which does the conversion:

- macOS: `brew install pandoc`
- Windows: [download the installer](https://pandoc.org/installing.html)

The script itself needs nothing installed — no `pip install`, no virtual environment.

## Running it

From the top level of the repository:

```bash
python3 scripts/docs_to_docx.py
```

That writes 62 Word files into `review/`, in one folder per section, and a tracking spreadsheet
beside them:

| Folder | Contents |
|---|---|
| `01-overview/` | 1 file — the landing page and the Trusted Digital Repository overview |
| `02-oais/` | 7 files — OAIS Documents, one per page |
| `03-tdr-3/` | 16 files — TDR 3.0 Organizational Infrastructure |
| `04-tdr-4/` | 31 files — TDR 4.0 Digital Object Management |
| `05-tdr-5/` | 7 files — TDR 5.0 Infrastructure and Security Risk Management |

Within a TDR folder there is one file per three-number criterion, so reviewers can take a criterion
each and work in parallel:

| File | Contents |
|---|---|
| `4.0 Overview.docx` | The section's landing page |
| `4.1.1 Combined - Content information and information properties.docx` | 4.1.1 and its sub-criteria 4.1.1.1 to 4.1.1.4 |
| `4.1.3 Recognition and parsing of SIPs.docx` | 4.1.3 alone — it has no sub-criteria |

A file named `Combined` holds a criterion together with everything beneath it, however deep
(4.2.4 brings 4.2.4.1, 4.2.4.1.1 and so on). Each criterion in it starts on its own page, and the
document opens with a table of contents. A `/` in a criterion's title becomes `-` in the file name.

The number prefixes on the folders make Google Drive sort them into the order of the standard.

### The tracking spreadsheet

`review/TDR Review 2026 Tracking.xlsx` (the year is the year you run the script) lists every page,
grouped under a band for each section, with these columns:

| Column | What goes in it |
|---|---|
| Status | Filled in during the review |
| Section Title | The page's title, led by its criterion number — filled in by the script |
| 1st Review Date | Filled in during the review |
| Group Review Date | Filled in during the review |
| Applied to Markdown | Filled in once the accepted changes are back in `docs/` |
| Document | The Word file the page is in — filled in by the script |
| Notes | Filled in during the review |

A sub-criterion that shares a `Combined` file shows `"` in the Document column, meaning "same
document as the row above".

The spreadsheet always lists every section, even when `--section` converts only one. Running the
script again writes a fresh, empty one over the copy in `review/` — so keep the working copy in
Google Drive, not here.

`review/` is ignored by git — the Word files are generated output and are never committed.

### Options

```bash
python3 scripts/docs_to_docx.py --section tdr-4     # one section only
python3 scripts/docs_to_docx.py --per-page          # one Word file per page, sub-criteria split out
python3 scripts/docs_to_docx.py --out ~/Desktop     # write somewhere else
```

## The review workflow

1. **Generate the files** and check the stamp printed at the end — it records the date and the
   commit the review copy was made from. Each document repeats it under the title. If people keep
   editing the site during the review, that stamp is how you know what was reviewed.

2. **Upload the folders and the tracking spreadsheet in `review/` to Google Drive.** Open each
   file in Google Docs or Google Sheets — Drive converts it automatically.

3. **Ask reviewers to use comments and suggestions**, not silent edits. In Google Docs that means
   the **Suggesting** mode (the pencil menu, top right) and the comment button. A tracked suggestion
   is far easier to act on than a changed paragraph nobody noticed.

4. **Apply the accepted changes back to the Markdown by hand.** Under every criterion's heading the
   document carries a line like:

   > *Source: [docs/tdr-5/05.01.01.01-employ-technology-watches.md](https://github.com/APTrust/tdr-docs/blob/main/docs/tdr-5/05.01.01.01-employ-technology-watches.md)*

   That is a live link to the page on GitHub — click it to go straight to the file, then use the
   pencil icon to edit it in your browser. Follow the conventions in
   [CONTRIBUTING.md](../CONTRIBUTING.md).

   The links point at the current version of each page on the `main` branch, not at the commit the
   review copy was made from, so they always open the version your change has to be applied to.

5. **Check the build, then commit:**

   ```bash
   .venv/bin/python -m mkdocs build --strict
   ```

   Reference the review round in your commit messages so the change has a traceable reason —
   for example, `Clarify AIP identifier convention per Certies review 2026-09`.

## Two things reviewers should be told

- **Cross-references look broken, and they are not.** Links between criteria appear in Word as links
  to `.md` files and will not open. They are correct in the source and work on the live site. Ignore
  them.
- **Do not reformat.** Headings, tables and lists carry meaning in the published site. Comment on
  wording and substance, not on how the Word file looks.

## Why there is no Word-to-Markdown script

Converting back automatically would rewrite all 127 files at once, and it would go wrong quietly:

- Every page begins with front matter — title, description, ISO number, source URL, retrieval date —
  that does not exist in the Word file and would have to be reattached to all 127 files.
- The 72 links between criteria and the exact spelling of the four canonical headings are both
  fragile under a round trip, and both are load-bearing: the first breaks the build, the second
  breaks nothing visibly and is only noticed later.
- A batch conversion produces a diff touching every file, which is precisely the kind of change
  nobody can meaningfully review.

Re-entering the accepted changes by hand is slower, and it cannot silently corrupt the site.

# Redirects from aptrust.org

The 119 pages that came from WordPress are still published at
`aptrust.org/documentation-page/…`. The aptrust.org theme sends each of those URLs to its page here
with a permanent (301) redirect, using a lookup table generated from the `source_url` front matter:

```bash
python3 scripts/wp_redirects.py
```

It writes `wp-content/themes/aptrust/includes/tdr_redirects.php` in a checkout of the
`aptrust-wordpress-theme` repo sitting next to this one (`--out` to put it elsewhere). It stops
without writing anything if a `source_url` is repeated, points outside the five TDR slugs on
aptrust.org, or the count is not 119.

**Re-run it whenever a page in `docs/` is renamed or moved to another folder**, then commit the
regenerated file in the theme repo and upload it to WP Engine. Otherwise the old aptrust.org URL
keeps redirecting to the page's previous address, which is now a 404. Edits to a page's content
need nothing.

The redirect code itself is `aptrust_tdr_redirect()` in the theme's `functions.php`. It matches on
the URL, not on the WordPress post, so it keeps working after the old posts are deleted.
