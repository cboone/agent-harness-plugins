# Verifying Concurrency

Organize evidence around the property claimed. A passed instrumented run is evidence for reached, instrumented paths in a named configuration. It does not become proof of every schedule, every dependency, safe reclamation, or a callback deadline.

| Claim                                             | Evidence to collect                                                                                          | A passing result cannot establish                                                       |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| Legal shared-memory access                        | Ownership argument, exercised concurrent case, instrumented TSan subject, and an observed failing control    | All schedules, unexecuted paths, uninstrumented dependencies, or an all-atomic protocol |
| Bounds, lifetime, and selected undefined behavior | ASan, selected UBSan checks, deterministic boundary fixtures, and bounded parser or event fuzzing            | Complete language-level validity, unexecuted cases, or deadline compliance              |
| Protocol and lifetime behavior                    | State-transition tests, adversarial schedules, capacity and reclamation cases, and a suitable model checker  | Production-target callback timing                                                       |
| Prohibited callback operations                    | Structural audit, supported static-effects checks, RTSan reached entries, and a planted prohibited operation | Unreached or unsupported boundaries                                                     |
| Bounded callback work and deadline margin         | Operation and batch bounds plus optimized-build measurement under representative load                        | Exhaustive behavior from averages, sanitizer builds, or one stress run                  |
| Compatibility and event semantics                 | Serialized fixtures, host or automation checks, and deterministic event traces                               | Other formats or historical releases not exercised                                      |

## Positive Controls

Before accepting instrument sensitivity, build the intended subject and a deliberately defective arm, establish that both reach the operation and contend where required, then observe the expected diagnostic there. Record one of three control outcomes:

1. The intended defect was detected at the intended operation.
1. An unrelated build or runtime failure prevented evaluation.
1. The intended defect was not detected.

A compile failure or unrelated crash is not a successful runtime control. Judge the subject result and control sensitivity separately. A subject defect remains a defect even when the control is inconclusive. Keep mutations faithful: change the property under test without silently replacing the tested implementation.

## Memory, Model, and Harness Scope

Use ASan for exercised bounds and lifetime failures, and select UBSan checks deliberately for arithmetic, alignment, conversion, or other stated properties. The `undefined` group does not enable every check, and some UBSan configurations recover instead of failing a test. Fuzz owned state or event storage with bounded malformed lengths, sizes, types, values, and orderings. Do not manufacture inaccessible host pointers and call that a plugin validation strategy.

TSan observes races on executed, instrumented paths using its synchronization knowledge. It does not prove all-atomic delivery, linearizability, progress, safe reclamation, or every schedule. A weakened ordering may expose a race only when the ordering guards ordinary payload. A clean all-atomic run does not validate the protocol. Keep joins, barriers, progress counters, and rendezvous from adding a publication edge that masks the subject's weakened edge.

For a model checker, state version, memory-model coverage, participants, capacity, iteration or preemption bound, explored schedules, and correspondence to production. Loom 0.7.2 requires replacement synchronization types, including in relevant dependencies, and documents unmodeled reorderings. A completed bound is evidence for that model and its assumptions. A non-lapping experiment can isolate publication but says nothing about production lapping when a participant can be descheduled.

## RealtimeSanitizer and Loading

For a supported Clang configuration, `-fsanitize=realtime` and `[[clang::nonblocking]]` can provide evidence for reached prohibited operations. Function Effect Analysis has separate warning settings such as `-Wfunction-effects`; state whether the project makes those diagnostics fail. Upstream LLVM 20 support and Apple compiler version numbering are different version scopes. The documented Rust standalone integration requires `RTSAN_ENABLE=1`; check target and build integration before prescribing it.

Test the actual plugin-loading arrangement as well as a standalone executable. Current RTSan documentation describes `verify_interceptors` and failure when a runtime loads too late, including through `dlopen`; older releases need separate confirmation. Identify reached contexts for process, reset, active flush, and every worker. A worker needs its own prohibited-operation control because a caller's thread-local real-time context does not transfer automatically. Record uncovered foreign code, callbacks, and loading arrangements.

## Deadline Measurements

Measure optimized production builds separately from sanitizer runs. Cover supported block sizes and sample rates, event density, maximum voices, numerical tails, multiple instances, and relevant concurrent UI, loading, or background activity. Include first callbacks after activation or reconfiguration and periodic work that causes spikes.

Record hardware, operating system, host and driver, compiler, backend, optimization mode, target, flags, measured duration, sample count, distribution or percentiles, maximum observed elapsed cost, deadline definition, and missed-deadline count. Elapsed callback time includes descheduling and waits; thread CPU time does not. Neither measures the whole host graph's margin. Keep measurement and record storage bounded. An observed maximum is not a mathematical worst-case bound.

## Walkthrough Template

For a publication control, state the ordinary payload, intended release and acquire edge, defective mutation, contending participants, expected diagnostic, and reachability proof. For a prohibited-operation control, state the marked entry, prohibited call, host or module loading context, expected diagnostic, and per-worker coverage. Pair either with a malformed-input or lifetime case checked by a suitable memory instrument. Report subject, detected-control, unrelated-failure-control, and missed-control results separately.

### Example: A Control Record, Not a General Result

For a C++20 owned-block subject, one producer writes `samples[256]` and release-stores `ready`; one consumer acquire-loads `ready`, copies once, and release-stores `returned`. The producer acquire-loads `returned` before reusing `samples`. A control changes only the publication store to relaxed while both arms keep that same reader-to-producer acknowledgment. The build records compiler, target, flags, whether each translation unit is instrumented, and a progress counter showing both participants reached the copy. A TSan diagnostic on the control is evidence that this run can observe that weakened ordinary-payload edge. A clean subject run is still limited to the executed schedule.

For a separate prohibited-operation control, a supported Clang build marks the actual callback and one render worker `[[clang::nonblocking]]`, then calls `malloc` from each control arm. The expected RTSan unsafe-library-call diagnostic must name the reached arm. A bundle-load failure before the callback is an unrelated-failure control result, while a reached control with no diagnostic is a missed-control result. Finally, a harness-owned malformed state stream with an oversized declared length is run under ASan and selected UBSan checks. These are three distinct records; no result is claimed here because the toolchain and host are examples rather than this repository's observed execution.

The [Plant Defects skill](https://github.com/cboone/agent-harness-plugins/tree/main/plugins/plant-defects) has deeper control-design material when installed. This reference is self-contained: a control establishes sensitivity only after it reaches the intended operation and yields its intended diagnostic.

## Sources

- [ThreadSanitizer](https://clang.llvm.org/docs/ThreadSanitizer.html), [AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html), and [UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html)
- [RealtimeSanitizer](https://clang.llvm.org/docs/RealtimeSanitizer.html), [LLVM 20.1.0 RealtimeSanitizer](https://releases.llvm.org/20.1.0/tools/clang/docs/RealtimeSanitizer.html), and [Function Effect Analysis](https://clang.llvm.org/docs/FunctionEffectAnalysis.html)
- [Rust standalone RTSan integration](https://github.com/realtime-sanitizer/rtsan-standalone-rs) and [Loom 0.7.2 limitations](https://docs.rs/loom/0.7.2/loom/#limitations-and-caveats)
- [fosforo TSan ADR](https://github.com/cboone/fosforo/blob/1317e2b752f7f7d44db9bb7745200ca6e59dde83/docs/adr/0016-verify-the-ring-ordering-with-tsan.md), an historical recorded experiment rather than a current run
