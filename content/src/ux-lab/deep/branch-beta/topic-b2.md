# Branch beta — topic B2

Data quality checks often deserve their own page. This stub describes validation rules—null rates, uniqueness, referential integrity—in prose form. Real docs might attach SQL snippets; here we avoid extra block types so the page remains a paragraph-forward sample.

## Thresholds and alerts

Thresholds should reflect business tolerance, not only statistical variance. A one-percent spike in nulls might be benign during a holiday freeze or catastrophic during a migration weekend. Explain trade-offs across multiple sentences so readers understand that alerting is contextual.

## Owner responsibilities

Data producers and consumers rarely share the same OKRs. Documentation bridges that gap by naming owners for schema fields, pipelines, and dashboards. Long paragraphs listing responsibilities help UX testers see how bold names and inline code might interleave in production.

## Next

Continue to [topic B3](topic-b3.md).
