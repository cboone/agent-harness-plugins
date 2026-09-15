# Lock-Free Buffers

Start with a protocol contract, not an atomic type: producer and consumer counts, owner of every storage location, publication and reuse points, capacity, maximum callback work, overflow rule, reclamation thread, and stalled-participant behavior. FIFO delivery of admitted events and latest-value or snapshot semantics are distinct products. A finite queue cannot guarantee lossless delivery under unlimited offered load.

## Legal Snapshots

A display may skip a frame, but a post-copy cursor check does not make a concurrent plain-data copy legal in C++ or Rust. A second cursor check and a larger history buffer can reduce visible tearing; neither repairs the data race or covers writes in progress after the last publication. A conventional plain-payload seqlock is therefore not portable C++ or Rust code.

Use one of these protocols instead:

- Transfer owned fixed blocks through a bounded SPSC channel.
- Protect double or triple buffers with an ownership state and a consumer-to-producer reuse acknowledgment.
- Use an atomic payload only after proving its coherence, ordering, target support, and capacity rules.

fosforo's [history ring](https://github.com/cboone/fosforo/blob/1317e2b752f7f7d44db9bb7745200ca6e59dde83/src/dsp/ring.zig) records an acknowledged lapping limitation. Its post-copy `coherent` predicate is a display decision under its assumptions, not a portable proof that sample access is race-free. Do not exclude a production-reachable race to obtain a clean experiment.

## Recommended Owned-Block Transfer

The following SPSC state table describes one bounded transfer. It requires one producer and one consumer. A worker turning into an extra producer invalidates that premise.

| State       | Owner    | Producer action                        | Consumer action                | Synchronization and full behavior                                               |
| ----------- | -------- | -------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------- |
| `free`      | Producer | Fill one block                         | None                           | Reuse only after consumer acknowledgment                                        |
| `published` | Consumer | Release-publish the block index        | Acquire-observe the index      | If no `free` block exists, apply the documented drop, coalesce, or defer policy |
| `consuming` | Consumer | Do not overwrite                       | Read the block                 | Work is bounded by the block's fixed capacity                                   |
| `returned`  | Producer | Acquire the acknowledgment, then reuse | Release-publish acknowledgment | The acknowledgment is the reverse edge that authorizes reuse                    |

Bound drain batches. “Drain until empty” can be unbounded when a concurrent producer continues publishing. Derive capacity from product requirements, report rounding, define writes larger than capacity, and route reset or clear through a valid ownership transition. Overwriting a published payload behind a cursor is not a clear operation without ownership or atomic access.

## Progress, Topology, and Costs

Lock-free describes system-wide progress. It does not promise a fixed number of steps for one callback. Standard Rust atomic types are available and lock-free, but a particular operation can still retry. For C++ and other APIs, check width, alignment, and target guarantees. State counter-wrap arithmetic, capacity assumptions, stale-handle behavior, and any ABA-related risk. SPSC is a topology constraint, not a proof that those concerns disappear.

A bounded enqueue is not the whole submission path. Audit payload construction, copy or move, success notification, rejected-payload destruction, and last-reference release separately. A render worker can turn an apparent SPSC route into multi-producer traffic. If preparation is late or a consumer stalls, keep the last valid configuration or follow the documented product policy without making callback progress depend on background progress.

## Events and Immutable Replacements

When accepting an event creates a future termination or cancellation obligation, reserve room for that obligation or reject the start before it is emitted. Dropping the newest event can discard a note-off. A planned 256-entry scheduler in springer is a project choice, not a portable capacity or proven overload policy. On an output `try_push` failure, retain the obligation for the next valid opportunity without unbounded retrying.

Prepare immutable replacements away from the callback. A pointer swap alone does not provide safe reclamation. Define reader acknowledgment, bound the retirement backlog, and defer new off-thread updates when retirement capacity is exhausted. Reference counting requires special scrutiny because a rejected operation or pointer replacement can run final destruction on the callback.

fosforo's [combined close flag and active count](https://github.com/cboone/fosforo/blob/1317e2b752f7f7d44db9bb7745200ca6e59dde83/src/clap/gate.zig) are one teardown protocol. Its closing loop spins and yields on the closing thread; completion depends on participants being scheduled and exiting. Keep that wait outside an audio callback. A mutex does not inherently create a check-then-enter race: define the state transition and the permitted waiting thread for the selected critical section.

## Review Cases

Validate block reuse, overwrite attempts, a stalled consumer, bounded drain batches, retirement exhaustion, notification cost, and payload destruction after rejected enqueue. Report the protocol's producer and consumer topology, all full-capacity behavior, and any unverified target-specific atomic guarantee.

### Example: Three Display Blocks

One callback producer and one UI consumer own three fixed 256-sample blocks. The producer fills a `free` block, release-publishes its index, and never touches it again until it acquire-observes the consumer's returned index. The consumer acquire-observes one published index, copies at most 256 samples, then release-publishes that index as returned. The producer examines at most one returned index and publishes at most one block per callback.

When all blocks are consumer-owned, the callback increments an atomic dropped-frame counter and retains the previously published display value. It neither retries nor posts a notification. The UI polls the counter. A test trace holds all three blocks, verifies that a fourth callback does not overwrite one, returns a block, and verifies that only the returned block becomes reusable. This establishes the stated SPSC transfer and bounded overflow policy; a worker producer or a reference-counted payload would require a different protocol and cost audit.

## Sources

- [fosforo history ring](https://github.com/cboone/fosforo/blob/1317e2b752f7f7d44db9bb7745200ca6e59dde83/src/dsp/ring.zig) and [gate protocol](https://github.com/cboone/fosforo/blob/1317e2b752f7f7d44db9bb7745200ca6e59dde83/src/clap/gate.zig)
- [Rust atomic module](https://doc.rust-lang.org/std/sync/atomic/index.html)
- [Timur Doumler, "Using locks in real-time audio processing, safely"](https://timur.audio/using-locks-in-real-time-audio-processing-safely)
