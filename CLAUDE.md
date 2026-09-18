# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

APTrust's self-assessment against ISO 16363 (audit and certification of trustworthy digital
repositories), as an MkDocs site. 120 markdown pages under `docs/`, one per criterion, scraped
from aptrust.org and then restructured.

**This is a content-source repo, not a standalone site.** It is shaped to match the four sibling
APTrust docs repos (`userguide`, `registry-docs`, `preserv-docs`, `dart-docs`), which are combined
into <https://docs.aptrust.org> by the `aptrust-docs` repo using `mkdocs-monorepo-plugin`. That
plugin reads only `nav:` and `docs_dir` from a child's `mkdocs.yml` — all theming, palette, CSS and
WCAG overrides live in the parent.

This has consequences that look like omissions but are deliberate:

- `theme: material` is a bare scalar. **Do not add a `theme:` block, palette, or `overrides/`** —
  the parent supplies them and ignores anything here.
- **Do not add a `plugins:` block.** Declaring one overrides MkDocs' implicit `['search']` and
  silently kills the search box (this is what happened to `userguide`). The parent ignores a
  child's plugins anyway, so any plugin needed here must also be declared in the parent against
  the merged tree.
- No `site_url`, no `site_description`. Page descriptions come only from per-page front matter.

`site_name: TDR Docs` becomes the URL prefix on the unified site (`/tdr-docs/`), so changing it
moves every page.

The repo is local-only — no git remote, no CI. Registering it with `aptrust-docs` is a future step.

## Commands

```bash
.venv/bin/python -m mkdocs serve          # preview at http://127.0.0.1:8000
.venv/bin/python -m mkdocs build --strict # build; fails on broken links or nav orphans
```

`mkdocs` is not on PATH — it lives in `.venv` (gitignored). Recreate with
`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

**Always build with `--strict`.** It is the only automated check that internal links resolve and
that every page is in the nav. (The parent repo omits `--strict` only because `dart-docs`' nav is
broken; that is not a reason to drop it here.)

`.claude/launch.json` defines a `tdr-docs` preview server on port 8124.

## Layout

```
docs/
  index.md                       landing page
  trusted-digital-repository.md  overview (sequence 01)
  oais/  tdr-3/  tdr-4/  tdr-5/  one folder per section; <folder>/index.md is its landing page
  img/                           all images, referenced as ../img/<name>
```

One level of nesting, **flat within each section**. Filenames keep a zero-padded sequence prefix
(`04.02.04.01.02-slug.md`) so alphabetical order matches ISO criterion order.

Internal links are relative `.md` links — bare filenames within a section, `../<folder>/<file>.md`
across sections. Moving a file between folders breaks every link to it; run `--strict` after.

## Page conventions

```yaml
---
title: "4.4.2.1 AIP procedures"
description: >-
  The repository shall have procedures for all actions taken on AIPs.
number: "4.4.2.1"        # ISO criterion number; absent on section landings
sequence: "04.04.02.01"  # drives ordering and nav nesting
section: "TDR 4.0 Digital Object Management"
source_url: https://aptrust.org/documentation-page/...  # provenance; do not rewrite
retrieved: 2026-09-17
---
```

`description` is required on every page — it becomes the `<meta name="description">` tag. Use
`>-` (folded **with** the strip indicator); a bare `>` leaves a trailing newline inside the
`content="…"` attribute. Target 50–160 characters, usually the requirement sentence.

Body structure after the H1 is: an unlabelled requirement paragraph (or `## Requirement Text`),
then `## Supporting Text`, `## Examples for Meeting the Requirement`, `## Discussion`,
`## Evidence Provided`. Those four headings have exact canonical spellings — casing variants were
normalized and should not creep back in.

## Nav

`nav:` in `mkdocs.yml` is explicit and hand-written; there is no awesome-pages or literate-nav.
Three things to know:

- **Labels are short and hand-authored.** 61 criterion titles run over 55 characters (the longest
  is 189) and would wrap the sidebar to six lines. The full title stays as the page H1; the nav
  carries a trimmed label keeping the leading ISO number. An explicit nav label wins over
  front-matter `title:`.
- **13 ISO subsections have no page of their own** (3.1–3.5, 4.1–4.6, 5.1–5.2). They appear as
  title-only group nodes. A criterion page that also has child sub-criteria is the overarching
  requirement itself — not a summary — and carries its own evidence, so it is listed as the
  group's own first child, repeating that label: `- 4.2.4 Persistent unique identifiers for
  AIPs:` as the group, then `- 4.2.4 Persistent unique identifiers for AIPs: <path>` beneath it.
  Only the four section landing pages (`oais/index.md`, `tdr-3/index.md`, `tdr-4/index.md`,
  `tdr-5/index.md`) are true overviews — no `number:`, no requirement text — and keep the
  `- Overview: <path>` label.
- **Quote any label containing a colon**, e.g. `- "4.1 Ingest: Acquisition of Content":` —
  otherwise YAML fails to parse.

## External links

- **`aptrust.org` links stay absolute.** That content lives on WordPress and is out of scope.
- **Never use `aptrust.github.io`.** Those sites are redirect stubs or dead; everything points at
  `docs.aptrust.org` (`/user-guide/`, `/registry-docs/`, `/preservation-services-docs/`,
  `/dart-docs/`, `/api/`). Note `userguide/bagging/` was renamed `depositing/`.
- Policy links use the `aptrust.org/resources/policies/` base with a section anchor; documents that
  also have an `/about/<name>/` page use that form consistently.
- Links to member- or staff-restricted resources carry an inline marker so a reader knows why the
  link will not open:
  `(APTrust members only; supplied to auditors on request)`

## Accessibility

Content is written to WCAG 2.2 AA; the parent site is externally audited against it. UI concerns
(focus order, nav semantics, contrast, external-link handling) belong to `aptrust-docs`, not here.
What this repo owns: descriptive alt text on every image, sequential heading levels with no skips,
tables with real header rows, link text that describes its destination rather than saying "here" or
repeating a bare URL, and no meaning carried by a symbol alone (check and cross glyphs are paired
with Yes/No).
