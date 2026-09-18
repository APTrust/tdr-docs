# Review tooling

`docs_to_docx.py` converts the 120 Markdown pages in `docs/` into Word documents that can be
uploaded to Google Drive for a collaborative review round.

This folder is outside the documentation itself — nothing here is published to the site.

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

That writes five files into `review/`:

| File | Contents |
|---|---|
| `01-overview.docx` | The landing page and the Trusted Digital Repository overview |
| `02-oais.docx` | OAIS Documents — 7 pages |
| `03-tdr-3.docx` | TDR 3.0 Organizational Infrastructure — 26 pages |
| `04-tdr-4.docx` | TDR 4.0 Digital Object Management — 61 pages |
| `05-tdr-5.docx` | TDR 5.0 Infrastructure and Security Risk Management — 24 pages |

One file per section, so reviewers can take a section each and work in parallel. The number prefixes
make Google Drive sort them into the order of the standard. Each criterion starts on its own page,
and each document opens with a table of contents listing every criterion in it.

`review/` is ignored by git — the Word files are generated output and are never committed.

### Options

```bash
python3 scripts/docs_to_docx.py --section tdr-4     # one section only
python3 scripts/docs_to_docx.py --per-page          # one Word file per criterion
python3 scripts/docs_to_docx.py --out ~/Desktop     # write somewhere else
```

## The review workflow

1. **Generate the files** and check the stamp printed at the end — it records the date and the
   commit the review copy was made from. Each document repeats it under the title. If people keep
   editing the site during the review, that stamp is how you know what was reviewed.

2. **Upload `review/` to Google Drive.** Open each file in Google Docs — Drive converts it
   automatically.

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

Converting back automatically would rewrite all 120 files at once, and it would go wrong quietly:

- Every page begins with front matter — title, description, ISO number, source URL, retrieval date —
  that does not exist in the Word file and would have to be reattached to all 120 files.
- The 72 links between criteria and the exact spelling of the four canonical headings are both
  fragile under a round trip, and both are load-bearing: the first breaks the build, the second
  breaks nothing visibly and is only noticed later.
- A batch conversion produces a diff touching every file, which is precisely the kind of change
  nobody can meaningfully review.

Re-entering the accepted changes by hand is slower, and it cannot silently corrupt the site.
