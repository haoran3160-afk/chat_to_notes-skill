# Contributing

Thank you for helping improve chat-to-notes. Small, reproducible changes are easiest to review.

## Report a problem

Use the bug form and describe the expected behavior, actual behavior, selected style, Python version, browser version, and operating system. Provide a **synthetic or redacted** minimal example. Do not upload private chats, slide decks, local font files, credentials, or machine-specific manifests.

## Propose a change

Keep source retrieval, content authoring, and rendering responsibilities separate. Preserve the generation-time style choice, HTML review before formal PDF export, and disclosure of source gaps. Do not make mathematical correctness claims from mechanical checks.

Add dependencies only when their benefit is clear. Runtime dependencies belong in `requirements-pdf.txt`; optional authoring tools should not become mandatory for the standard-library renderer.

## Develop and verify

1. Fork or create a branch and make a focused change.
2. Run the commands in [Usage](docs/usage.md#checks).
3. For rendering changes, check all affected styles at desktop and narrow widths; inspect printed pages, formulas, images, answers, and navigation.
4. Update documentation and `CHANGELOG.md` when behavior changes.
5. Open a pull request with the problem, observable change, actual validation, and remaining limitations.

The authoring standards live in [learning-design.md](skills/chat-to-notes/references/learning-design.md). The tests exercise mechanical properties; a human still reviews explanation quality and visual output.

## Labels

General labels (`bug`, `enhancement`, `documentation`, `question`) describe the request. Area labels identify `sources`, `content`, `styles`, `math`, `pdf`, or `testing`. Maintainers may add `needs-reproduction`. Label definitions are versioned in [.github/labels.json](.github/labels.json).
