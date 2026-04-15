# Responsive notes

::: note
Placeholder material for internal testing only. No operational, analytical, or evaluative use is intended.
:::

Responsive design is not only about breakpoints. It is about **priorities**: which content stays visible when the viewport narrows, which navigation patterns collapse, and which auxiliary widgets disappear first. This page collects long paragraphs that describe hypothetical breakpoints so you can read them while resizing the browser and watching the doc layout adapt—or not—depending on your current CSS.

## Desktop-first assumptions

Many internal tools assume a desktop monitor. Writers embed wide screenshots, assume hover states, and describe multi-pane workflows. When those same docs are opened on a tablet in landscape orientation, sidebars may consume precious width. If your site uses a flex row with a fixed sidebar, test whether the main column can shrink below a comfortable measure without overlapping the iframe navigation.

## Mobile-first counterpoints

Mobile-first documentation starts with a single column, then adds complexity as width increases. That philosophy can clash with dense tables and wide code samples. A pragmatic compromise is to keep prose readable at all sizes while allowing horizontal scroll for exceptional blocks. Document that behavior so readers do not blame their hardware when a table scrolls sideways.

## What to verify manually

Resize slowly from wide to narrow and back. Watch for text reflow bugs where the last word of a paragraph wraps alone on a new line, or where headings orphan their first sentence. Toggle the sidebar open and closed at each width. If anything feels unstable, capture the viewport width in a ticket and fix CSS before adding more content.

## Long closing paragraph

Documentation that discusses responsiveness often ends with a reminder to test with real devices and assistive technologies. Screen readers may ignore visual reflow but still benefit from logical heading order and descriptive link text. Keyboard users need visible focus indicators on every interactive control, including the compact navigation toggle in the sidebar. If those details are easy to forget during a visual redesign, keep this page bookmarked so the team revisits the checklist whenever the shell changes.
