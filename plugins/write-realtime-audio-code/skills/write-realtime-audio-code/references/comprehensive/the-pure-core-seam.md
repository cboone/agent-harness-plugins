# The Pure-Core Seam

Use a host-independent core to isolate behavior that can be built and tested without a plugin host. This boundary can contain explicit state. It is an architectural dependency boundary, not a claim that every core function is mathematically pure.

## Layer Responsibilities

One useful direction is host adapter to scheduling engine to arithmetic core. The adapter owns plugin APIs, buffers, event timestamps, process status, and host notifications. The scheduling engine owns domain timelines and policy. The core receives explicit state and configuration and returns behavior that can be compared without a host.

springer's proposed arithmetic core, scheduling engine, and adapter illustrate this direction, but its import assertion, scheduler, and Node-generated vectors are planned at the pinned revision. Do not present them as completed controls or tests.

## Enforce the Boundary

fosforo's [GPU interface assertions](https://github.com/cboone/fosforo/blob/1317e2b752f7f7d44db9bb7745200ca6e59dde83/src/gpu/iface.zig) check backend signatures in that project's vocabulary. They do not prove transitive imports are absent. A Rust crate without a plugin-API dependency or a C++ target without SDK include paths supplies a structural constraint, but other dependency paths can still expose a host API.

Show two distinct controls when enforcement is important:

| Restriction               | Control                                                                      | Scope                                                       |
| ------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Import or dependency rule | Introduce a forbidden host dependency and verify the actual check rejects it | Direct and transitive dependencies covered by that check    |
| Signature rule            | Change a backend signature and verify the interface assertion rejects it     | The listed signatures, not imports or callback reachability |

Keep shared containers independent of their producer and consumer so they remain testable on required targets. Do not add an unused abstraction only to demonstrate future portability.

## Validate Core and Adapter Separately

Build and test the core without a host. If it uses a reference implementation, define behavior and numerical tolerance. A pure arithmetic test can validate a cursor predicate but cannot prove legal concurrent access around it.

Test the adapter separately for buffer aliases, event time, lifecycle, process status, output obligations, and restart notifications. Correct DSP or scheduling behavior does not establish that a host adapter handles persistent ramps, delayed restart, in-place buffers, or pending output events. Reuse core vectors only for the behavior they specify.

Faust generated code, architecture files, foreign functions, and host glue still need a callback-safety audit. For arithmetic translations, specify negative-input behavior. JavaScript `Math.floor` and Zig `@divFloor` express floor division. Zig runtime signed division requires an explicit permitted operation such as `@divTrunc`, `@divFloor`, or `@divExact`; `/` is not a universal runtime truncation rule. Choose remainder semantics deliberately and test negative boundaries.

### Example: Enforced Rust Core Boundary

A Rust workspace has `core`, `scheduler`, and `clap-adapter` crates. `core` has no dependency path to the CLAP SDK; a dependency-policy check rejects a temporary direct or transitive CLAP dependency added to `core`. That failing control establishes the scope covered by the policy. A separate compile-time signature assertion rejects a backend function whose buffer argument changes from `&mut [f32]` to `&[f32]`; it does not prove import isolation.

Core vectors cover `floor_div(-1, 12) == -1` and a note timeline transition with a stated tolerance. Adapter fixtures separately cover an aliased buffer, event offset 63, a retained pending note-off, and delayed restart notification. The core vectors therefore support arithmetic and scheduling conclusions only. The policy-control and signature-control results must be recorded for the selected build before calling the boundary enforced.

## Sources

- [springer core-boundary ADR](https://github.com/cboone/springer/blob/e76419dc022cb1690d22c779cfee39dd5f53565d/docs/adr/0005-a-pure-musical-core-behind-a-seam.md), a planned design at the pinned revision
- [fosforo GPU interface assertions](https://github.com/cboone/fosforo/blob/1317e2b752f7f7d44db9bb7745200ca6e59dde83/src/gpu/iface.zig)
- [Faust foreign functions](https://faustdoc.grame.fr/manual/syntax/#foreign-functions) and [Zig 0.16 documentation](https://ziglang.org/documentation/0.16.0/)
