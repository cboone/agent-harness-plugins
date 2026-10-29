# Root filesystem operands for captured paths

Structural Important round 2 found another instance of the option-like operand class fixed in round 1. Collection now accepts a checkout named `-vendor`, but the rewritten discovery snippet runs `readlink -n "${path}"` for `-vendor/new-link`. Quoting does not stop option parsing. Discovery exits before emitting the required link annotation.

Proposed invariant: scope data keeps its canonical repository-relative paths; filesystem operations never receive those strings as unrooted CLI operands. Derive a separate operand once before acting on each path. Use the absolute repository root in collectors and helper renderers, and `./${path}` in the discovery loop, which runs from the captured repository root. Keep the original relative path in JSON annotations and findings.

Audit every filesystem operand in both helper copies and the reviewer instructions against that invariant, including `cd`, `find` and `readlink`. The shared Git policy remains unchanged. This needs no new tool or library: existing per-checkout and per-path variables can hold rooted operands consistently.

Add an end-to-end fixture combining the currently separate cases: a normally named submodule checked out at `-vendor`, containing an untracked symlink. Run collection, prompt, validation, changes and gate; execute the actual documentation snippet and require a link-only annotation with the original relative path. Confirm the target contents do not appear. Plant removal of the rooted operand and require that exact Scrut case to fail. Run the combined case under Bash 3.2 too.

No fix is applied at the recurrence gate. After TOOLING's decision, the next structural threshold is Critical-only if production behavior changes, preserving Nit 1 and two Important rounds. If the fix remains instructions/tests only, the no-behavior-change rule requires no additional structural round.
