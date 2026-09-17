# Changelog

## Unreleased

### Documentation previews

- Make the six style examples demonstrate distinct reading structures around the same mathematical problem.
- Replace tiny full-document thumbnails with labeled body excerpts; retain links to complete screenshots and reproducible capture commands.

### Initial public repository

- Import the existing chat-to-notes Skill with six generation-time styles and fixed-style HTML/PDF output.
- Support current Codex context, accessible task/chat references, and transcript files; slides are optional.
- Preserve source coverage standards, worked examples, retrieval practice where appropriate, and no-appendix notes.
- Include hash-bound PDF export, embedded resource checks, native bookmarks, and internal link normalization.
- Add bilingual documentation, synthetic reproducible examples, tests, issue forms, and CI.

### Interface notes

- HTML generation requires an explicit `--style`.
- Fixed-style HTML determines PDF style; conflicting export flags are rejected.
- Legacy two-style HTML requires its explicitly reviewed style when exporting.
