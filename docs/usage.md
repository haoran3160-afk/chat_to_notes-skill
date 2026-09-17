# 安装与使用 / Installation and usage

## Requirements

- Python 3.10 or newer. The renderer has no third-party Python dependencies.
- PDF export: a local Chrome, Edge, or Chromium executable plus `requirements-pdf.txt`.
- Conversation retrieval: an agent with access to the target chat, or a transcript file. A GitHub clone alone cannot authenticate to private conversations.
- Optional desktop fallback: the host application's existing official connection and Node runtime. See [the reader reference](../skills/chat-to-notes/references/desktop-reader.md); this is an environment-specific fallback, not a universal API.

Use an isolated environment for PDF tools:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
python -m pip install -r requirements-pdf.txt
```

On Windows, use `.venv\Scripts\python.exe -m pip install -r requirements-pdf.txt` without activating the environment. Run later Python commands with the same interpreter. Existing environments with these libraries can be reused.

## Manual installation

Clone the repository:

```bash
git clone https://github.com/haoran3160-afk/chat_to_notes-skill.git
cd chat_to_notes-skill
```

Copy only `skills/chat-to-notes` into your configured Skill discovery directory. The following examples use `$CODEX_HOME/skills` or the conventional `.codex/skills` fallback. If your host uses another discovery directory, use that instead. Do not overwrite a customized installation silently.

Windows PowerShell:

```powershell
$notesRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$notesParent = Join-Path $notesRoot 'skills'
$notesTarget = Join-Path $notesParent 'chat-to-notes'
if (Test-Path -LiteralPath $notesTarget) { throw 'Existing installation: back it up and review the differences before updating.' }
New-Item -ItemType Directory -Path $notesParent -Force | Out-Null
Copy-Item -LiteralPath './skills/chat-to-notes' -Destination $notesTarget -Recurse
```

macOS / Linux:

```bash
notes_root="${CODEX_HOME:-$HOME/.codex}"
notes_target="$notes_root/skills/chat-to-notes"
if [ -e "$notes_target" ]; then
  printf '%s\n' 'Existing installation: back up and review it before updating.'
else
  mkdir -p "$notes_root/skills"
  cp -R skills/chat-to-notes "$notes_target"
fi
```

Reload the Skill list or start a new task if the current host has already cached discovery. A full copy is necessary: the scripts load templates and references by relative paths.

## Authoring and HTML

The model authors the explanation; `render_notes.py` assembles already-authored HTML. It does not call a model to rewrite a transcript.

```bash
python skills/chat-to-notes/scripts/render_notes.py \
  --body work/body.html --map work/map.html \
  --title "My study notes" --style electronic \
  --output outputs/notes.html
```

In PowerShell, write this command on one line or use PowerShell continuation syntax. `--style` is required. Supported values: `cornell`, `outline`, `annotated`, `sketch`, `handwritten`, `electronic`. Layout conventions are documented in [styles.md](../skills/chat-to-notes/references/styles.md).

Every h2/h3 needs a stable ID; internal links must resolve. Embed required images as data URLs or use inline SVG. Use static MathML for equations. Examples and formulas remain subject to source and semantic review.

## PDF export

First review the actual HTML. Once approved, calculate its SHA256 and export that exact version. The hash is an integrity check, not evidence that a human approved the content.

PowerShell:

```powershell
$notesHash = (Get-FileHash -LiteralPath 'outputs/notes.html' -Algorithm SHA256).Hash.ToLowerInvariant()
python skills/chat-to-notes/scripts/export_pdf.py outputs/notes.html --output outputs/notes.pdf --approved-sha256 $notesHash --work-dir work
```

macOS / Linux:

```bash
notes_hash="$(python -c 'import hashlib; from pathlib import Path; print(hashlib.sha256(Path("outputs/notes.html").read_bytes()).hexdigest())')"
python skills/chat-to-notes/scripts/export_pdf.py outputs/notes.html \
  --output outputs/notes.pdf --approved-sha256 "$notes_hash" --work-dir work
```

Use `--browser /path/to/chrome` if auto-detection cannot find your executable. The fixed style is read from the HTML; an optional `--style` must agree with it. Existing PDF files are not overwritten. Legacy two-style HTML requires its explicitly reviewed style.

Font changes, broken resources, missing bookmarks, or print overflow can block export. Repair the HTML and review the change; do not suppress the checks to obtain a PDF. Review the final PDF page by page. See [the full export contract](../skills/chat-to-notes/references/render-and-export.md).

## Reproduce previews

The public demo is a synthetic one-dimensional quadratic, unrelated to a user's course files or chats.

```bash
python examples/build_demo.py --style all --output-dir outputs/demo
```

With the PDF environment installed, render screenshots of those documents:

```bash
python examples/capture_previews.py --html-dir outputs/demo --output-dir outputs/previews
```

This also requires Pillow (`python -m pip install Pillow`) for the contact sheet. Pillow is a preview-development dependency, not part of note authoring or PDF export. `<style>.png` is a complete page; `<style>-detail.png` is the characteristic body excerpt. The two-column overview combines those excerpts with reading-method captions, omitting shared page headers and navigation. No preview-only typography or theme CSS is injected. The sample images in `docs/images/` are checked-in documentation assets; generated notes and PDFs stay ignored.

## Checks

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python -m unittest discover -s tests -p "browser_*.py" -v
```

The first command uses only the standard library. The second requires PDF dependencies and an installed browser; set `NOTES_BROWSER` to a browser executable if necessary. The CI workflow runs both suites separately.
