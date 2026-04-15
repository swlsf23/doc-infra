# Dense lists

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

Bullet lists compress information. When many bullets appear in sequence, vertical spacing and marker alignment become visible at a glance. This page stacks nested lists and mixed list types so you can confirm the doc theme keeps indentation predictable and does not collide with the sidebar gutter on medium-width viewports.

## Shallow checklist

- Confirm build artifacts are immutable and tagged by commit SHA.
- Verify secrets never appear in logs or client-visible error strings.
- Run smoke tests against staging before promoting to production.

## Nested responsibilities

- Platform
  - Maintain base images and patch schedules.
  - Coordinate kernel upgrades with capacity planning.
  - Own incident bridges for regional outages.
- Product engineering
  - Ship feature flags with safe defaults.
  - Document rollback steps beside launch notes.
  - Participate in post-incident reviews when features contribute to failure.
- Security
  - Review threat models for new data flows.
  - Approve third-party dependencies above a risk threshold.
  - Track certificate expirations and DNS hygiene.

## Numbered escalation

1. Page the primary on-call rotation for the affected subsystem.
2. If fifteen minutes pass without acknowledgment, escalate to secondary.
3. If customer impact is confirmed, open a status page and notify account teams.

Dense lists should still leave room to breathe. If markers crowd the text, increase list padding or reduce bullet size slightly before changing the overall font scale.
