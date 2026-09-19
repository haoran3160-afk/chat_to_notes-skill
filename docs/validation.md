# Validation and limits / 验证范围

## What the repository tests

The standard-library suite checks all six render modes, source preservation, resource counts, file hashes, missing style selection, invalid layouts, broken anchors, external images, and unconverted math. Repository checks validate relative documentation links, label definitions, and the installable package boundary.

The browser suite renders the same synthetic example in all six styles. It checks fixed style selection, desktop versus narrow layouts, answer expansion/restoration, actual PDF generation, bookmarks, internal links, and rejection of hash/style conflicts. It also compares computed typography between handwritten and formal styles, so merely changing a title cannot pass as a style change.

Tests run locally and through the [Checks workflow](https://github.com/haoran3160-afk/chat_to_notes-skill/actions/workflows/checks.yml). Consult the run for the commit you use; a README badge is not evidence about future changes.

Static-content regressions reject SVG events, encoded executable links, active
metadata, SVG animation, unknown author attributes and ambiguous duplicate
attributes. Export preflight rejects active content even with a matching approval
hash. A real-browser regression deliberately bypasses author validation to verify
that the generated CSP blocks a before-print paragraph change while the trusted
answer-expansion script still works; actual PDF text must retain the original
paragraph. All six styles also preserve article text across print preparation.

## Evidence at initial publication

- Local execution: Windows, Python 3.12, Chrome 153, PyMuPDF 1.28.0, websocket-client 1.9.0.
- Public fixture: independently authored `f(x)=(x−2)²`, its derivative, a sampled parabola, a global-minimum argument, and a sign-reversal exercise.
- Six full-page HTML previews were captured from the actual renderer and visually inspected as a contact sheet. They use local fonts; no font files are redistributed.
- The browser tests exercise real export, rather than only comparing HTML strings.
- The initial authoring workflow was also exercised on private course material. That material and its transcripts are deliberately not shipped, so those earlier checks are not a public reproducibility claim.

The CI matrix includes Python 3.10/3.12 on Windows and Ubuntu for renderer checks, plus an Ubuntu browser/PDF job. An environment listed in a workflow is not a passing result until its run succeeds.

## Style showcase update

The public example now uses each style's intended structure: aligned recall rows, nested reasoning, per-step annotations, a graph linked to a proof path, continuous handwritten explanation, or a formal evidence table. The mathematical task and conclusion stay the same.

README thumbnails are labeled body excerpts cropped from the actual rendered HTML; full screenshots remain available. Cropping removes shared navigation rather than injecting alternate presentation CSS. The same renderer and browser/PDF suites also cover these richer examples.

## What is not proved

- That a model's explanation is complete or mathematically correct.
- That every platform's private chat can be read, or that cached context is a full transcript.
- That a smaller model matches a larger model's authoring quality.
- That typography is pixel-identical across machines or browsers.
- That PDF navigation behaves identically in all readers; Goodnotes device import has not been tested.
- That all long-document pagination cases are covered by the compact public example.

Content review and page-by-page visual inspection remain required for real deliverables. A valid anchor, formula count, hash, or bookmark does not establish semantic correctness.
