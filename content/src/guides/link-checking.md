# Link checking

Internal links should resolve against the set of built pages. External links are optional and may be slower or flaky.

## Internal links

Use relative paths that match the published site structure once routing rules are defined. Broken internal links should fail the site build when strict mode is enabled.

## External links

Consider rate limits and network availability. Many teams run external checks on a different schedule than PR builds.

## Anchors

Heading IDs may be generated from titles. If your converter customizes slugs, link checks must use the same rules.
