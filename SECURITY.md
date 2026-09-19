# Security and privacy

Do not include private conversation exports, credentials, account identifiers, copyrighted course attachments, or local machine manifests in public reports. Use synthetic input to reproduce a problem.

For a vulnerability involving data exposure or unintended execution, use [GitHub private vulnerability reporting](https://github.com/haoran3160-afk/chat_to_notes-skill/security/advisories/new). Avoid publishing exploit details or sensitive data in a public Issue.

Only the current default branch is maintained. This project has no guaranteed response time or long-term support policy.

The HTML renderer expects authored content from an agent workflow. It is not a sandbox or general-purpose HTML sanitizer. Review untrusted input before passing it to a browser. The desktop reader only uses an existing official host connection; it does not grant new account access or read login tokens.

Author fragments use an explicit static HTML/SVG/MathML vocabulary. Unsupported
elements/attributes, event handlers, executable URLs and ambiguous duplicate
attributes are rejected rather than rewritten. Generated HTML includes a CSP
whose script hashes come only from the installed trusted template; author content
does not grant itself execution permission. The template's print-answer behavior
remains enabled. PDF preflight also rejects active attributes and any script other
than the known template or the JSON manifest, even when the approval hash matches.

These checks protect the author/template execution boundary, not the truth of
the notes or every possible visual deception. Content and page-by-page review
remain necessary. Older HTML containing custom runtime scripts must be rendered
and reviewed again; do not remove checks to make it export.
