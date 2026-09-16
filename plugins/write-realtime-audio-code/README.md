# Write Real-Time Audio Code

Write and review real-time audio code: callback safety, bounded cross-thread communication, memory ordering, sample-accurate events, and compatible plugin parameters and state.

**Type:** Skill
**Trigger:** `/write-realtime-audio-code` (also activates automatically)

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

This guide maps callback reachability and lifecycle before selecting a communication protocol or a memory ordering. It covers buffer and output contracts, bounded work, parameter and state compatibility, sample-accurate events, smoothing, numerical recovery, host-independent cores, and verification evidence.

Reading the guide has no hard external dependency. Executing a sanitizer, model check, or host validation procedure requires a compatible downstream toolchain, target, and host arrangement.

## Usage

```text
/write-realtime-audio-code
```

The skill also activates automatically for real-time audio implementation, review, and planning requests.

## Examples

- "Review this audio callback and its UI meter path": maps callback-reachable work and chooses a legal ownership transfer.
- "Can this parameter queue use relaxed atomics?": identifies whether it publishes only one self-contained value or an ordinary payload.
- "Add a parameter without breaking saved automation": checks released identifiers, state migration, reactivation, and event behavior.

## See Also

- [Plant Defects](../plant-defects/README.md): design a control that proves a test or instrument can detect the intended defect
- [All plugins](../../README.md)
