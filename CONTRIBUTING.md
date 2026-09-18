# How to edit these pages

This repository holds APTrust's self-assessment against ISO 16363, the standard for audit and
certification of trustworthy digital repositories. There are 120 pages here, one per criterion,
written in Markdown. They are published as part of the combined APTrust documentation site at
[docs.aptrust.org](https://docs.aptrust.org/).

This guide is for the people who maintain that content. It assumes you have never used GitHub
before. You do not need to know git to make a change.

## Getting access

You need **Write** access to this repository. Read access is not enough to save a change, and you
should not be given Admin.

Ask an APTrust staff member who administers the `APTrust` GitHub organization. What they will do:

1. Go to the repository on GitHub and open **Settings**.
2. In the left sidebar, choose **Collaborators and teams**.
3. Select **Add people**, enter your GitHub username or email, and choose the **Write** role.

You will get an email invitation. **You have to accept it before you can edit anything** — the
invitation expires after seven days. If you do not have a GitHub account yet, create a free one at
[github.com](https://github.com/) first, and give that username to whoever is granting your access.

## Which way should you edit?

There are two ways to work, and the right one depends on what you are changing.

| What you are doing | Use |
|---|---|
| Fixing a typo, rewording a sentence, updating a link | **GitHub in your browser** |
| Adding or removing a page, moving pages, editing `mkdocs.yml` | **VS Code on your computer** |
| Anything you want to *see* rendered before it goes live | **VS Code on your computer** |
| Editing several pages at once | Either — use the browser editor's `.` shortcut, below |

The browser is faster. VS Code is the safer choice for bigger changes, because it is the only way
to preview the site before your change is published.

## Option A — edit in your browser

Best for small, self-contained text changes.

1. Navigate to the page you want to change, in the `docs/` folder of this repository.
2. Click the **pencil icon** in the upper right of the file view.
3. Make your change.
4. Click **Commit changes…**.
5. Write a commit message describing your change — see
   [Writing a commit message](#writing-a-commit-message) below.
6. Leave **Commit directly to the `main` branch** selected, and click **Commit changes**.

That is the whole process. Your change is saved.

### Editing several files at once

From anywhere in the repository on github.com, press the **`.`** key. This opens github.dev, a full
editor in your browser with the file tree on the left. Edit as many files as you like, then use the
Source Control panel on the left (the branching-arrows icon) to enter a message and click
**Commit & Push**.

github.dev cannot preview the rendered site — it only edits text. For that, use VS Code.

## Option B — edit in VS Code on your computer

Best for larger changes, and the only way to preview your work before it is published.

### One-time setup

Install these three things:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Python](https://www.python.org/downloads/) 3.9 or newer
- [Git](https://git-scm.com/downloads) — macOS usually has it already

Then get a copy of the repository:

1. Open VS Code.
2. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows) and type **Git: Clone**.
3. Paste `https://github.com/APTrust/tdr-docs` and choose a folder to put it in.
4. VS Code will offer to sign you in to GitHub — accept, and it handles the login for you.
5. When it asks whether to open the cloned repository, say yes.

Now set up the preview tools. Open VS Code's built-in terminal with **Terminal → New Terminal**, and
run these, one at a time.

On macOS:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

On Windows:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

You only do this once.

### Each time you edit

1. **Get the latest changes first.** Click the **sync icon** (circular arrows) in VS Code's blue
   status bar at the bottom. This pulls in anything other people have changed. Do this before you
   start, every time — it avoids conflicts.

2. **Start the preview.** In the terminal:

   ```bash
   .venv/bin/python -m mkdocs serve
   ```

   On Windows, use `.venv\Scripts\python -m mkdocs serve`.

   Open <http://127.0.0.1:8000> in your browser. The preview reloads automatically every time you
   save a file. Leave it running while you work.

3. **Make your changes** in the editor.

4. **Check that nothing is broken.** Stop the preview with `Ctrl+C`, then run:

   ```bash
   .venv/bin/python -m mkdocs build --strict
   ```

   This checks that every internal link points at a real page and that every page appears in the
   navigation. If it prints errors, fix them before you save your work — this is the same check
   that runs on GitHub after you push.

5. **Save your work to GitHub.** In the Source Control panel (the branching-arrows icon in the left
   sidebar):
   - Your changed files are listed. Hover over each and click **+** to stage it.
   - Type your commit message in the box at the top.
   - Click **Commit**, then **Sync Changes** to send it to GitHub.

   You never need to type a git command.

## Writing a commit message

We commit directly to `main` rather than opening pull requests. That keeps things simple, but it
means **the commit message is the only record of why a change was made**. For an audit document,
that record matters — treat it as part of the work.

Write a short summary line saying what changed, and if the reason is not obvious, add a blank line
and a sentence or two explaining why.

Good examples from this repository's history:

```
Fix dead OAIS Reference Model links

The public.ccsds.org PDF links no longer resolve; point at the ISO
standard page and the DOI instead.
```

```
Point the dead Risk Management link at the threats-and-mitigations page
```

Avoid messages like `update`, `fix`, `changes`, or `asdf`. In six months, someone preparing for an
audit will be reading these.

## What happens after you commit

> **Status: not yet connected.** This repository is not registered with the combined documentation
> site yet, so nothing is published at docs.aptrust.org today — your commits are saved safely on
> GitHub and nothing else happens. The rest of this section describes how it will work once
> registration is complete. See the *Publishing* section of [README.md](README.md) for what that
> involves.

When you commit to `main`, a rebuild of the combined documentation site starts automatically. Your
change is normally live at [docs.aptrust.org](https://docs.aptrust.org/) within **3 to 5 minutes**.
There is nothing else you need to do — no separate publish step, no button to press.

To watch it happen, open the **Actions** tab at the top of this repository. A yellow dot means a
build is running, a green check means it finished, and a red X means something went wrong.

### If you see a red X

A build check runs on every commit and tries to build the site exactly the way the live site does.
If it fails, GitHub emails you. A red X almost always means one of two things:

- **A broken link** — you linked to a page that does not exist, or you renamed a file and something
  else still points at its old name.
- **A page missing from the navigation** — you added a page but did not add it to `nav:` in
  `mkdocs.yml`.

Click the red X, then the failed step, to see which file and line caused it. Then fix it and commit
again. There is nothing to undo or roll back — **everything here is fixed by editing forward**.
Nothing you can do in this repository is hard to reverse.

## Before you save — a checklist

The full conventions are in [README.md](README.md). The things most easily got wrong:

- **Every page needs a `description:`** in its front matter. It becomes the page's search-result
  summary. Use the folded-with-strip form — `>-`, not `>` — and aim for 50 to 160 characters.
- **Use the four canonical headings**, spelled exactly like this: `## Supporting Text`,
  `## Examples for Meeting the Requirement`, `## Discussion`, `## Evidence Provided`.
- **Links between pages are relative Markdown links** to the `.md` file — a bare filename within the
  same folder, or `../folder/file.md` across folders.
- **A new page must be added to `nav:`** in `mkdocs.yml`, or the build fails.
- **Never run `mkdocs gh-deploy`.** You will see it in the MkDocs documentation. It does not apply
  here and would publish a broken copy of the site. Publishing is handled for you.

## Keeping it accessible

These pages are written to meet **WCAG 2.2 Level AA**, and the published site is audited against it
by an external reviewer. The way you write Markdown affects whether the site passes, so a few habits
matter.

**Not your concern:** color contrast, keyboard navigation, focus order, and how external links are
marked are all controlled by the site's theme, which lives in the `aptrust-docs` repository and is
audited there. You do not need to think about them here.

**What this repository is responsible for:**

- **Give every image descriptive alt text** (WCAG 1.1.1). The text in the square brackets is what
  someone using a screen reader hears instead of the image. Describe what the image *tells the
  reader* — a bare filename or the word "screenshot" on its own tells them nothing.

  ```markdown
  Not this:  ![screenshot](../img/ObjectDetailTop.png)
  This:      ![The APTrust Registry Object Details page for a deposited item.](../img/ObjectDetailTop.png)
  ```

  Do not open with "An image of" — a screen reader already announces that it is an image, so those
  words are read out twice. Opening with "Screenshot of" is fine when it matters to the reader that
  they are looking at a captured screen rather than a diagram, as it does on the evidence pages.

  If the description needs more than a sentence or two — as several evidence screenshots here do —
  put that detail in the body text where every reader benefits, and keep the alt text shorter.

- **Never skip heading levels** (WCAG 1.3.1, 2.4.6). Go `#` → `##` → `###` in order. Each page has
  exactly one `#`, its title. Do not jump from `##` to `####` because you prefer the smaller text.

- **Do not use bold text as a heading.** People using screen readers navigate a page by jumping from
  heading to heading, and a bold line is invisible to that.

  ```markdown
  Not this:  **Evidence Provided**
  This:      ## Evidence Provided
  ```

- **Write link text that describes where it goes** (WCAG 2.4.4). Not "here", "this page", or "click
  here" — and never paste a bare URL as the link text, because a screen reader reads it out one
  character at a time. Screen readers can also list every link on a page on its own, so the text has
  to make sense with no sentence around it.

  ```markdown
  Not this:  The policy is available [here](https://aptrust.org/resources/policies/).
  This:      See the [APTrust preservation policies](https://aptrust.org/resources/policies/).
  ```

  If a link goes somewhere the reader cannot open, say so in the sentence, the way existing pages do:
  `(APTrust members only; supplied to auditors on request)`. If it goes to a PDF, say that too.

- **Give tables a real header row** (WCAG 1.3.1). The `| --- |` line under the first row is what
  turns it into a header. Without it, the table is just a grid of unlabelled cells. Keep tables
  simple — one header row, no merged cells, and never use a table to lay out a page.

- **Never let a symbol or a color carry meaning by itself** (WCAG 1.4.1). A ✅ on its own is not
  read as "yes". Pair it with a word, the way the tables in `docs/tdr-5/` already do — `✅ Yes` and
  `❌ No`. For the same reason, do not write "the rows highlighted in red".

- **Use real list and quote syntax** (WCAG 1.3.1). Start list items with `-` or `1.` so that a
  screen reader announces "list, 6 items" instead of reading a run-on paragraph. Mark quoted
  material with `>` rather than only wrapping it in quotation marks — several evidence pages quote
  AWS documentation and console output, and those are easier to follow when marked up as quotations.

- **Avoid raw HTML for visual effect.** No `<br>` to force spacing, no `<font>`. It bypasses the
  theme's styling and often the semantics with it.

- **Expand an acronym the first time you use it** on a page — AIP, SIP, DIP, PDI, OAIS. This one is
  good practice for an audit document rather than a strict AA requirement, but auditors reading a
  single criterion page out of context will thank you.

## Reviewing the content in Word or Google Docs

For a full review round — where several people read and comment on the content together — there is a
script that converts these pages into Word documents you can upload to Google Drive. See
[scripts/README.md](scripts/README.md).

## Getting help

- Something about the content or the standard: ask on the Certies list.
- Something about GitHub, the build, or an error you do not recognize: ask APTrust staff. Include a
  link to the commit or the failed build — that is usually enough to diagnose it.
