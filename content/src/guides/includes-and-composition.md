# Includes and composition

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

Large sites should split manifests across files, then compose them with explicit include nodes.

## Rules of thumb

- Prefer **named fragments** checked into version control.
- Keep include order stable; it doubles as build order.
- Avoid globbing as the default discovery mechanism—explicit lists scale better for audits.

## Failure modes

- Two fragments both emit the same output path.
- A fragment references a missing file.
- Circular includes (detect and error).

Each of these should surface during manifest validation, not halfway through conversion.
