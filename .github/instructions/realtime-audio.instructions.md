---
applyTo: "plugins/write-realtime-audio-code/**/*.md"
excludeAgent: "cloud-agent"
---

# Real-Time Audio Review Instructions

- Validate external documentation fragments against the page's actual HTML `id` attributes. Rust Reference rule labels such as `undefined.race` and `undefined.alias` are displayed names; the linked live page uses `r-undefined.race` and `r-undefined.alias` as its anchor IDs. Do not remove the `r-` prefix based only on the displayed rule label.
