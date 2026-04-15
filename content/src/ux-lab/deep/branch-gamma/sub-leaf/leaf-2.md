# Sub-leaf — page two

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

Second pages in a small cluster often capture edge cases. Here the edge case is **relative imports**: Markdown links to siblings, parents, and cousins should resolve after HTML conversion. If your converter rewrites links, test both `.md` sources and generated `.html` targets in the browser.

## Cousin links

Linking to [leaf 1](leaf-1.md) and [leaf 3](leaf-3.md) keeps readers inside the sub-leaf folder. Linking to [topic A1](../../branch-alpha/topic-a1.md) jumps sideways across branches—useful for verifying that `../` chains stay correct when the site output mirrors the source tree.

## Narrative filler

Real documentation would explain why cross-branch links matter: shared dependencies, coordinated releases, or unified on-call rotations. Synthetic text only needs to occupy space so scrolling and scanning feel realistic when you evaluate typography.
