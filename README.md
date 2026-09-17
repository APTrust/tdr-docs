# TDR Docs

APTrust's self-assessment against [ISO 16363](https://www.iso.org/standard/56510.html),
the standard for audit and certification of trustworthy digital repositories.

The content is built with [MkDocs](https://www.mkdocs.org/) using the
[Material](https://squidfunk.github.io/mkdocs-material/) theme, the same setup used by
the other APTrust documentation repos.

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

## Publishing

This repo is not published yet. It is intended to be folded into the unified APTrust
documentation site at [docs.aptrust.org](https://docs.aptrust.org/) alongside the User
Guide, DART, Registry and Preservation Services docs.

**Do not run `mkdocs gh-deploy`.**
