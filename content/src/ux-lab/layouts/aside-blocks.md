# Aside blocks (prose simulation)

Real documentation systems often render **notes**, **warnings**, and **tips** as aside elements or blockquotes. This page simulates that pattern using plain Markdown emphasis and paragraphs so you can preview spacing and hierarchy before your converter emits richer HTML.

**Note:** In a production pipeline, this paragraph might live inside a bordered component with an icon. For now, bold labeling stands in for the chrome. Check that the bold line does not sit too close to neighboring paragraphs when the sidebar is hidden and the main column expands.

**Warning:** Destructive operations should always require confirmation. If your UX uses modals, ensure keyboard focus moves predictably and that documentation pages do not trap focus when embedded in iframes elsewhere. This warning is intentionally verbose so you can see how multiple sentences behave when they are visually grouped with a label.

**Tip:** Keep titles short. Readers scan headings first; long headings wrap awkwardly on mobile and compete with navigation labels. When in doubt, split content into two headings rather than one heading with a subordinate clause that stretches across the entire line.

## Returning to normal body text

After simulated asides, ordinary paragraphs should feel calmer. The transition matters: add a line of body copy before the next major heading so readers reset mentally. If asides are frequent, consider a lighter background color or left border in CSS—those styles are easier to tune when sample pages exist early, which is exactly why this UX lab section is here.
