# First build

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

Once the manifest describes your sources, the build should be a single command away.

## Minimal flow

1. Author content under `content/src/`.
2. Point the manifest at those files with explicit paths.
3. Run the build and inspect the output directory.

## Output

Expect HTML (or intermediate artifacts) under the configured output root. The exact layout is defined by the site build stage, not by this sample page.

## See also

- `guides/pipeline-stages.md` for how stages are separated.
- `reference/file-locations.md` for path conventions used in these examples.
