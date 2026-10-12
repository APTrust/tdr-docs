# TDR Docs

APTrust's self-assessment against [ISO 16363](https://www.iso.org/standard/87472.html),
the standard for audit and certification of trustworthy digital repositories.

The content is built with [MkDocs](https://www.mkdocs.org/) using the
[Material](https://squidfunk.github.io/mkdocs-material/) theme, the same setup used by
the other APTrust documentation repos.

**If you are here to edit the content, start with [CONTRIBUTING.md](CONTRIBUTING.md).** It
covers getting access, editing in the browser or in VS Code, and the accessibility rules
this content is held to. It assumes no prior experience with git or GitHub. The rest of
this file is a technical overview of how the repository is put together.

## Editing locally

You'll need Python 3.x and pip. To set it all up, run:

```
pip install -r requirements.txt
```

Then start the server with:

```
mkdocs serve
```

If you get a message saying mkdocs is not installed, try running the server with this
command instead:

```
python3 -m mkdocs serve
```

To check that everything still builds and that no internal links are broken:

```
mkdocs build --strict
```

## How the content is organized

Markdown lives under `docs/`, one folder per section of the standard:

| Folder | Contents |
|---|---|
| `docs/oais/` | OAIS conformance documents |
| `docs/tdr-3/` | TDR 3.0 Organizational Infrastructure |
| `docs/tdr-4/` | TDR 4.0 Digital Object Management |
| `docs/tdr-5/` | TDR 5.0 Infrastructure and Security Risk Management |
| `docs/img/` | Images |

The landing page and a short overview page sit directly in `docs/`.

Filenames use a zero-padded hierarchical sequence (`04.02.04.01.01-…`) so that
alphabetical order matches ISO 16363 criterion order.

Every page carries front matter recording its `title`, the ISO criterion `number`, the
`sequence` used for ordering, its `section`, and the `source_url` and `retrieved` date
it was drawn from. Most pages were drawn from aptrust.org. Seven were not, and have no
`source_url`: 4.1.1.3, 4.1.1.4, 4.2.3.2, 4.2.3.3, 4.3.5 and 5.1.1.7 were added in the 2024
edition of the standard, and 5.1.1.1.1 had no page on aptrust.org. Those pages carry the
standard's text, with the evidence still to be written by the APTrust Certification
Working Group. Every page also carries a `description`, which becomes the page's
`<meta name="description">` tag — use the folded-with-strip form when adding a page:

```yaml
---
description: >-
  One or two wrapped lines, 50-160 characters total.
---
```

The navigation sidebar is defined explicitly in `mkdocs.yml`. Page titles are often long
ISO criterion statements, so `nav:` carries a shortened label for each page while the
full title stays as the page's heading. Adding a page means adding it to `nav:`.

## Accessibility

Content here is written to meet WCAG 2.2 level AA: images carry descriptive alt text,
heading levels are sequential, tables have real header rows, and link text describes its
destination rather than saying "here" or repeating a bare URL. Please keep to that when
editing.

## Reviewing content in Word

`scripts/docs_to_docx.py` converts the pages into Word documents for a collaborative
review round in Google Drive:

```
python3 scripts/docs_to_docx.py
```

It writes into `review/`, which git ignores:

- **One folder per section** — `01-overview/`, `02-oais/`, `03-tdr-3/`, `04-tdr-4/`,
  `05-tdr-5/`.
- **One Word file per three-number criterion**, such as 4.1.1 or 4.2.4. A criterion with
  sub-criteria is written as a single file named `Combined`, for example
  `4.1.1 Combined - Content information and information properties.docx`, holding 4.1.1
  and everything beneath it. Each section's landing page becomes `4.0 Overview.docx` and
  so on.
- **A tracking spreadsheet**, `TDR Review <year> Tracking.xlsx`, with one row per page and
  the Word file it landed in, plus empty columns for status, review dates, whether the
  change has been applied back to the Markdown, and notes.

The script needs Python and [pandoc](https://pandoc.org/installing.html), nothing else.
Review happens in Google Drive, and accepted changes are applied back to the Markdown by
hand. The full workflow, the options, and the reason there is no Word-to-Markdown
conversion are in [scripts/README.md](scripts/README.md).

## Publishing

This repo is published as the **TDR** tab of the unified APTrust documentation site, at
<https://docs.aptrust.org/tdr/>, alongside the User Guide, DART, Registry and Preservation
Services docs. The `aptrust-docs` repo combines them using `mkdocs-monorepo-plugin`.

**Do not run `mkdocs gh-deploy`.** Publishing is the parent repo's job; deploying from
here would put a broken standalone copy of the site on a `gh-pages` branch.

### How a commit reaches the site

A push to `main` runs `.github/workflows/notify-parent-docs.yml`, which sends a
`repository_dispatch` event of type `sub-repo-updated` to `APTrust/aptrust-docs`. That repo
clones all five sub-repos, rebuilds, and deploys. A commit is normally live in three to five
minutes.

The dispatch needs the `DOCS_DISPATCH_TOKEN` Actions secret on this repo: the fine-grained
PAT owned by the `aptdeploy` service account, with **Contents: Read and write** on
`APTrust/aptrust-docs`. It expires after 366 days and is shared with the other sub-repos, so
it is rotated in all of them together — see *Automatic deploys* in the `aptrust-docs` README.
If the token is missing or expired, the *Notify Parent Docs Repo* run turns red but nothing
breaks: the parent's nightly 07:00 UTC build picks the content up within 24 hours.

### What lives in `aptrust-docs`

- The `- TDR: '!include ./repos/tdr/mkdocs.yml'` entry in the parent `nav:`. The tab label
  readers see comes from there.
- The `git clone` line for this repo in `.github/workflows/build-and-deploy.yml`.
- The "TDR" search-result badge in `docs/stylesheets/extra.css`, keyed on the `/tdr/` prefix.

The `/tdr/` URL prefix comes from `site_name: tdr` in this repo's `mkdocs.yml`. Changing it
moves every page and orphans the search badge.

### Still to do

Capture the two screenshots still missing from [CONTRIBUTING.md](CONTRIBUTING.md), which
need real build runs to exist: `actions-01-status.png` (the Actions tab listing runs, ideally
with both a green check and a red X) and `actions-02-failed-step.png` (a failed run opened to
the step that names the file at fault). Save them in `contributing-img/` and add them under
*What happens after you commit* and *If you see a red X*.

## License

Copyright © 2026 APTrust. The content in this repository is licensed under the
[Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/)
(CC BY-NC 4.0), matching the combined site at docs.aptrust.org. The full legal text is in [LICENSE](LICENSE).
[test](no-such-page)
