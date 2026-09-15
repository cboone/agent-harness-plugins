# Audio-Thread Rules

Use this reference to audit every entry that can run under an audio deadline. The host contract determines the actual requirements; a familiar framework or a main-thread callback does not relax them by itself.

## Budget and Reachability

At 48 kHz, 128 frames span about 2.67 ms. That interval is not a private plugin budget: other graph nodes, scheduling, driver behavior, and the host's safety margin also consume it. Trace setup, process, reset, flush, error paths, destructors, third-party calls, and render workers before calling an operation bounded.

Allocation, freeing, container growth, formatting, logging, reference-counted final destruction, exceptions, lazy initialization, untouched pages, I/O, mutex operations, and a loop that waits for another thread can all violate a callback bound. The cost of undocumented library calls, RTTI, thread-local initialization, and host services must be checked for the selected target and configuration. A successful `try_lock` does not make a later standard-mutex unlock suitable for a callback.

Preallocated scratch is compatible with a bounded design when its capacity, initialization, and reset costs are bounded. The allocator-free core proposed by springer and fosforo's fixed-buffer allocator check are project-specific controls. The latter observes that allocator's state; it does not by itself cover every allocation or free reachable from `process`. Touch storage before processing when page faults matter, and inspect where setup and destruction actually run.

## Buffers and Output

Record buses, channel counts, sample formats, legal in-place pairs, ownership, and pointer lifetimes. Validate count, index, header, and host values before bounded use, but do not claim a length check proves an arbitrary foreign pointer is accessible. Follow the API's failure contract.

CLAP audio ports require 32-bit sample support and make 64-bit support optional. Support unequal input and output counts, select the supplied representation, preserve an aliased input until it is consumed, and write every required output sample, including extra channels and fallback paths. `constant_mask` is a reader hint, so a constant output still needs a complete buffer. Rust code that wraps host buffers must also meet the slice contract: a C ABI's in-place permission does not authorize overlapping incompatible Rust references.

Use the actual block-size rule. CLAP activation negotiates positive minimum and maximum sizes. JUCE preparation supplies an expectation while processing permits varying blocks, including zero samples. Test zero frames only where the API permits it. PortAudio requires filling an output buffer regardless of callback return value, whereas `CLAP_PROCESS_ERROR` asks the host to discard output. Neither outcome is a universal policy.

## Lifecycle and Threads

CLAP's audio thread is symbolic. A host serializes ordinary audio callbacks for an instance but can use different operating-system threads over time, including the main thread. A cached thread ID and a callback-scoped marker are different mechanisms. `[thread-safe]` permits concurrency; it does not establish a deadline. Audit every callback boundary and worker rather than assuming main-thread execution means processing has stopped.

| Entry or phase             | CLAP thread and state                                                        | Required audit                                                                        |
| -------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `activate`                 | Main thread, inactive                                                        | Negotiate bounds and prepare storage that stays fixed while active                    |
| `start_processing`         | Audio thread, active, not processing                                         | Audit reached initialization and move unbounded preparation to an allowed phase       |
| `process`                  | Audio thread, active, processing                                             | Meet buffer, event, ownership, and bounded-work contracts for each supported block    |
| `stop_processing`          | Audio thread, active                                                         | Audit cleanup and final destruction reached here                                      |
| `reset`                    | Audio thread, active                                                         | Preserve reset semantics and bound clearing work as well as allocation                |
| Parameter `flush`          | Audio thread while active; main thread while inactive; serial with `process` | Apply active-path limits and supplied event-list lifetime rules                       |
| State save and load        | Main thread; processing can continue                                         | Use a coherent snapshot or validated handoff instead of assuming exclusive access     |
| Thread-pool `exec`         | Render worker; tasks can run concurrently                                    | Audit worker callees, task-local scratch, communication topology, and instrumentation |
| `deactivate` and `destroy` | Main thread; destruction follows deactivation                                | Establish that processing and separate users stopped before reclaiming storage        |

Reset can miss a deadline by clearing a large preallocated buffer even when it allocates nothing. Bound the chosen storage strategy against the relevant lifecycle contract. CLAP thread-pool `request_exec` is permitted only inside `process`, cannot be nested or concurrent, waits for tasks, and can reject work. Its own documentation warns that synchronization can violate hard real-time requirements. Give rejected or unavailable workers a bounded fallback. Do not share callback scratch with workers, and do not assume a callback-local marker transfers to them.

## Notifications, Diagnostics, and Teardown

