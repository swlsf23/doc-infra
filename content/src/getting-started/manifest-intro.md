# Manifest introduction

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

The manifest is the authoritative list of generated pages. It is **ordered**: sibling order matters for build order and for navigation consumers later.

## Principles

- **Explicit includes** over implicit directory scans.
- **Unique output paths** across the composed manifest.
- **Reuse** is modeled as the same input mapped to multiple outputs—each output path remains unique.

## Validation

Parsing and validation should fail fast, before any copying or conversion begins. That keeps error messages close to the authoring mistake.
