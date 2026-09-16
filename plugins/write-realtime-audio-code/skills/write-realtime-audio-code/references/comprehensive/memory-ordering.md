# Memory Ordering

Atomic ordering follows a protocol. First identify the ordinary or atomic payload, the publication that makes it available, the observation that authorizes access, and the reverse edge that authorizes storage reuse. An acquire and release placed somewhere in the same program are insufficient unless the language's synchronization rules connect them.

| Purpose                                              | Zig 0.16    | C++                    | Rust      |
| ---------------------------------------------------- | ----------- | ---------------------- | --------- |
| Atomic access without cross-location synchronization | `monotonic` | `memory_order_relaxed` | `Relaxed` |
| Acquire                                              | `acquire`   | `memory_order_acquire` | `Acquire` |
| Release                                              | `release`   | `memory_order_release` | `Release` |
| Acquire and release on an eligible operation         | `acq_rel`   | `memory_order_acq_rel` | `AcqRel`  |
| Sequential consistency                               | `seq_cst`   | `memory_order_seq_cst` | `SeqCst`  |

Zig's `unordered` is a separate Zig ordering. Do not call it another spelling of C++ or Rust relaxed ordering.

## Object Validity Comes First

Name the C++ edition, Rust toolchain and documented model, or Zig toolchain and target used by an example. A link to the current C++ draft does not make an older edition or Rust follow every draft rule. Ordering does not establish object lifetime, alignment, aliasing, or reference validity. In particular, publication does not make overlapping incompatible Rust references valid or extend a host buffer's lifetime.

Sequential consistency is operation-specific: a load has acquire semantics, a store has release semantics, and an RMW can have both, alongside additional sequential-consistency rules. Check legal orderings for loads, stores, RMWs, and compare-exchange success and failure paths in the selected language documentation.

## Worked Protocols

### Relaxed Self-Contained Meter

An atomic peak meter that stores only the current numeric value can use relaxed load and store when no ordinary payload or ordering depends on that value. The documented result may overwrite an unread peak; that is a product decision. Adding an ordinary timestamp or pointer creates a new publication protocol.

### Payload Publication

For a fixed owned block, the producer writes the block, then release-stores its index. The consumer acquire-loads the index and reads that block only after observing the published index. The consumer release-publishes an acknowledgment after it finishes. The producer acquire-observes the acknowledgment before overwriting the block. Explain which index values mean each state and how wraparound remains unambiguous.

### SPSC Reuse

An owner-local read of its own cursor can be relaxed when the protocol permits it. The other participant still needs the publication and reuse synchronization. Correct individual operations do not make arbitrary check-then-act transitions indivisible. Use an RMW, ownership state, or larger mechanism only for the transition that actually needs it, and bound retry behavior if a failed operation retries.

### Example: Rust `AtomicU8` Slot States

This example uses Rust 1.86 and a target with `AtomicU8` support, exactly one producer, and exactly one consumer. Three fixed `[f32; 256]` slots have an atomic state: `0` is producer-owned, `1` is consumer-owned, and `2` is returned. The producer writes samples only while state is `0`, then release-stores `1`. The consumer acquire-loads `1` before reading, copies the array, and release-stores `2`. After an acquire load observes `2`, the sole producer calls `state.store(0, Ordering::Relaxed)` and only then overwrites the slot. The acquire load synchronizes with the consumer's return; the relaxed store records the producer-owned state without publishing payload. The consumer must not access the slot again until it acquire-observes a new release-stored `1`. Each slot's state is separate, so no wrapping cursor interpretation is needed.

A peak meter is separate and requires a target that provides `AtomicU32` with Rust's lock-free guarantee; `AtomicU8` support alone does not establish that requirement. On such a target, `AtomicU32` stores `f32::to_bits()` with `Relaxed`, and the UI can miss intermediate peaks because its value publishes no ordinary payload. The slot states cannot use that rule because they authorize ordinary-array access. The example assumes the slot array outlives both participants and that no references to a slot escape the consumer's copy. It establishes the stated ownership edges, not wait-free callback completion or a proof for another language.

## Implementation Evidence

AArch64 commonly maps relaxed loads and stores to `LDR` and `STR`, and acquire or release operations to `LDAR` and `STLR`. x86 also has operation-specific behavior, including for sequentially consistent stores. Inspect disassembly to understand a selected compiler and target. It is not a reason to weaken a language-level proof.

Comment the invariant and each participant's obligations, not just an ordering enum. Batch publication where semantics permit, while accounting for unpublished work. A source-order canary can preserve a reviewed structure but cannot prove its invariant.

## Sources

- [C++ data races and memory location rules](https://eel.is/c++draft/intro.races)
- [Rust atomic module](https://doc.rust-lang.org/std/sync/atomic/index.html) and [Rust orderings](https://doc.rust-lang.org/core/sync/atomic/enum.Ordering.html)
- [Zig 0.16 documentation](https://ziglang.org/documentation/0.16.0/)
- [C and C++ atomic processor mappings](https://www.cl.cam.ac.uk/~pes20/cpp/cpp0xmappings.html)
