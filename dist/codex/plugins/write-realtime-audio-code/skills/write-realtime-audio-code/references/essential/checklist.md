# Real-Time Audio Checklist

Answer each question from the change and its applicable host contract. Follow the linked reference when the answer needs a protocol or API explanation.

## Callback Contract

- [ ] Are advertised buses, channel counts, sample formats, legal aliases, and every required output sample handled? See [audio-thread rules](../comprehensive/audio-thread-rules.md).
- [ ] Does each permitted block size, including a permitted zero-size block, have bounded API-specific handling, and does an oversized input follow the documented rejection or recovery path?
- [ ] Are host pointers used only for their documented lifetime, and are host values validated before bounded memory access?

## Thread and Lifecycle Map

- [ ] Does the call graph include start, stop, reset, active flush, error paths, destructors, and each render worker? See [audio-thread rules](../comprehensive/audio-thread-rules.md).
- [ ] Are symbolic thread rules used instead of assuming one permanent operating-system thread?
- [ ] Are deactivation, destruction, and separate users ordered before storage reclamation?

## Ownership and Communication

- [ ] Does each storage location name its producer, consumer, publication point, reuse acknowledgment, capacity, and reclamation thread? See [lock-free buffers](../comprehensive/lock-free-buffers.md).
- [ ] Are queue draining, notification, payload copy, payload destruction, reset, and retirement work bounded on the callback?
- [ ] Can overflow discard a termination obligation or prevent its next processing opportunity?
- [ ] Does a stalled consumer leave the callback with a defined bounded fallback?

## Memory Ordering

- [ ] Does the protocol state the payload, release publication, acquire observation, and reverse edge before storage reuse? See [memory ordering](../comprehensive/memory-ordering.md).
- [ ] Are lifetime, alignment, aliasing, and reference-validity arguments made separately from atomic ordering?
- [ ] Is every relaxed operation self-contained, owner-local, or otherwise justified without publishing ordinary payload?

## Verification

- [ ] Do selected tools cover the claimed property, actual plugin-loading arrangement, and each real-time entry point? See [verifying concurrency](../comprehensive/verifying-concurrency.md).
- [ ] Did the positive control produce the expected diagnostic at the intended operation?
- [ ] Are subject verdict, control sensitivity, executed paths, configuration, and unverified areas reported separately?
- [ ] Do timing records include first calls, periodic spikes, elapsed callback cost, and missed deadlines under a stated configuration?

## Parameters and Identifiers

- [ ] Are released CLAP IDs, VST3 `ParamID`s, Audio Unit IDs or addresses, product identities, and parameter meanings preserved? See [parameters and state](../comprehensive/parameters-and-state.md).
- [ ] Does a fixture exercise automation after a parameter is inserted or reordered, including an AUv2 wrapper mapping where applicable?

## State

- [ ] Does a failed load leave the current instance unchanged and publish only a complete validated replacement?
- [ ] Does a structural change wait for the permitted deactivation, activation, and notification transition?
- [ ] Are short reads, writes with no progress, unknown fields, unsupported versions, and non-finite decoded values handled by the schema policy?

## Events and Timing

- [ ] Are event type, size, address, offset, ordering, lifetime, and output failure handled by the selected API contract? See [events and timing](../comprehensive/events-and-timing.md).
- [ ] Are host curves, ramps, and modulation decoded before intentional smoothing?
- [ ] Do silent blocks, discontinuities, reset, bypass, and deactivation preserve or clear pending obligations according to a documented policy?

## Numerics

- [ ] Are recursive tails, non-finite inputs and state, overflow, subnormals, and floating-point flags covered by a bounded recovery policy? See [audio-thread rules](../comprehensive/audio-thread-rules.md).
- [ ] Does the selected transition law support its parameter domain, including a zero or mute policy where needed?

## Core Boundaries

- [ ] Does the core boundary have an enforced dependency or signature rule, with a failing control where the claim needs enforcement? See [the pure-core seam](../comprehensive/the-pure-core-seam.md).
- [ ] Are core-vector results kept separate from adapter evidence for buffers, events, host status, and reactivation?
