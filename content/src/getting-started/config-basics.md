# Config basics

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

Configuration is split so authors do not have to touch infrastructure knobs for everyday writing.

## Layers

| Layer | Purpose |
| --- | --- |
| `convert/config.yml` | Paths, plugins, defaults for the build tool |
| Manifest | What gets built, in what order |
| `site-config.yml` | Site-wide presentation data |

## Example snippet

```yaml
output_dir: dist/site
manifest: content/manifest.yml
```

Replace values when your implementation reads real keys.
