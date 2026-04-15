# Tables and code

Tables and fenced code blocks are two of the fastest ways to break a narrow layout or force horizontal scrolling on small screens. This page includes both so you can resize the window, toggle the navigation sidebar, and observe whether scrollbars appear in the right places—on the main column, the page, or an inner container.

## Sample configuration table

The following table is wider than a typical phone screen in monospace terms. It is acceptable if the main region scrolls horizontally as long as the header row remains discoverable and the first column stays readable.

| Service        | Region | Min instances | Max instances | Notes                                      |
| -------------- | ------ | ------------- | ------------- | ------------------------------------------ |
| api-gateway    | us-west| 3             | 24            | Scale on CPU > 65% sustained five minutes |
| worker-batch   | us-west| 1             | 12            | Queue depth threshold drives scale-out     |
| notifier       | global | 2             | 8             | Keep N+1 across zones for redundancy       |
| search-indexer | eu     | 2             | 16            | Rebuild windows coordinated with storage   |

If the table feels cramped, consider enabling zebra striping in CSS or increasing cell padding slightly. Avoid shrinking font size below the body text unless you also provide a zoom-friendly alternative.

## Fenced code sample

```text
# Hypothetical deploy snippet — not executable in this repo
export ENVIRONMENT=staging
export ROLLBACK_WINDOW_MINUTES=45
run_pipeline --manifest ./deploy/staging.yml --require-approval
```

Long lines inside code blocks should scroll independently of body text. If the entire page scrolls sideways because of a code block, check overflow rules on `pre` and `code` elements in your stylesheet.

## Narrative wrap-up

Tables and code rarely stand alone. Surround them with short introductions and interpretations so scanners understand what to look for. This closing paragraph returns to full-width prose so you can compare spacing above and below block elements against a normal paragraph flow.
