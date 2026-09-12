# Structural Uncoverability

Code that no test binary compiles is not uncovered. It is absent from the program the tools analyzed, which is why nothing reports it.

## Four failure classes

| Class                     | Shape                                                                                    | How it is found                                                 |
| ------------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| False negative            | A defect one instrument cannot see                                                       | Plant it and watch the instrument stay green; name a second one |
| False positive            | Nothing was broken and a required check said something was                               | The check fails on an unmodified tree                           |
| Structural uncoverability | Code no test binary compiles, so it is not in the analyzed program                       | Plant a defect in it and watch the whole suite pass             |
| Unvisited branch          | It compiles, an instrument could reach it, and no arm was ever written to steer it there | Plant a defect in it and watch the whole suite pass             |

The first is closed by adding an instrument. The second is closed by fixing the check. The third and fourth are closed by changing what the test build contains or where its arms go, and neither is closed by writing more tests of the kind already there.

Note that the third and fourth are found the same way and are not the same thing. Distinguishing them takes one extra step: check whether the code is in the binary at all.

## The measured case

A file watcher was written as two alternative types selected at compile time:

```zig
const Watcher = if (shader.live) struct { ... } else struct { ... };
// where: shader.live = builtin.mode == .Debug and !builtin.is_test
```

A test binary is a debug build with the test flag set, so it takes the stub. The real `poll` was not merely untested: it was **not compiled**, and no test written in that suite could have reached it however it was written.

The plant was applied to `poll` as it stood, before anything moved. The unit suite reported **297 of 297** and the smoke harness reported `ok`, with all five of its hot-reload arms running and both rejection diagnostics printed. Nothing in the repository caught the defect the issue had been filed about, so the gap was one instrument wider than the issue claimed.

Two lessons, both transferable:

- **A coverage tool cannot report this.** The code is not 0% covered; it is not present. Reading a coverage report and finding nothing alarming is consistent with a whole subsystem being absent.
- **An acceptance criterion that names the instrument it expects to fail is asserting something, and it has to be run rather than read.** This criterion named a hand-run harness as the one instrument that would catch the defect. Run, that harness caught nothing.

## Causes, by mechanism

| Mechanism                          | Spelling                                                                  |
| ---------------------------------- | ------------------------------------------------------------------------- |
| Compile-time branch on a test flag | `if (comptime is_test) Stub else Real`                                    |
| Build tags                         | `//go:build !test`, or a tag the test command never sets                  |
| Conditional compilation            | `#[cfg(not(test))]`, `#ifdef NDEBUG`, `#if DEBUG`                         |
| Feature flags                      | A default feature set that excludes the module under test                 |
| Build-mode branches                | Code behind a debug-only or release-only path                             |
| Type-check-only imports            | `if TYPE_CHECKING:`, where the runtime branch is never exercised          |
| Dependency injection at build time | A fake wired in for every test target, with no arm using the real one     |
| Dead-code elimination              | A declaration the linker drops, so a planted defect has nothing to affect |

The pattern to watch for is any predicate that mentions the test configuration. A stub selected for tests is a reasonable design; a stub selected for tests with no other arm reaching the real implementation is this failure.

## Lazy and per-declaration analysis

Some toolchains do not type-check what nothing references. A public function nothing calls can carry a type error and the build still succeeds.

Measured rather than reasoned about: a type error planted in one accessor built clean, and the same error in a function the suite calls failed the build. The same plant on a private method built clean even with a reflection-style sweep in place, because the sweep does not reach private declarations.

**The build cache cannot answer this question for you**, because a manifest lists the files the compiler read rather than the declarations it checked. The check that does answer it is a planted type error in the specific declaration you care about, which still produces a binary if nothing references it.

The closing move is a sweep that references every public declaration from a test, so the analysis reaches them. Then plant a type error in a declaration nothing calls and confirm the build now fails, which is the control on the sweep.

## The optimize-mode matrix

Run the suite in the configuration that ships, not only in the one that is convenient.

- Assertions may be compiled out in release, so a suite that passes in debug is silent about the artifact users receive.
- Optimization can remove the very branch a plant targets.
- A free positive control that the modes really differ: search each test binary for a panic message the compiler only emits in checked modes, and confirm it is present in some and absent in others. If every binary looks the same, the matrix is not actually testing different modes.

Then pin the configuration and give the pin a control of its own. On the source project a build option carries the mode the build system asked for and a compile-time block fails the build if the artifact was produced at another. Planted, by swapping the mode at the call site, it fails and names both modes. Without it, a refactor that drops the pin leaves a green job testing the same mode twice.

## The unvisited branch

The fourth class, and the hardest to notice.

The code compiles in a plain build, an instrument that could reach it exists, and no arm was ever written to steer it there. What makes it hard to see is that **every counter it moved was read by something, so nothing looked absent.** There is no gap in the coverage report, no stub in the source, and no configuration predicate to grep for. The branch is simply never taken by any input the suite supplies.

Finding these is a matter of enumerating the arms an instrument has rather than trusting that the instrument exists. Ask, for each check: which inputs does it actually run on, and which branch does each one take?

A related case worth recording separately: a defensive arm that an earlier guard refuses, so it cannot fire at all. That one is unreachable rather than unvisited, and it is worth a line in the plant table saying so.

## Finding all four

A procedure, cheapest first:

1. **Grep for configuration predicates that mention the test flag**, the test feature, or a debug-only mode. Each hit is a candidate for structural uncoverability.
1. **Plant a type error** in each declaration you believe is covered, one at a time, and confirm the build fails. A clean build means nothing is analyzing it.
1. **Plant a behavioural defect** in each declaration whose build did fail, and confirm a named test fails. A clean run over a compiled declaration is either an unvisited branch or a missing arm.
1. **Check the artifact.** Search the test binary for a string unique to the code in question. Absent, it is structural; present, the branch is merely unvisited.
1. **Record the class** in the plant table, because the remedy differs by class and a row that only says "not caught" invites the wrong fix.

## The remedy

For structural uncoverability, make the code reachable from a test build. Usually this means extracting the part that has no platform dependency, so the bookkeeping becomes a pure function the suite can call while the compile-time selection keeps only the part that genuinely cannot run under test. On the source project, extracting a watcher's bookkeeping turned a plant that nothing caught into a plant that fails three named tests.

For an unvisited branch, add the arm, and state which input steers it there.

For either, where extraction is not worth it, name the obligation and give it a home rather than leaving it as prose. A manual check with an owner is a different thing from a gap nobody has written down.
