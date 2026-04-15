# Publishing

Publishing is mostly “copy `dist/` to hosting,” but a few details recur in real projects.

## Artifacts

- HTML pages
- Static assets (CSS, JS, images)
- Optional `sitemap.xml` and `robots.txt`

## Environments

Keep environment-specific values (analytics IDs, API endpoints) out of Markdown unless you have a templating pass that injects them safely.

## Rollbacks

Versioned deployments make rollbacks easy. Pair that with immutable asset URLs when possible.
