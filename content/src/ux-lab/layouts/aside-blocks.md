# Aside blocks (admonitions)

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

Real documentation systems often render **notes**, **cautions**, and **warnings** as aside elements. This page uses the doc-infra `::: kind` … `:::` directives (`caution`, `warning`, `note`) so you can preview spacing, titles, and hierarchy in the built site.

::: note
In a production pipeline, this paragraph might live inside a bordered component with an icon. For now, the admonition chrome comes from CSS. Check that the title and body do not sit too close to neighboring paragraphs when the sidebar is hidden and the main column expands.
:::

::: caution
Keep titles short. Readers scan headings first; long headings wrap awkwardly on mobile and compete with navigation labels. When in doubt, split content into two headings rather than one heading with a subordinate clause that stretches across the entire line.
:::

::: warning
Destructive operations should always require confirmation. If your UX uses modals, ensure keyboard focus moves predictably and that documentation pages do not trap focus when embedded in iframes elsewhere. This warning is intentionally verbose so you can see how multiple sentences behave when they are visually grouped with a label.
:::

## Returning to normal body text

After admonitions, ordinary paragraphs should feel calmer. The transition matters: add a line of body copy before the next major heading so readers reset mentally. If asides are frequent, consider a lighter background color or left border in CSS—those styles are easier to tune when sample pages exist early, which is exactly why this UX lab section is here.
