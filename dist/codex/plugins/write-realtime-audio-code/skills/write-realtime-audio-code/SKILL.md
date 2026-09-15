---
name: write-realtime-audio-code
description: >-
  Write and review real-time audio code: callback safety, bounded cross-thread
  communication, memory ordering, sample-accurate events, and compatible plugin
  parameters and state.
---

# Write Real-Time Audio Code

Use the host contract and a stated communication protocol to make callback-reachable code safe, bounded, and compatible.

## When to Use

Apply this skill to an audio callback and all of its reachable code, including audio-to-UI paths, audio-related atomics and lifetimes, real-time verification, plugin parameters and state, event timing, smoothing, numerical behavior, and host-independent cores.

Do not activate it only because a change has a queue, an atomic, DSP mathematics, GUI code, server concurrency, or offline processing. Shared code remains in scope when a real-time callback reaches it. Check a host-specific offline-rendering contract before treating that mode as non-real-time.

## Core Constraints

An audio callback has bounded work only in the context of its host contract. Inspect transitive callees, notifications, payload copies, and final destruction. Prove that shared-memory access, state publication, storage reuse, aliases, and required output samples are legal. Preserve released identities, automation meaning, and host transitions. A race detector gives evidence about exercised access patterns; it does not measure deadline compliance.

## Read the Callback Contract First

Record these facts before choosing an implementation or review conclusion:

- The host API, lifecycle phase, symbolic thread, and any render workers.
- Buffer layouts, sample formats, aliases, lifetimes, legal block sizes, and required output behavior.
- Pending-event and process-status obligations, including reset, flush, and deactivation.
- Whether processing is real-time or an explicitly supported offline mode.

Use the downstream project's existing conventions to record relevant entry points and boundaries. Do not require a new thread annotation on every function.

## Workflow

1. Establish whether the request is a review, plan, or authorized implementation.
1. Map the changed callback call graph, lifecycle, shared storage, and host-facing transitions.
1. Read the [essential checklist](./references/essential/checklist.md), then select the detailed references that answer the remaining questions.
1. Record protocol assumptions, source and toolchain scope, capacity and work bounds, and failure policies.
1. For authorized implementation or experiments, use an instrument and a positive control suited to the claim. For a review, distinguish observed evidence from proposed checks.
1. Report what remains unverified, including paths, hosts, workers, loading arrangements, and tools that were not exercised.

## Reference Navigation

- [Audio-thread rules](./references/comprehensive/audio-thread-rules.md): use for callback reachability, lifecycle, buffers, work bounds, host calls, and numerical recovery.
- [Lock-free buffers](./references/comprehensive/lock-free-buffers.md): use when data, events, or immutable replacements cross an audio boundary.
- [Memory ordering](./references/comprehensive/memory-ordering.md): use after a protocol identifies the payload, publication, observation, and reuse edges.
- [Verifying concurrency](./references/comprehensive/verifying-concurrency.md): use to select a control, sanitizer, model, or deadline measurement and to scope its conclusion.
- [Parameters and state](./references/comprehensive/parameters-and-state.md): use for released plugin identity, parameter meaning, state loading, and host reactivation.
- [Events and timing](./references/comprehensive/events-and-timing.md): use for event order, automation, scheduling, status, smoothing, and numerical transitions.
- [The pure-core seam](./references/comprehensive/the-pure-core-seam.md): use when separating host-independent behavior from format adapters.
- [Rule-to-evidence map](./references/essential/rule-to-evidence.md): use when a review needs the source scope and example behind a safety-critical conclusion.

## Related Skill

When installed, [Plant Defects](https://github.com/cboone/agent-harness-plugins/tree/main/plugins/plant-defects) gives deeper guidance for designing and recording positive controls. This skill remains usable without it: [verifying concurrency](./references/comprehensive/verifying-concurrency.md) explains the subject, positive-control, and inconclusive-result distinctions locally.

## Sources

- [CLAP 1.2.9 headers](https://github.com/free-audio/clap/tree/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap)
- [Ross Bencina, "Real-time audio programming 101"](https://www.rossbencina.com/code/real-time-audio-programming-101-time-waits-for-nothing)
- [Timur Doumler, "Using locks in real-time audio processing, safely"](https://timur.audio/using-locks-in-real-time-audio-processing-safely)
