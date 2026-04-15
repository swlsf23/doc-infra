# Next steps

You now have a small library of sample Markdown across nested folders. Use it to test:

- Path normalization and duplicate detection
- Multi-file includes
- HTML conversion and post-processing hooks

## Suggested experiments

1. Add a deliberate duplicate output path in a throwaway manifest and confirm the validator catches it.
2. Reference the same source file from two manifest entries with different output paths and confirm both builds succeed.
3. Introduce a broken internal link and confirm link checking reports it during site build.

When those behaviors are green, the scaffolding is doing its job.
