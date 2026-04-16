---
audience: [agents, humans]
version: 1
---

# Style guide

These rules apply to documentation and other prose in this project.

## Verb tense

- Prefer **present tense** when describing how the product or tooling behaves today.
- Avoid **future tense** for ordinary procedures. Use future tense only when the text is about a future release, a scheduled action, or clearly hypothetical behavior.
- Do not include **forward-looking** placeholder content (for example outlines of planned topics, “intended sections,” or “coming soon” lists). Write what is true today or omit the topic until it is ready.

## Voice

- Prefer **active voice** so the reader sees who acts.
- Use **passive voice** only when the actor does not matter or when passive is standard for the domain.

## Addressing the reader

- Use **“you”** for procedures and guidance.
- Avoid **“the user”**, **customers**, etc. when you mean the reader.

## Terminology

- Use **one term per concept** across the docs.
- Match **product names**, spelling, and capitalization to the product and branding.
- Prefer **topic** over **page** when you mean a subject or section of the documentation (not a literal browser or printed page).

## Capitalization

- Use **sentence case** for headings unless your product defines title case.
- Define how to treat **product names** and proper nouns and stay consistent.

## Lists

- Use **parallel structure** in each list (all start the same way, same grammar).
- Punctuate lists consistently. Use either **fragments** without a final period or **full sentences** with periods.
- Keep **pipe tables** (GitHub-style `| … |` tables) **out of nested list bodies**. A table indented under a numbered step is often parsed as plain text so pipes show literally. End the list (or close the step with only a code fence), then put the table at **section level** with no leading indentation.

## Tables

- Use **tables** for real tabular data, not for layout.
- Follow the rule above when combining tables with procedures so the site converter renders them as HTML tables.

## Procedures

- Introduce a **numbered procedure** with a short **lead-in sentence** in the form **To** *verb clause* (for example *To install…*, *To configure…*). The verb clause states what the reader will do and any important context (for example the tool or product). End that sentence with a **colon**, then start the numbered steps on the next line.
- Example: *To install the **AWS Command Line Interface (AWS CLI)** with Homebrew:*

## Code and UI

- Use **monospace** for commands, paths, and literals.
- Treat **real paths** (for example repository-relative paths the reader must open, copy, or `cd` into) as **code examples** when they are the main focus of a step. Put them in a **fenced code block** instead of burying them only in prose.
- For those path examples, use a **` ```text `** fence when the block is a path (or tree fragment) by itself. Use a **` ```bash `** fence when the path appears inside a runnable shell command.
- Use **inline monospace** for short path fragments inside a sentence when a fence would read awkwardly.
- Use **bold** for UI labels when you describe what to click.
- Do not invent menu paths or labels that do not exist in the product.

## Links

- Prefer **callout links** at the end of a sentence or paragraph: “See [link text](url) for more information” or “See [link text](url) for more information on *topic*.”
- Use an **inline link** in the middle of a sentence when that reads more naturally than a callout.
- Do not use generic phrases such as “click here” as the only link text.
- Keep links accurate when you maintain the page.

## Numbers and units

- Pick **digits or spelled-out numbers** for small counts and stay consistent.
- Write **units** clearly (for example `10 MB`).

## Abbreviations

- Spell out **abbreviations on first use** in a page unless the audience always knows them.
- Give the short form in parentheses after the first use when you need both.

## Accessibility

- Add **alt text** for images that carry meaning. Use empty alt for purely decorative images when your format allows it.

## Punctuation

- Do **not** use the semicolon (`;`). Split the thought into two sentences or use a colon, dash, or list instead.
