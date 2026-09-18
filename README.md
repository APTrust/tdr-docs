# TDR Docs

APTrust's self-assessment against [ISO 16363](https://www.iso.org/standard/56510.html),
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

Filenames use a zero-padded hierarchical sequence (`04.02.04.01.01-…`) so that
alphabetical order matches ISO 16363 criterion order.

Every page carries front matter recording its `title`, the ISO criterion `number`, the
`sequence` used for ordering, its `section`, and the `source_url` and `retrieved` date
it was drawn from. Every page also carries a `description`, which becomes the page's
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
review round in Google Drive. See [scripts/README.md](scripts/README.md).

## Publishing

This repo is **not published yet**. It is intended to be folded into the unified APTrust
documentation site at [docs.aptrust.org](https://docs.aptrust.org/) alongside the User
Guide, DART, Registry and Preservation Services docs, which are combined by the
`aptrust-docs` repo using `mkdocs-monorepo-plugin`.

**Do not run `mkdocs gh-deploy`.** Publishing is the parent repo's job; deploying from
here would put a broken standalone copy of the site on a `gh-pages` branch.

### Registering with `aptrust-docs`

Until the steps below are done, a commit to `main` here publishes nothing. `aptrust-docs`
rebuilds on a push to itself, on a nightly 07:00 UTC schedule, or on a
`repository_dispatch` event of type `sub-repo-updated` — which only its four registered
sub-repos send. Adding this repo as a fifth:

1. Add `.github/workflows/notify-parent-docs.yml` here, modeled on the copy in
   `APTrust/registry-docs`: `peter-evans/repository-dispatch@v3`, event type
   `sub-repo-updated`, targeting `APTrust/aptrust-docs`. Note this repo's default branch
   is `main`, where the sibling repos use `master`.
2. Add a `DOCS_DISPATCH_TOKEN` secret to this repo — a token with permission to trigger
   workflows in `aptrust-docs`. The sub-repo workflow cannot fire the event without it.
3. In `aptrust-docs`, add `tdr-docs` to the checkout and merge steps of
   `.github/workflows/build-and-deploy.yml`.
4. In the parent `mkdocs.yml`, add this repo to the `nav:` via `mkdocs-monorepo-plugin`.
   `site_name: TDR Docs` makes the URL prefix `/tdr-docs/`, so changing it moves every page.

Once that is in place, a commit to `main` is live in three to five minutes, and the status
block in [CONTRIBUTING.md](CONTRIBUTING.md#what-happens-after-you-commit) should be deleted.

## License

Copyright © 2026 APTrust. The content in this repository is licensed under the
[Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/)
(CC BY-NC 4.0), matching the combined site at docs.aptrust.org. The full legal text is in [LICENSE](LICENSE).
