# Chapter two — lists interleaved with prose

Long documentation rarely sticks to pure paragraphs. Writers interleave numbered steps, nested bullets, and definition lists. This chapter mixes those patterns with uninterrupted paragraphs so you can verify that list markers align with the main text column and that nested lists do not collide with the sidebar when the layout is only two columns wide.

## Narrative with a short list

Sometimes a paragraph introduces a decision tree that is easier to scan as bullets than as prose. For example, you might document three ways to recover from a failed deploy: roll back the artifact, replay a canary stage, or freeze traffic while operators inspect logs. Each option can be a single line in a list while the surrounding paragraphs explain trade-offs in full sentences.

- Roll back when the failure is clearly tied to a single release artifact.
- Replay the canary when metrics look ambiguous but the blast radius is still small.
- Freeze traffic only when data integrity is at risk and stakeholders are online.

## Deeper nesting without tables

Nested lists are notorious for horizontal overflow on small screens. The following structure is intentionally deep so you can collapse the sidebar, open devtools, and watch how wrapping behaves when the viewport is barely wider than a phone in landscape orientation.

- Top-level concern: operator visibility
  - Sub-point: dashboards must show lag under one minute during incidents.
  - Sub-point: on-call rotations should surface ownership for each subsystem.
    - Detail: paging policies differ between business hours and weekends.
    - Detail: some teams prefer chat-based alerts for non-critical drift.

## Returning to prose

After a dense list, writers often add another paragraph to reset the rhythm. That paragraph might summarize what the reader should remember before moving to the next chapter, or it might tee up a code sample on another page. Either way, the transition should feel intentional rather than abrupt, even when the words themselves are synthetic.
