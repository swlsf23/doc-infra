# Troubleshooting

## Build fails immediately

Check manifest validation output first. Most early failures are duplicate output paths or missing sources.

## HTML looks wrong

Inspect the converter plugin output in isolation. Compare against golden fixtures for a small Markdown sample.

## Links pass locally but fail in CI

Case sensitivity differs between macOS and Linux. Normalize paths and enforce consistent casing in manifests.

## Slow builds

Measure whether time is spent in conversion, asset copying, or link checking. Parallelize only after profiling.
