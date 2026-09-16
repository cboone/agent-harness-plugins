# Events and Timing

Define the time domain before processing an event. Block-relative offsets, an internal sample timeline, CLAP `steady_time`, and musical transport positions have different meanings. `steady_time` can be `-1`; between consecutive `process` calls without an intervening `reset`, the CLAP process contract requires an available value to be nonnegative and advance by at least `frames_count`. Reset can restart that sequence, so define its discontinuity policy explicitly. A transport position can move backward across a seek, reset, or loop, but a change in either time value does not identify the cause by itself. Respect transport validity flags and in-block transport events before treating transport data as a scheduling boundary.

## Event Boundaries and Scheduling

Treat a block as a half-open sample interval. Validate event space, type, header size, address, and offset before interpreting a payload. Split processing at valid offsets, preserve required order for equal offsets, handle unknown events under the selected API, and emit output events in nondecreasing sample order. Test minimum, maximum, and varying blocks, equal offsets, final-frame events, and an internally scheduled event at the next block boundary. At 48 kHz, 1024 frames span about 21.3 ms; this illustrates block-boundary quantization, not a guarantee that smaller blocks hide defects.

Use an internal sample timeline for delayed events across blocks. Define its reset and discontinuity behavior, and bound event admission, per-block work, and active voices. A scheduled note-on carries a termination obligation, including when an early note-off arrives before the delayed start. Apply the overflow policy from [lock-free buffers](lock-free-buffers.md), rather than dropping events by recency.

CLAP note matching uses the complete `(port, channel, key, note_id)` address. `CLAP_EVENT_NOTE_ON` requires a valid nonnegative input port index, channel in `0..15`, and key in `0..127`; its `note_id` can be `-1` when unspecified. Validate these upper bounds and the configured port count as well as nonnegativity. For matching events such as note-off, choke, and end, use `-1` wildcards only where the event contract permits them. A note ID does not replace the other fields. Note-off, choke, and end have different meanings. CLAP note-on velocity zero remains a note-on; do not import MIDI 1.0's special encoding.

Host event pointers and process buffers have API-defined lifetimes. Copy a payload that must survive the callback, including variable-size SysEx, into bounded owned storage with an admission policy. A failed output `try_push` does not deliver the event. Retain required state for a defined later opportunity or follow the selected product recovery policy.

## Processing Status and Lifecycle

Choose CLAP process status from audible output and internal obligations. Delayed notes and retained termination events can require another callback while current audio is silent. Do not use `CLAP_PROCESS_SLEEP` or `CONTINUE_IF_NOT_QUIET` when pending work needs future processing. Use `CONTINUE` when required, and use tail status only if the declared tail contract covers the remaining work. If work arrives outside `process`, audit the permitted `clap_host.request_process()` path, including its thread and notification constraints: returning `CONTINUE` cannot wake a host that has stopped calling `process`.

Reset and deactivation clear the appropriate internal state, but they do not provide an output event list. Clearing a note table is not itself a downstream note-off. A retained rejected event cannot promise delivery if the host stops offering output opportunities. Define transport stop, bypass, tail completion, reset, and deactivation separately, including selected bypass latency and transition behavior.

## Automation Before Smoothing

Decode value steps, automation curves, render ramps, and modulation in the host's time domain before adding DSP smoothing. A host trajectory should not accidentally become a new target ramp at each received endpoint. State the intentional law, units, and effect on published automation behavior.

VST3 parameter queues specify a piecewise-linear normalized-value curve. Account for omitted first points, empty queues for unchanged sections, and a slope represented only by the block's final point. In that case, the previous value is the implicit point at offset `-1`. Reconstruct the curve before converting to DSP units, and preserve jumps from adjacent point encoding.

An AUv3 parameter ramp arrives in the render cycle where it begins and can continue through later cycles without another event. Retain remaining duration and trajectory across blocks. CLAP `PARAM_VALUE` and `PARAM_MOD` have different semantics. Respect port, channel, key, and note targeting. A polyphonic modulation amount already includes the monophonic contribution, so adding both again changes the requested value. Keep the stored base value distinct from its effective modulation.

Apply a discrete target at its event offset, then choose a law appropriate to its domain. Recompute sample-rate-dependent coefficients at the suitable lifecycle boundary. Initial setup, reset, preset loading, and state loading can need distinct policies. Stepped values are discrete. JUCE multiplicative smoothing cannot reach zero, so specify a mute or zero policy rather than applying it to every parameter. Crossfade only when semantics and bounded resources justify it.

## Deterministic Trace

Build a trace with a delayed note-on and note-off, equal-offset events, an output rejection, a discontinuity, silent blocks with pending work, and deactivation with outstanding obligations. Add separate traces for a sparse VST3 curve, an AUv3 ramp across blocks, and CLAP base values with targeted modulation. Check multi-port matching, wildcard addresses, continuity, optional smoothing behavior, stepped values, and a zero target.

### Example: Bounded Two-Block Trace

The scheduler accepts at most two pending events. At block 1000 with 64 frames, it receives note-on `(0, 0, 60, 7)` at offset 8 for delivery at sample 1080, then its note-off at offset 20. Admission reserves the note-off slot when accepting the note-on. The selected policy records `released_before_start` on that pending note at offset 20; it does not emit a note-off before the note-on. A same-offset parameter value and note event preserve the host's declared order. A discontinuity resets the internal timeline according to the selected transport policy and clears only obligations that the policy permits clearing.

The next 64-frame block starts at sample 1064. At offset 16, the scheduler starts the internal note for sample 1080, reads `released_before_start`, then attempts a `CLAP_EVENT_NOTE_END` after that start. `NOTE_END` tells the host that the plugin has ended the voice; its event time is ignored, so the example relies on ordering rather than a sample-offset guarantee. If the output list rejects that `NOTE_END`, it retains `{ port: 0, channel: 0, key: 60, note_id: 7, termination_pending: true }` and returns `CLAP_PROCESS_CONTINUE` while audio is silent. It retries only on the next valid output opportunity, then clears the obligation only after a successful push. Deactivation clears the local schedule without claiming it emitted an unavailable output event. Separately, a VST3 block with only a final point at offset 63 interpolates from the prior value at offset `-1`; an AUv3 96-sample ramp retains 32 samples of duration after a 64-sample block; and a zero target takes the explicit mute path rather than multiplicative smoothing. These traces establish the selected policy and must be adapted to each host contract.

## Sources

- [CLAP events](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/events.h), [process status](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/process.h), and [tail](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/ext/tail.h)
- [VST3 parameter queues](https://steinbergmedia.github.io/vst3_doc/vstinterfaces/classSteinberg_1_1Vst_1_1IParamValueQueue.html), [AU render events](https://developer.apple.com/documentation/audiotoolbox/auinternalrenderblock), and [JUCE smoothing](https://docs.juce.com/master/classjuce_1_1SmoothedValue.html)
