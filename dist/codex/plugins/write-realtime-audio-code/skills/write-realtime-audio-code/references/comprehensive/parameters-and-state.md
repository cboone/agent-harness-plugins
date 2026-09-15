# Parameters and State

Treat released parameter and plugin identities as compatibility contracts. Assign permanent identifiers explicitly, independently of display names and enumeration positions. Do not reuse released IDs. Preserve the meaning, range, normalization, and automation mapping of an ID, or provide a documented compatible migration.

## Identity and Presentation

Keep CLAP parameter IDs, VST3 `ParamID`s and normalized values, AUv2 IDs, and AUv3 addresses distinct. Inventory the released CLAP plugin ID, VST3 class IDs, Audio Unit type, subtype, and manufacturer, plus relevant bundle identity. For the selected format, record which fields identify the product, influence signing or preferences, or are presentation metadata. Wrapper defaults can make metadata part of identity; an AU type derived from the first CLAP feature has an explicit wrapper override.

A compatible replacement preserves released identity. A co-installable development channel is a separate product decision and may need distinct identity. fosforo's provenance stamping without an identity namespace is a project choice. A version string is not a plugin identifier, but hosts can still retain version information.

Maintain a baseline fixture of released IDs, meanings, and saved state. After insertion or reordering, exercise a real automation binding. A source canary over an enum complements that fixture but cannot prove host compatibility.

## AUv2 Wrapper Ordering

At clap-wrapper revision `1cca996e96f29ab2be7ae9f8cfe532bbc92e1dd6`, extension `clap.plugin-auv2-param-ordering/0` has a source discrepancy. Its header describes `ordering[CLAP index] = AUv2 position`; the implementation consumes `ordering[AUv2 position] = CLAP index`. Use the implementation mapping for that revision and preserve the historical relative order of existing parameters. Do not extend this conclusion to other wrapper versions or hosts.

Use a permutation that differs from its inverse. With CLAP parameters `[A, B, C]` and `ordering = [2, 0, 1]`, the pinned implementation exposes AUv2 order `[C, A, B]`; the inverse interpretation gives `[B, C, A]`. Identity mappings and two-element swaps cannot detect the direction. Source inspection establishes the code's mapping. Host compatibility needs the wrapper's parameter list and a preserved automation binding.

## State Schema and Publication

Specify the state schema and migration policy from the first release. A binary magic value, version, and fixed endianness are one implementation option, as illustrated by fosforo. The policy must define missing-field defaults, recognized old versions, unsupported newer versions, unknown fields, and meaning changes. Do not mandate append-only binary records or accept arbitrary trailing bytes without a schema rule.

Bound parsing lengths and allocations on a permitted thread. Handle truncated and corrupt input, partial reads and writes, and a zero-byte write as no progress rather than an infinite retry. Validate decoded values, including non-finite values, then publish a complete replacement. A failed load leaves the current instance unchanged. Saving on the main thread needs a coherent snapshot when audio processing can update state; loading needs a safe handoff while processing continues.

## Structural Changes

Distinguish three state-change classes:

| Change                                     | May apply while active?                        | Required behavior                                                                             |
| ------------------------------------------ | ---------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Compatible parameter value                 | As the selected parameter contract allows      | Preserve released meaning and publish through the permitted event or flush path               |
| Prepared internal replacement              | Only if it preserves active host configuration | Transfer ownership safely and reclaim after readers acknowledge                               |
| Latency, ports, or other structural change | No, unless the host specifically permits it    | Keep the current configuration active until deactivation, activation, and notifications occur |

An ownership-safe swap solves only the internal-replacement case. It does not authorize changing negotiated latency or ports while active. Track what is pending and what audio-thread and main-thread queries expose until a permitted transition.

CLAP latency changes during activation, and its `changed` notification is limited to that phase. Structural ports and parameter changes requiring `CLAP_PARAM_RESCAN_ALL` require deactivation and their documented rescan contract. Use value, text, and info rescan flags for cache or presentation changes; reserve structural rescans for changes that alter the parameter set. A host's `request_restart` can be delayed, so continue with the current valid configuration without waiting in the callback or reporting the pending configuration as active. Update host-visible caches and notifications only at permitted boundaries.

Keep `get_value` coherent on the main thread. Do not call `clap_host_params.request_flush` on the audio thread. During `process` or active `flush`, use the supplied output event interface for parameter events and handle failed pushes. Use gestures where appropriate. When an output parameter change mirrors mapped MIDI input, set `CLAP_EVENT_DONT_RECORD` so the host does not record the same change as new automation. State-driven value changes need the matching main-thread rescan so host caches do not become stale.

## Worked State Transition

1. Parse a new preset on an allowed thread into owned temporary storage.
1. Reject truncation, invalid values, unsupported versions, short writes, and no-progress writes without changing the active instance.
1. Publish a compatible prepared replacement only when its reader and retirement protocol is ready.
1. For a latency or port change, mark it pending, keep processing the current configuration, request the permitted restart or rescan, then complete the transition through deactivation and activation.
1. Exercise reordered parameters, changed meanings, failed-load preservation during processing, delayed restart, and notifications in a host or format fixture.

### Example: Preset With Pending Latency

An established plugin stores `gain` as CLAP ID 10 and `mix` as CLAP ID 20. Its baseline fixture records those IDs, normalized meanings, and an automation lane bound to ID 20. A new `drive` parameter receives ID 30, so the fixture verifies that the earlier bindings still resolve. For the pinned AUv2 wrapper, `[A, B, C]` with `ordering = [2, 0, 1]` must present `[C, A, B]`; this is a source-level mapping check until a host fixture also verifies its parameter list and automation binding.

A main-thread loader decodes a preset into temporary owned storage. A truncated stream fails before publication, leaving the active instance unchanged. A valid preset that changes latency records `pending_latency = 128`, continues processing the active 64-sample configuration, requests restart on the permitted thread, and exposes 64 until deactivation and activation complete. After activation, the host-visible latency is 128 and the required notification has occurred. The trace proves transactional state handling and a delayed transition policy for this example, not every host's restart behavior.

## Sources

- [CLAP parameters](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/ext/params.h), [state](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/ext/state.h), [latency](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/ext/latency.h), [ports](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/ext/audio-ports.h), and [host](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/host.h)
- [VST3 parameters and automation](https://steinbergmedia.github.io/vst3_dev_portal/pages/Technical%2BDocumentation/Parameters%2BAutomation/Index.html) and [AU parameter addresses](https://developer.apple.com/documentation/audiotoolbox/auparameteraddress)
- [clap-wrapper ordering header](https://github.com/free-audio/clap-wrapper/blob/1cca996e96f29ab2be7ae9f8cfe532bbc92e1dd6/include/clapwrapper/auv2.h) and [pinned implementation](https://github.com/free-audio/clap-wrapper/blob/1cca996e96f29ab2be7ae9f8cfe532bbc92e1dd6/src/wrapasauv2.cpp#L370)
