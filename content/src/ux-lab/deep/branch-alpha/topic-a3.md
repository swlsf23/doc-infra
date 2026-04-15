# Branch alpha — topic A3

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

Access control appears in almost every deep runbook. This page talks about roles, bindings, and audit logs in abstract terms so you can evaluate how much vertical space a security-heavy section consumes when sandwiched between operational content elsewhere in the branch.

## Roles and bindings

Roles should map to job functions rather than named employees. Bindings attach roles to principals at specific scopes: organization, project, resource group, or individual resource. When documentation explains that hierarchy, paragraphs tend to grow because exceptions abound—break-glass access, time-bound elevation, and emergency overrides all deserve sentences of their own.

## Audit expectations

Auditors want immutable logs with trustworthy timestamps. Operators want logs they can search without waiting minutes for results. Balancing those needs is a product decision; the documentation only needs to show how much text typically accumulates when both sides are acknowledged fairly.

## Navigation

Use [topic A2](topic-a2.md) and [topic A4](topic-a4.md) as sibling navigation targets. If relative links fail, the bug is likely in path resolution during HTML generation, not in this stub.
