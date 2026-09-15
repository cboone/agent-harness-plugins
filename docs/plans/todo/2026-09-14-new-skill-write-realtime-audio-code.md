# New skill: write-realtime-audio-code

Issue: [#343](https://github.com/cboone/agent-harness-plugins/issues/343)

## Context

Nothing in the catalog covers code reachable from an audio callback, and it is the domain where a reviewer without audio background most reliably gets things wrong: an allocation, a lock, or a relaxed atomic compiles, passes every test, and ships as an intermittent click that does not reproduce under a debugger. fosforo (ADR 0010) and springer (ADR 0007) both carry the same non-negotiable:

> Nothing reachable from the audio thread allocates, locks, or makes a syscall.

The outcome is a `code-quality` plugin, `write-realtime-audio-code`, shaped like `write-go-code` (a short SKILL.md, an essential checklist, seven comprehensive references) but a domain guide rather than a language one, like `write-formalization-roadmap`. The rules follow from the audio thread's scheduling contract, so they hold for Zig, C++, Rust, and Faust alike.

## Approach

**Language-neutral rules, with fosforo and springer as cited worked examples.** Each rule is stated generally; the measured instance comes from the source projects (Zig, CLAP, macOS); and where a mechanism differs by toolchain, the reference names the Zig, C++, Rust, and Faust forms, but only ones verified during planning.

**Apply `plant-defects`; do not duplicate it.** `plant-defects` already carries fosforo's TSan material in generic form: the non-atomic-memory rule, the `Pending` 2x2, and the five-ordering result in `instrument-blindness.md`, control-first judging in `ordered-assertions.md`, and canary mechanics in `source-canaries.md`. `verifying-concurrency.md` states what is specific to audio seams and links to those files by repository path for the method.

**Keep the issue's seven-file structure exactly.** The issue's "other traps" fold into the existing files instead of becoming an eighth: the thread map, denormals, and NaN go in `audio-thread-rules.md`, and parameter smoothing goes in `events-and-timing.md`.

**One scope addition:** the `plant-defects` README says a real-time audio companion is "filed and not yet built". That becomes false when this lands, so that README and the related-plugins line in its SKILL.md get updated, with a patch bump to `1.0.1`.

No bundled scripts, so rule 18, `tests/scrut/`, and the `Makefile`/CI `SCRUT_ENV` lists are untouched.

## Facts verified during planning

These back claims the skill makes beyond what the issue states:

- **CLAP headers** (`free-audio/clap` 1.2.9, via the local `clap-host` clone): `clap_param_info.id` is "Stable parameter identifier, it must never change". `clap_event_header.time` is a "sample offset within the buffer for this event". Input events arrive sorted in sample order, and the plugin must push output events sorted. `state.save`/`load` are `[main-thread]`, `params.flush` is `[active ? audio-thread : main-thread]`, and `host.request_flush` is `[thread-safe,!audio-thread]`. `reset` is `[audio-thread & active]`, and `steady_time` may jump backward across it. `thread-check.h`: the audio thread is _symbolic_. A host may run `process` on different OS threads over time, including the main thread, and guarantees only that no two run at once. A MIDI CC mapped to a parameter should set `CLAP_EVENT_DONT_RECORD`.
- **Thread Sanitizer runtime** (`libtsan/tsan_interface_atomic.cpp`, shipped with Zig 0.16): a relaxed load or store is a plain access with no happens-before edge; an acquire load joins the sync object's clock; a release store publishes into it; `seq_cst` counts as both. The runtime distinguishes orderings for every language, but whether a language's orderings _reach_ it intact is a compiler and standard-library property, measured here only for Zig 0.16 via LLVM. The skill says so and requires a positive control rather than generalizing.
- **Zig 0.16 `AtomicOrder`**: `unordered`, `monotonic`, `acquire`, `release`, `acq_rel`, `seq_cst`. C++: `memory_order_relaxed`, `_acquire`, `_release`, `_seq_cst`. Rust: `Relaxed`, `Acquire`, `Release`, `SeqCst`.
- **RealtimeSanitizer**: Clang 20+, `-fsanitize=realtime` plus `[[clang::nonblocking]]` on the real-time entry point, with the compile-time Function Effect Analysis sharing that attribute, and `rtsan-standalone` for Rust. It is dynamic, so it sees only paths a run reaches.
- **Faust**: `-ftz <n>` / `--flush-to-zero` adds flush-to-zero code to recursive signals (0 none, 1 fabs-based, 2 mask-based), for targets such as WebAssembly with no hardware mode.
- **Sources**: Ross Bencina, "Real-time audio programming 101: time waits for nothing" (5 July 2011). Timur Doumler, "Using Locks in Real-Time Audio Processing, Safely" (ADC 2020). Dave Rowland and Fabian Renn-Giles, "Real-time 101", parts I and II (ADC 2019).

## Files

### `plugins/write-realtime-audio-code/.claude-plugin/plugin.json`

Alphabetized fields matching `write-go-code`: `"version": "1.0.0"`, `"skills": "./skills"`, MIT, author, homepage, repository. Keywords: `["audio", "clap", "dsp", "lock-free", "real-time"]`.

Canonical description, 154 characters, which fits the root README's existing 154-character column so Prettier does not repad the table:

> Style guide for code reachable from an audio callback: the audio thread's contract, lock-free seams and memory orderings, and identifiers a host persists.

The same string appears verbatim in the marketplace entry, as the first paragraph of the plugin README, and in the root README row.

### `skills/write-realtime-audio-code/SKILL.md`

Frontmatter holds `name` and a folded `description`, which must stay under 1024 characters and follows the house shape: what the skill is; "Use whenever real-time audio code is the subject of the work, not only when editing: (1) writing or reviewing a process or render callback or anything it calls, (2) passing data between the audio thread and a GUI, render, or main thread, (3) choosing or reviewing an atomic ordering, ring buffer, or other lock-free structure, (4) verifying a cross-thread ordering or the no-allocation rule with a sanitizer or source canary, (5) defining parameters, plugin identifiers, or saved state for CLAP, VST3, or Audio Units, (6) handling sample-accurate events, parameter smoothing, denormals, or NaN in recursive state, (7) keeping a DSP or musical core free of host types"; then a `Covers ...` sentence.

Body sections:

- **Title and the core rule** as a block quote, attributed to both projects' ADRs.
- **When to Use.** The positive signals above. Do not use it for offline rendering with no deadline (unless that code is shared with the real-time path, which makes it reachable), for filter design or DSP mathematics, or for GUI toolkit conventions.
- **Core Principles**, seven:
  1. A missed deadline is an audible click, not a slow frame, so ask about worst case, not average.
  1. "Reachable" means the call graph, not the function body.
  1. What must happen and cannot happen on the audio thread is handed across a seam.
  1. Say which ordering, and why, at both ends of every atomic pair.
  1. A single-threaded suite cannot see an ordering, so verify by instrument with a control that must fail.
  1. What a host persists is permanent.
  1. Keep the core pure, and enforce the seam with a compile error rather than a review.
- **Know Which Thread Calls You.** A compact table of CLAP's thread annotations, the symbolic-audio-thread trap, and the convention of doc-commenting every function with its thread (`[audio-thread & active & processing]`, `[main-thread]`, `[render-thread]`, `[thread-safe]`), as fosforo does throughout.
- **Workflow**, five steps:
  1. Map the thread for each function touched.
  1. Review against the checklist.
  1. For a cross-thread mechanism, read `lock-free-buffers.md` and `memory-ordering.md`.
  1. Verify with `verifying-concurrency.md`, using the `plant-defects` skill for the method.
  1. For parameters, identifiers, or state, read `parameters-and-state.md` before the first release, since the mistakes there cannot be undone afterward.
- **Reference Navigation**, spelled `./references/...` so rule 19 resolves each path.
- **Sources**: fosforo ADRs 0005, 0010, 0016, and 0018, `src/dsp/ring.zig`, `src/clap/gate.zig`, `src/ring_race.zig`, `src/gate_race.zig`, `src/canary.zig`, `src/clap/state.zig`, `src/gpu/iface.zig`, `docs/notes/concurrency-and-canaries.md`, and the build plan's identifiers section. springer ADRs 0005, 0007, 0008, and 0013 and its build plan. Then the CLAP spec (`clap/ext/thread-check.h` in particular), compiler-rt's `tsan_interface_atomic.cpp`, Clang's RealtimeSanitizer docs, Bencina, Doumler, and Rowland and Renn-Giles.

### `references/essential/checklist.md`

Checkbox rules in `write-go-code`'s format, a line each with a short example where one clarifies. Sections: the audio thread's contract, the thread map, crossing the seam, memory orderings, verification, parameters and identifiers, state, events and timing, numerics (denormals and NaN), and the pure core.

### `references/comprehensive/audio-thread-rules.md`

- **Why.** Deadline arithmetic, a runtime fact: 128 samples at 48 kHz is about 2.67 ms per block. Memory safety is not real-time safety; the failure is intermittent, load-dependent, and invisible under a debugger (springer ADR 0007).
- **The forbidden list, including where each item hides**: allocation and free (container growth, string formatting, type-erased callables, exceptions, the last owner of a reference-counted pointer freeing on the audio thread), locks (priority inversion; an uncontended `unlock` can still wake a waiter through the kernel), syscalls, file I/O, logging and `printf`, `dynamic_cast`, page faults on first touch of fresh memory, lazy thread-local initialization in a `dlopen`-ed library on glibc, garbage collection, unbounded loops, and retry loops that spin on another thread's progress.
- **Enforce it structurally rather than by discipline.** Two measured shapes: hand the audio path no allocator at all, so "does this allocate" is a question about the call graph (springer); or hand it a fixed-buffer allocator sized at `activate` and assert it is untouched after `process` (fosforo). The C++ and Rust counterparts are RealtimeSanitizer, Function Effect Analysis, and `rtsan-standalone`, each needing a planted allocation as its positive control.
- **Refuse, do not assert, at the host trust boundary.** A `frames_count` above the negotiated maximum returns an error, because an assertion is compiled out of exactly the build where a misbehaving host does damage.
- **Capacity bounded by construction and derived in one place.** springer's 256 scheduler entries, with a defined overflow policy: drop the newest, because the oldest pending events include note-offs, and dropping one leaves a note hanging.
- **Diagnostics set state; a thread that may block reports it later** (`request_callback` then `on_main_thread`, then `clap.log`). `[thread-safe]` is not real-time safe.
- **Know which thread calls you.** CLAP's symbolic threads, in detail. A thread-local "am I the audio thread" check is wrong because the audio thread is not one OS thread. `[audio-thread]` functions never run concurrently with each other, but `[thread-safe]` ones may. The render thread touches the GPU only and marshals UI mutations to the main thread. Resize is the one seam that cannot be fully lock-free: a pending flag serviced at the top of the render tick (fosforo ADR 0010). Stopping a callback source does not promise no callback is in flight, which is why fosforo has its teardown gate.
- **Denormals.** They arise in feedback paths decaying toward zero: IIR filters, reverb and delay feedback, release tails. Set flush-to-zero and denormals-are-zero (MXCSR on x86, FPCR on AArch64) at the top of each callback with a scoped guard that restores the previous state, because the control register is per thread and the host owns the thread. Where no hardware mode exists, use a software fix such as Faust's `-ftz 2`. The penalty is microarchitecture-specific, so measure rather than assume a target is immune. Fast-math can fold away the check that would detect a denormal.
- **NaN and infinity in recursive state are permanent.** `NaN * decay` is NaN forever (fosforo's accumulation texture; the same holds for filter state), so sanitize at the boundary, and do it in code fast-math cannot fold away.

### `references/comprehensive/lock-free-buffers.md`

- **Decide by what the consumer needs.** Choose "every item exactly once" (a queue: notes, parameter changes, anything that must not be lost) or "the most recent window" (a history ring: a scope, a meter, an analyzer). A queue for a display adds backpressure nobody asked for; a ring for events loses messages. fosforo ADR 0010 is the worked case.
- **Say how many producers and consumers, and enforce it.** A single producer may read its own cursor unsynchronized, which is exactly why a second producer silently loses samples. A many-to-one structure needs compare-and-swap and has failure modes, ABA among them, that a single-producer, single-consumer design never meets.
- **State the protocol completely in the module header.** Write, then publish once per block with release semantics; acquire-load, then read a trailing window.
- **Cursor mechanics.** The cursor is a monotonic 64-bit sample count rather than a wrapped index, so a reader can tell "lapped twice" from "not moved". Capacity is a power of two, so the wrap is a mask, and the container reports the rounded capacity. Storage is allocated and zeroed once at `activate` and never resized. The container is total: a write longer than the capacity keeps its newest samples and still advances by the whole input.
- **Torn reads.** Either prevent them (a seqlock retry) or tolerate and report them. A display tolerates: `coherent(snapshot, now, capacity, copied)` says whether the producer overran the window during the copy, and the consumer skips the frame instead of retrying on the audio thread's heels. The margin argument is a capacity of about a second against windows of tens of milliseconds.
- **Clear through the write path**, never a memset behind a published cursor, which a coherence check is structurally unable to report (fosforo's `Ring.clear`).
- **Event scheduling across blocks.** A fixed-capacity ring of events with absolute sample timestamps (springer's scheduler).
- **The one-word message** (fosforo's `Pending`). A whole update packed into one atomic integer is the cheapest seam there is, and it stops being that the moment a field rides alongside it.
- **Handing over objects.** Build a complete immutable replacement off the audio thread, swap it in, and retire the old one to a thread that may free it. Never free on the audio thread (Doumler, ADC 2020).
- **Lifecycle seams.** fosforo's teardown gate: one word carries both the closed flag and the count of ticks inside it, so entering claims a place and learns whether the gate is open in a single atomic operation. `close` spins, bounded by one tick. A mutex here would reintroduce a check-then-enter window, and its contended path is an unbounded wait the host's main thread could enter.

### `references/comprehensive/memory-ordering.md`

- **The orderings across Zig, C++, and Rust**, as a table using the verified names.
- **The pairing.** A release store publishes; an acquire load observes everything published before it. State the pair in a comment at both sites, naming what catches a weakening (fosforo's `ring.zig` pattern).
- **What relaxed is for.** The sole writer reading its own value, which is the one relaxed load in `Ring.write`. Anywhere else it buys nothing at runtime: on x86-64 and AArch64, loads and stores compile to the same instructions whatever the ordering (disassemble to confirm on your target), so relaxing changes only what a sanitizer or optimizer is told. It is a weakening that compiles and passes every single-threaded test.
- **`seq_cst` is both acquire and release** in the sanitizer's model and is C++'s default. It is not wrong, but it hides intent, so choose deliberately.
- **Check-then-act across two atomic operations is a race** even when each is ordered correctly. Do both in one operation: the teardown gate's `fetchAdd`, then its flag test, undone on refusal.
- **Statement order matters too.** Two individually correct statements in the wrong order are a defect counting cannot see: fosforo's renderer `Mailbox` and its `canary.statedBefore` check.
- **Publish once per block**, not once per sample.
- **The language caveat** from the verified facts above.

### `references/comprehensive/verifying-concurrency.md`

This is `plant-defects` applied to memory ordering. Each section links the matching `plugins/plant-defects/skills/plant-defects/references/*.md` for the general method.

- **A single-threaded suite cannot observe an ordering.** All 139 of `ring.zig`'s tests passed with the release store weakened to `.monotonic`.
- **A stress test measures the hardware and the day, not the code.** A weakened store's visibility window is nanoseconds, and drawing the trace cannot tell. With both halves weakened, the harness's own validation passed 4096 windows with none torn; only the sanitizer noticed.
- **The Thread Sanitizer model.** It builds a happens-before graph and reports two threads reaching one address with no edge between them. Its verdict is a property of the code.
- **The rule that decides whether an arm can exist:** TSan discriminates an ordering only where that ordering guards non-atomic memory. Ask "what plain memory does its release make safe to touch". Hence the payload harness (fosforo's `[]u64` standing in for the editor's fields), the 2x2 that proves a clean result is a fact about the subject's shape, and a source canary for one-word messages.
- **Two arms, control first.** Judge the weakened arm before reading the subject, with a progress counter proving the threads met (`scripts/race-check`).
- **Control-faithfulness hazards**, each measured:
  - Thread creation is itself an edge, so write the payload after spawning.
  - `join` is an edge, so write before joining.
  - The rendezvous flag must stay relaxed on both sides, because a release-acquire pair there supplies the very edge under test.
  - The instrument's own cost changes timing: fosforo's weakened control stopped contending until the holder was made to hold, after which both arms contended in all 256 rounds, 0.17% apart.
  - The replica must differ from the real type in exactly one ordering.
- **Plant in the real type, not only the replica.** Of five orderings planted in the gate, two flag, and the filing issue had named one of the three that do not. Planting also found a harness gap: a per-iteration `written()` acquire load made the harness blind to a weakened acquire in `read`.
- **Bound the writer** so the tolerated torn path produces no real reports: at most `capacity - window` samples over the whole run. A ratio does not work, because a descheduled reader breaks any ratio.
- **State what is and is not verified**: the non-lapping path only, with this compiler, on this target.
- **Toolchain traps that pass silently.**
  - Zig 0.16's self-hosted x86-64 backend links the TSan runtime and emits no instrumentation (`use_llvm = true` fixes it).
  - A `-fsanitize-thread` binary on `aarch64-macos` segfaults before `main`, so the check runs on Linux CI.
  - The module under test must depend on nothing platform-bound, and so must the build script, because dependency build functions run at configure time.
  - The general rule: confirm instrumentation by disassembly rather than by the flags you passed.
- **Source canaries** as the faster guard on the development machine: a text assertion that proves nothing about behavior. Pin every atomic operation in a guarded file and count all of them.
- **The no-allocation rule's instruments**: RealtimeSanitizer and its positive control, and the structural Zig shapes. **Seam checks**: plant the forbidden import and confirm the build goes red (springer ADR 0005).

### `references/comprehensive/parameters-and-state.md`

- **Stable ids, never index or name.** CLAP's `clap_id`, VST3's `ParamID`, and Audio Unit parameter ids. Assign each once, in an enum doc-commented as permanent; never reuse, renumber, or derive ids from position; number groups with gaps. Scripter is the cautionary tale: binding automation to index froze the parameter order (springer ADR 0008).
- **Display order is separate from ids, and AUv2 ordering is a separate problem.** Logic presents parameters in reported order, so implement clap-wrapper's `clap.plugin-auv2-param-ordering` from the start. Under stable ids a deferred parameter costs nothing (springer ADR 0013).
- **Checks**: a source canary over the id enum, plus a by-hand confirmation that an automation lane still binds after a rebuild.
- **Identifiers in three tiers** (fosforo's build plan):
  - Permanent: the CLAP `id`, the AU type, subtype, and manufacturer codes, and VST3 class ids.
  - Sticky: the bundle identifier (signing and preferences).
  - Free: the display name, and the manufacturer name (with its `Vendor: Product` shape caveat).
  - Keep the table in the build plan and doc-comment each value at its declaration.
  - A field that looks cosmetic can be identity: clap-wrapper derives the AU type from CLAP `features[0]`.
  - Do not namespace identity per worktree; stamp build provenance into the version string, which no host persists (fosforo ADR 0018).
- **Versioned state from the first release, even with nothing to persist** (fosforo `state.zig`):
  - A magic number and a version, with explicit endianness.
  - Growth by appending, with the reader tolerating trailing bytes.
  - A version bump only when a field changes meaning or disappears, and a newer version refused cleanly rather than misread.
  - A failed load leaves the instance unchanged.
  - Save and load run on the main thread, so loaded values reach the audio thread across the seam.
- **Plugin-initiated parameter changes**: an output parameter event plus `request_flush`. A MIDI CC mapped to a parameter sets `CLAP_EVENT_DONT_RECORD`.

### `references/comprehensive/events-and-timing.md`

- **Events carry a sample offset within the block.** Split the block at each offset. Applying events at block boundaries quantizes them to the buffer size, which is invisible at a 64-sample development buffer and audible at the large buffers people mix at: 1024 samples at 48 kHz is about 21.3 ms of error. Test at the negotiated maximum block size with an event on the last frame.
- **Output events must be pushed sorted.**
- **Schedule across blocks with absolute sample timestamps.** A strummed chord's note-offs carry the same offsets as their note-ons, or the upper voice is released before it is struck and hangs.
- **Note matching.** Prefer the host's `note_id` and fall back to channel and key when it is `-1`. The note-off path consults the voice table first, and `reset` and `deactivate` release everything.
- **Transport and reset.** A beat-based gate is disabled while the transport is stopped, and a negative elapsed value means a loop jump. `reset` may move `steady_time` backward, so rebuild derived state rather than advancing it.
- **Parameter smoothing.** An unsmoothed gain step is a discontinuity in the waveform, heard as a click. Ramp toward the target per sample, starting at the event's offset. Derive coefficients from the sample rate at `activate`. Snap rather than glide on `activate`, `reset`, and state load. Do not interpolate stepped or enumerated parameters; crossfade between their results instead.
- **Take time from sample counts, not wall clocks**, and validate host-supplied values at the boundary.

### `references/comprehensive/the-pure-core-seam.md`

- **Three layers with the dependency arrow pointing one way** (springer ADR 0005). The core takes numbers and returns numbers; the engine knows sample offsets, note ids, and event ordering; only the host adapter names a host type.
- **Enforce it with a compile error, in either of two forms.**
  - An import assertion: nothing under the core may import the host bindings. springer has decided this in ADR 0005 but not yet built it.
  - A signature assertion: every backend function's type is checked against the seam's own vocabulary, so a leaked Metal type stops compiling. fosforo's `src/gpu/iface.zig` does this.
  - Counterparts elsewhere: a Rust core crate that does not depend on the plugin API crate, a C++ core library target built without the SDK's include path, and Faust, which is pure by construction and keeps its host glue separate.
  - Plant the forbidden import to prove the check can fail.
- **Why it pays.** The core is testable with no host, and a reference implementation becomes the strongest instrument available: springer runs its original Scripter script under Node to generate expected output vectors. Pure arithmetic, such as `coherent`, can be tested exactly instead of by racing threads.
- **Load-bearing with one backend.** It costs almost nothing now; design for the port, and do not build the port (fosforo ADR 0005). Pass configuration as arguments rather than reading parameters from inside the core.
- **Porting hazard: division semantics differ by language.** JavaScript's `Math.floor` floors while Zig's `/` truncates, so negative scale degrees need `@divFloor` and `@mod`, plus a canary for the negative case.
- **Keep shared containers free of both producer and consumer.** `ring.zig` imports only `std`, which is what let it be built for Linux and raced there.

### `plugins/write-realtime-audio-code/README.md`

The sibling template, in order: title; the description verbatim; `**Type:** Skill`; `**Trigger:** /write-realtime-audio-code (also activates automatically)`; Installation, pointing to `../../README.md#install`; What It Does; Usage; Examples; See Also, linking Plant Defects and All plugins. No Requirements section, since the skill runs no command.

### Catalog registration

- `.claude-plugin/marketplace.json`: a new entry between `write-pandoc-markdown` and `write-scrut-tests` with `"category": "code-quality"`. Recompute `metadata.version` with `bin/compute-catalog-state`. It is `catalog-M70-m103-p156-n57` now, and the expected end state after both plugin changes is `catalog-M71-m103-p157-n58`, to be confirmed from the script rather than assumed.
- Root `README.md`: a `Write Real-Time Audio Code` row between `Write Lean Tests` and `Write Scrut Tests`. No External tools bullet. `## Contents` is left alone.
- Run `bin/build-codex-marketplace` and `bin/build-opencode-mirror`, and commit both trees, including the new `dist/opencode/skills/` symlink.

### `plant-defects` companion update (1.0.0 to 1.0.1)

- `plugins/plant-defects/README.md`: replace the "filed and not yet built" sentence so it links the real-time audio skill and keeps the CI-audit companion as filed, and add a See Also link.
- `plugins/plant-defects/skills/plant-defects/SKILL.md`: add `write-realtime-audio-code` to the related-plugins sentence.
- Bump the version in `plugin.json` and the marketplace entry, then recompute catalog state and regenerate both mirrors.

## Corrections to the issue body

| Issue says                                                                                                         | Actually                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| springer's ADR 0005 "puts a comptime assertion in `src/music/`"                                                    | ADR 0005 decides it. springer's `main` has no `src/` yet, and the build plan names `src/music/scale.zig` as its future home. The skill describes it as a decision                                                                                          |
| ADR 0005 calls it "the seam that makes most of the plugin testable without a host"                                 | That wording is in springer's build plan, not the ADR: "the load-bearing seam and the reason most of this plugin is testable without a host"                                                                                                               |
| Both projects identify parameters by stable id                                                                     | Only springer does (ADR 0008). fosforo has no parameters, and states the permanence of its plugin `id` and AU triple instead                                                                                                                               |
| Both projects keep an "Identifiers, which are permanent" table                                                     | springer's has that title. fosforo's is "Identifiers: what is permanent and what is not", with three tiers (permanent, sticky, free), which the skill adopts as the more useful structure                                                                  |
| fosforo's renderer seam is stated                                                                                  | It is also mechanized: a comptime block in `src/gpu/iface.zig` asserts every backend signature against the seam's vocabulary. That is a different mechanism from springer's import assertion, and the skill teaches both                                  |
| "Timur Doumler's talks"                                                                                            | Doumler's relevant talk is "Using Locks in Real-Time Audio Processing, Safely" (ADC 2020). "Real-time 101" is by Dave Rowland and Fabian Renn-Giles (ADC 2019). Both are cited, attributed correctly                                                       |
| A relaxed load "usually buys nothing you wanted"                                                                   | That holds, with the exception the skill must state: a relaxed load is correct for the sole writer reading its own value, which is what `Ring.write` does                                                                                                   |
| TSan findings framed generally                                                                                     | They were measured with Zig 0.16 via LLVM only. The runtime distinguishes orderings in every language, but whether a language's orderings reach it is not established here                                                                                  |

These measurements from the issue check out against the ADRs and source: five gate orderings planted with two flagging, the filing issue naming a clean one (`enter`'s acquire), the `[]u64` payload, the `Pending` 2x2, and all 139 ring tests passing with the store weakened.

## Cross-reference hazards

Rule 19 scans `SKILL.md` and everything under `references/`.

- Do **not** add `<!-- validate-plugins: repository-paths -->`. Without it, the `docs/` and `bin/` paths quoted from fosforo and springer are skipped rather than resolved against this repository. `src/` and `scripts/` are in no prefix list.
- `plugins/plant-defects/skills/plant-defects/references/*.md` paths resolve against the repository root, so each one linked must exist.
- Put a backticked name next to the word "skill" only for plugins that exist (`plant-defects`). The unbuilt audio siblings (`scaffold-clap-audio-plugin`, `set-up-clap-validation`) are not mentioned that way.
- Avoid backticked single-segment absolute paths, which the checker reads as skill names.
- Keep every relative link in the READMEs resolvable, fragments included.

## Verification

```bash
yarn install --immutable
bin/check-cross-references plugins/write-realtime-audio-code/skills/write-realtime-audio-code/SKILL.md
make format
make build
make validate
make test-all
git status --porcelain dist/ .agents/
```

`make validate` is the gate that matters here. Rule 10 checks catalog state, rules 15 and 16 check mirror freshness, rule 17 enforces the 1024-character canonical description limit (and warns above 320 on the Codex copy), and rule 19 resolves cross-references. After a clean run, use the `check-versions` skill, then run the `plugin-dev:skill-reviewer` agent on the finished skill for trigger quality and progressive disclosure.

A manual pass follows, since the prose is the product:

- `grep` the new files for em dashes.
- Confirm there are no time or effort estimates. Runtime figures such as block durations are fine.
- Check neutral terminology. Audio jargon collides with it: write "main bus", not "master bus", and "release all voices", not CLAP's own "kills all voices".
- Re-check every quoted number against its source file.

## Commits

1. `docs: add plan for the write-realtime-audio-code skill (#343)`
1. `feat: add write-realtime-audio-code skill plugin (#343)`, containing the plugin directory alone
1. `feat: register write-realtime-audio-code in the marketplace catalog (#343)`, containing the marketplace entry, the root README row, recomputed catalog state, and both generated trees
1. `docs: link plant-defects to its real-time audio companion (#343)`, containing the `plant-defects` text, the patch bump, catalog state, and regenerated trees
