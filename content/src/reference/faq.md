# FAQ

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

## Why YAML for the manifest?

It stays readable in review, supports hierarchy, and diffs cleanly.

## Why not glob everything?

Explicit composition keeps builds auditable and makes per-build variants straightforward.

## Can one page appear twice?

The same **source** can map to multiple **outputs**. Two outputs cannot share the same destination path.

## Where do React apps fit?

Outside the core converter. Treat UI shells as optional plugins that consume generated artifacts.
