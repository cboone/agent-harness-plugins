# Write Real-Time Audio Code Assessment

## Evaluated Revision

Canonical skill at commit `9c9f1e9e3b4f4f740a42b9dd6c323a84628cb16d`, after the worked-example and evaluation-corpus revision. This revision remains at `1.0.0` because the plugin has not yet been released.

## Results

No completed fresh-context evaluation is retained for these cases. Earlier assessor summaries describe intended assessment outcomes, but omit evaluator output, action traces, observed command completions, and evidence links. Treat every row as not executed until a run records those artifacts against the named revision.

| Case       | Selected references                                               | Result     | Assessment and unverified scope                                                                                                                                                                      |
| ---------- | ----------------------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RTAC-001` | Checklist; audio-thread rules; lock-free buffers; memory ordering | Unverified | Reported: rejects concurrent plain copy and selects owned blocks with acknowledgment. Host contract, topology, capacity, overflow, and lifecycle remain unverified.                                  |
| `RTAC-002` | Checklist; memory ordering                                        | Unverified | Reported: accepts relaxed access for the self-contained meter and names missed updates. Target support and later payload changes remain unverified.                                                  |
| `RTAC-006` | Checklist; verifying concurrency                                  | Unverified | Reported: calls the result inconclusive because the subject is uninstrumented and the control passed. Actual contention and other schedules remain unverified.                                       |
| `RTAC-019` | Checklist; parameters and state                                   | Unverified | Reported: identifies `[C, A, B]` for the pinned wrapper and requests a host automation binding. Other revisions and host behavior remain unverified.                                                 |
| `RTAC-023` | Checklist; events and timing                                      | Unverified | Reported: requires VST3 curve reconstruction before smoothing and retained AUv3 ramp state. Units, order, and host behavior remain unverified.                                                       |
| `RTAC-029` | Checklist; audio-thread rules                                     | Unverified | Reported: produces findings only and does not edit, commit, install, or invoke a companion. Buffer contract and ownership remain unverified.                                                         |
| `RTAC-030` | Checklist; audio-thread rules; lock-free buffers; memory ordering | Unverified | Reported: navigates local references and explains a local publication protocol without requiring Plant Defects. Callback and payload contract remain unverified.                                     |
| `RTAC-031` | Checklist; verifying concurrency                                  | Unverified | Reported: classifies the reached RTSan diagnostic as a detected positive control. Other entries, loading modes, and deadline behavior remain unverified.                                             |
| `RTAC-032` | Checklist; verifying concurrency                                  | Unverified | Reported: classifies the reached control without a diagnostic as insufficient sensitivity. Toolchain integration and subject coverage remain unverified.                                             |
| `RTAC-033` | Checklist; verifying concurrency                                  | Unverified | Reported: treats the instrumented, reached TSan control as sensitivity evidence and scopes it from the subject result. Other schedules and lifetime behavior remain unverified.                      |
| `RTAC-034` | Checklist; verifying concurrency                                  | Unverified | Reported: separately recognizes callback, loading, and worker coverage and requests controls for other entries. Reset, active flush, foreign code, and other loading arrangements remain unverified. |
| `RTAC-035` | Checklist; events and timing                                      | Unverified | Reported after fixture correction: accepts reconstruction before smoothing and corrects the expected value at offset 31 to `0.5`. Queue edge cases and unit conversion remain unverified.            |

`RTAC-003` through `RTAC-005`, `RTAC-007` through `RTAC-018`, `RTAC-020` through `RTAC-022`, and `RTAC-024` through `RTAC-028` remain unverified because they were outside this independent sample. The evaluation corpus records their raw inputs and criteria for later runs. Generated Codex and OpenCode layout navigation remains unverified because this corpus contains no retained record of those runs.

## Record Format

For each execution, replace the relevant unverified entry with the case ID, skill revision, harness and model, input variant, selected references, recommendation or produced artifacts, observed command completions, assessment against the criterion, and links to retained evidence.