Record bounded diagnostic state, then report through an API-permitted service or later non-real-time consumer. Audit enqueueing, payload copies, signaling, and destruction after both success and failure. JUCE `AsyncUpdater::triggerAsyncUpdate` may block while posting a system message despite being thread-safe. Coalesce notifications, specify diagnostic overflow, and avoid retry-until-success behavior when a consumer stalls.

fosforo's render/main-thread arrangement and resize protocol describe that project. They do not prescribe another API's thread model. Stopping a callback source and waiting for existing users are separate lifecycle operations; use the ownership protocol and an allowed waiting thread to establish teardown.

## Numerical Behavior

Recursive tails can enter the subnormal range. Non-finite inputs, overflow, and an earlier non-finite value can also corrupt later internal state. Define bounded detection and recovery for the selected algorithm. On x86, MXCSR has FTZ and DAZ controls; on AArch64, FPCR has separate controls. Save and restore any host-owned floating-point state and verify compiler and architecture behavior. Faust's `-ftz` modes are documented compiler options, not a universal setting or proof about foreign callees.

Test numerical checks with the production floating-point flags. Fast-math assumptions can invalidate non-finite checks. A recovery path should say whether it clears state, clamps a value, bypasses an operation, or emits a bounded diagnostic.

## Worked Callback Audit

| Division | Permitted work                                                                       | Buffer and lifetime contract                                                                              | Failure behavior                                            |
| -------- | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Setup    | Allocate, initialize, touch, and negotiate on the host-permitted thread              | Store fixed capacity, supported layouts, and format-specific bounds                                       | Reject unsupported activation before processing             |
| Process  | Bounded per-block DSP, owned event handling, and bounded publication                 | Inputs remain valid for the callback; outputs are fully initialized; aliases follow the selected strategy | Use the host's bounded error or fallback result             |
| Retire   | Stop sources, wait on an allowed non-audio thread, then reclaim acknowledged storage | No reader may retain a released buffer or replacement                                                     | Preserve a valid old configuration until retirement is safe |

For each supported configuration, exercise legal in-place buffers, unequal channels, constant channels, supported sample formats, variable legal sizes, an oversized block, hidden allocation or final destruction in every real-time entry, thread migration, worker scratch ownership, rejected worker requests, a near-zero recursive tail, and non-finite recovery. These cases establish only their stated host, build, and execution coverage.

### Example: Two Inputs, Three Outputs, and a Worker

This reviewed design supports stereo `f32` input, three `f32` outputs, and blocks from 1 through 256 frames after CLAP activation. During `activate`, it allocates and touches three 256-frame output scratch buffers and one 256-frame scratch buffer per possible render worker. `process` accepts an in-place left channel only after it reads that channel, zeroes the unmatched third output channel, rejects a block larger than 256 with `CLAP_PROCESS_ERROR`, and does not allocate, log, or notify the host.

`reset` clears only the active 256-frame delay window, so its work has a stated 256-sample bound. A rejected worker request processes the same work on the callback only if that fallback also fits the documented bound; otherwise the prepared last-valid result is used. `stop_processing` only marks the instance inactive. `deactivate` runs on the main thread, waits for worker completion, then releases scratch storage. A focused adapter test supplies aliased stereo input, one input with three outputs, a constant channel, a 256-frame block, and a 257-frame block. It establishes buffer and lifecycle behavior for this declared configuration, not other formats or hosts.

## Sources

- [CLAP plugin and lifecycle contract](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/plugin.h)
- [CLAP audio buffers](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/audio-buffer.h) and [audio ports](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/ext/audio-ports.h)
- [CLAP thread check](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/ext/thread-check.h), [thread pool](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/ext/thread-pool.h), [parameters](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/ext/params.h), and [state](https://github.com/free-audio/clap/blob/cd94482ba5941ae410809b6fbaed3bc851044270/include/clap/ext/state.h)
- [JUCE AudioProcessor](https://docs.juce.com/master/classjuce_1_1AudioProcessor.html), [JUCE AsyncUpdater](https://docs.juce.com/master/classjuce_1_1AsyncUpdater.html), and [PortAudio callbacks](https://portaudio.com/docs/v19-doxydocs/portaudio_8h.html)
- [Rust mutable slice construction](https://doc.rust-lang.org/std/slice/fn.from_raw_parts_mut.html), [Faust options](https://faustdoc.grame.fr/manual/options/), and [Faust foreign functions](https://faustdoc.grame.fr/manual/syntax/#foreign-functions)
- [fosforo source at `1317e2b`](https://github.com/cboone/fosforo/tree/1317e2b752f7f7d44db9bb7745200ca6e59dde83) and [springer source at `e76419d`](https://github.com/cboone/springer/tree/e76419dc022cb1690d22c779cfee39dd5f53565d)
