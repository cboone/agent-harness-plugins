---
applyTo: "plugins/write-realtime-audio-code/**/*.md"
excludeAgent: "cloud-agent"
---

# Real-Time Audio Review Instructions

- Validate external documentation fragments against the page's actual HTML `id` attributes. Rust Reference rule labels such as `undefined.race` and `undefined.alias` are displayed names; the linked live page uses `r-undefined.race` and `r-undefined.alias` as its anchor IDs. Do not remove the `r-` prefix based only on the displayed rule label.
- Assess reused atomic state values using modification order and write-read coherence. In the documented Rust per-slot handshake, each participant writes to the same atomic before polling it again; a later load cannot read a modification preceding that participant's own store. Do not infer an ABA hazard solely from repeated state values. An acknowledgment in a separate atomic or another participant changes the proof and must be assessed separately.
