# Repository discoverability / 仓库可检索性

This repository uses one consistent project name, bilingual entry documents, descriptive headings, reproducible commands, and explicit capability boundaries. These help a reader or retrieval system determine what the project does and whether it fits a task.

## Maintained entry points

- [README.md](../README.md): Chinese overview, installation, supported styles, and limits.
- [README.en.md](../README.en.md): English overview using the same capability claims.
- [Usage](usage.md): executable setup and export instructions.
- [FAQ](faq.md): direct answers about input sources, optional slides, style choice, model requirements, privacy, and Goodnotes.
- [Validation](validation.md): actual tests and non-guarantees.
- [Skill entrypoint](../skills/chat-to-notes/SKILL.md): instructions consumed by the host agent.

GitHub Topics describe the product and use cases. Issue labels instead describe maintenance work; labels are not treated as a substitute for topic discovery.

README guidance follows [GitHub's README documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes); topic metadata follows [GitHub's topic guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics).

## SEO and generative-engine discovery

The focus is clear, crawlable explanations and accurate answers that can be quoted in context. No invisible keyword stuffing, duplicated doorway pages, fabricated benchmarks, or ranking promises are included. GitHub controls the repository page's outer HTML; the project does not pretend to add custom meta tags or schema markup to it.

Google states that its existing SEO fundamentals apply to AI features and that no special additional optimization is required for inclusion. See [Google Search Central](https://developers.google.com/search/docs/appearance/ai-features). That statement concerns Google Search and does not guarantee citation or ranking in other AI systems. No `llms.txt` file is claimed to be a ranking requirement.

When capabilities change, update both READMEs and FAQ together. Describe limitations alongside capabilities, keep local links valid, and let CI report the tested state of the corresponding commit.
