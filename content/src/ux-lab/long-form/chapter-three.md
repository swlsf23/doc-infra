# Chapter three — cross-links and tone

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

Cross-links are how readers move between chapters without relying solely on the site navigation. In this stub, links point at sibling pages inside `ux-lab/long-form` and occasionally at the layouts section. When you click through, confirm that the iframe-based navigation highlights feel consistent and that the browser history stack behaves as expected when you alternate between sidebar links and in-body anchors.

## Linking backward and forward

Start by referencing the [long-form overview](overview.md) so the reader can refresh the purpose of this section. Then point forward to the [very long scroll test](very-long-scroll-test.md), which exists specifically to exceed one viewport height by a wide margin. Intermediate chapters like [chapter one](chapter-one.md) and [chapter two](chapter-two.md) provide stepping stones so the link graph is not a star centered only on the stress page.

## Tone and voice

Even dummy text benefits from a consistent voice. Here the tone is neutral, slightly formal, and oriented toward internal tooling. If your real documentation prefers second person or a more conversational rhythm, replace these paragraphs wholesale—the layout tests will still apply because length and structure remain similar.

## What to watch while testing

Pay attention to focus rings when tabbing through links inside the main column, especially after hiding the sidebar with the compact toggle. Screen reader users will rely on landmarks and heading levels; keep that in mind if you later add skip links or adjust heading order in the converted HTML.
