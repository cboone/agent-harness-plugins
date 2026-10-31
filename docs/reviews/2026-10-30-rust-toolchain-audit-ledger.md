# Rust toolchain audit review ledger

Base: `5205fada80635f7d9dd4a1967c94a256e60a99cb` (`origin/main` merge base).
Issue: [legacy Rust toolchain audit](https://github.com/cboone/agent-harness-plugins/issues/420).

## Scope and design

TOOLING directed legacy-first precedence to match rustup, superseding the brief's
modern-first order. No other runtime audits changed. Node and Ruby already inspect
multiple source forms; Python, Go and Zig inspect only their documented source,
so potential `.tool-versions` omissions were reported to TOOLING.

## Plants

The seven-case Scrut document passed before plants and after restoration. Tests
were committed before mutation. Each mutation changed the canonical template.

| Planted defect                                         | Instrument          | Measured result         | Coverage                             |
| ------------------------------------------------------ | ------------------- | ----------------------- | ------------------------------------ |
| Remove legacy fallback by selecting a nonexistent file | Rust Scrut document | Exit 50 via make exit 2 | Bare, TOML and precedence cases      |
| Return TOML key instead of channel value               | Rust Scrut document | Exit 50 via make exit 2 | Both TOML filename cases             |
| Accept moving channels                                 | Rust Scrut document | Exit 50 via make exit 2 | All nine format/channel combinations |
| Always report modern filename                          | Rust Scrut document | Exit 50 via make exit 2 | Exact legacy drift rows              |

## Structural Nit round

Fresh read-only Codex runs: `gpt-6.1-sol`, high effort, context 872000.
Report-only simplify used the four cleanup angles. All completed with valid,
nonempty structured results and no findings.

Setup failures before any cleanup reviewer launched: the scope file was still
being produced, then the repository-local helper refused to review itself.
The installed helper ran after scope completion. These were incomplete setup
attempts, not clean review rounds.

At this checkpoint, the anti-pattern result was pending.

## Validation checkpoint before focused review

Focused review, trims, baseline Semgrep, lint-and-fix, full suite, tidy and PR
are pending. JSON and plugin validators passed; check-versions confirms the
patch bump `1.2.5 -> 1.2.6`, catalog coverage, and manifest-only versions.

## Structural Nit findings and decisions

- Reviewer label Important; our severity Important: tailoring instructions would
  delete auditing in legacy-only repositories. Taken: updated the coverage
  summary and removal condition. Docs change alone needs no extra review.
- Reviewer label Important; our severity Important: single-quoted TOML channels
  were skipped. Taken: support literal quotes in both filenames, with two new
  regression cases. Behavior changed, advancing to the Important round.
- ShellCheck SC2154 was a CI-covered result, not a reviewer finding. Declared the
  fixture's sourced array explicitly; ShellCheck now passes.

The first anti-pattern reply was valid JSON but incomplete solely because its
sandbox tried GitHub despite the supplied no-PR context. Parent verification returned
an empty PR list; no PR body exists to review. Findings were taken without a
severity downgrade. This incomplete result is not described as clean.

Literal-quote plant: restoring the double-quote-only extractor failed both new
literal-channel tests (Scrut exit 50 via make exit 2). Restored nine-case suite
passes. Four simplify angles completed without findings. Next structural round
is Important, including report-only simplify.

## Structural Important round: stopped: recurring defect

The second anti-pattern review completed with valid schema output
and complete coverage. Reviewer label Important; our severity Important: valid
TOML quoted keys (`"channel" = "1.76.0"`) and triple-quoted string values are
still silently skipped. These are additional instances of the TOML parser-input
class fixed in the Nit round. The four simplify angles all completed with
valid results and no findings.

Take or record: retained unresolved pending TOOLING's structural design decision.
Review again: stopped by the recurrence rule; counts remain Nit 1, Important 1.
A structural TOML parser would close the format class, but the template currently
requires only Bash, gh, jq and curl, so adding a parser needs a design decision.

The focused aspects were mistakenly launched before the parent inspected the
Important result. Their recorded helper PID 15681 received SIGTERM; the helper
completed with status 143. Those interrupted aspects are incomplete, not clean,
and do not replace a completed focused review round.

No trims, baseline Semgrep, final lint-and-fix, full suite, tidy, push or PR ran.
The shared full-suite lock was never acquired. No live configuration changed.
JSON/plugin validators and check-versions passed. Targeted nine-case Scrut suite
and ShellCheck passed before the final literal-quote plant; the template was
restored byte-for-byte to the committed passing tree afterward.

## TOOLING structural decision and resume

TOOLING directed retaining Bash, gh, jq and curl without a new parser dependency.
The simple reader accepts bare channels and ordinary quoted TOML channels;
unsupported or malformed declarations now emit an `unreadable toolchain pin`
row with the selected filename and a manual-review status. Moving channels
remain skipped. This prevents silent omission by reporting uncertainty rather than
supporting every TOML spelling.

The in-progress label was restored. Thirteen targeted cases pass, including
quoted keys, triple-quoted values, malformed declarations in either filename,
and empty-file precedence. Two further plants failed (Scrut exit 50 via make
exit 2): removing the unreadable row failed the unsupported/malformed cases;
restoring permissive extraction failed the malformed-channel assertions.

Counts persist: structural Nit 1 and Important 1. The next round is Important 2
with report-only simplify. No focused review completed.

## Structural Important 2: stopped: recurring defect

Anti-pattern review completed with valid schema output and complete coverage.
Both findings have reviewer label Important and our severity Important because
unsupported inputs can still silently bypass the required manual-review row.

- Mixed quote content such as `channel = "stable'broken"` matches the quoted
  line but the shared quote separator truncates its value to `stable`.
- A multiline channel declaration containing an interior
  `channel = "stable"` line is mistaken for an ordinary moving channel.

Take or record: both remain unresolved at the recurrence stop. Review again:
TOOLING must choose the structural correction. A stricter simple reader could
reject unsupported channel declarations before considering later lines, and
extract using only the delimiter that actually opened the value.

Four simplify angles completed successfully. Efficiency reported one
`suggestion`: combine the two awk file reads. Our severity Nit, since the
extra subprocess and reread have limited cost. Recorded below the active
Important threshold; combining parser control flow is not a trivial local edit.
Other cleanup angles had no findings.

Counts: structural Nit 1, Important 2. No focused review completed. Final
trims, baseline Semgrep, lint-and-fix, full suite, tidy, push and PR remain
unrun. No live changes or full-suite lock acquisition occurred.

## Whole-file whitelist decision

TOOLING approved validating the complete TOML file against a simple whitelist:
blank lines, comments, one `[toolchain]` header, and ordinary single-line
string assignments with matching delimiters. Exactly one channel declaration
is required. Unsupported syntax, duplicate channels and invalid trailing lines
produce the unreadable row. Extraction uses the actual opening delimiter.

The twenty-four-case Scrut document passes. ShellCheck and shfmt pass.
Two required bypass plants were measured after committing the tests:
mixed-quote splitting failed all four mixed-quote assertions; ignoring the
whole-file invalid flag failed both multiline assertions plus both invalid
trailing-line assertions. Each run exited 50 through Scrut, make exit 2.
The original source was restored byte-for-byte after each plant.

Counts remain structural Nit 1 and Important 2. The next structural round is
Critical-only with report-only simplify. The question about applying the
whole-file restriction to legacy bare first-line input was sent to TOOLING;
the original issue explicitly asks for its first non-empty line.

TOOLING clarified that the whole-file restriction also applies to the bare
format: one non-empty channel line only, with surrounding whitespace and
blank lines allowed. The positive bare fixture now reflects that rule; an
additional regression requires a manual-review row for a second channel line.
All twenty-five targeted cases pass. Planting acceptance of additional bare
lines failed the dedicated assertion (Scrut exit 50 via make exit 2); source
restored. The clarification is reflected in the plan.

## Structural closure and focused Nit round

Structural Critical 1 completed with valid, complete anti-pattern output and
no Critical findings. Report-only simplify completed all four angles. Two
suggestions, our severity Nit, were recorded below threshold: the extra awk
reread and extracting a parser helper. Neither changes the reporting boundary.
Structural end state: **clean at Critical** (Nit 1, Important 2, Critical 1).
The scope comparison found no lasting changes.

Focused Nit 1 completed all four selected aspects (`code`, `errors`, `tests`,
`comments`) successfully on the same scope, with gpt-6.1-sol/high/872000 and
read-only sandboxing. Types was omitted because no typed data model changed.

- Code and errors: no findings.
- Comments: two reviewer `suggestion` labels, our severity Nit. Taken: document
  the whole-file TOML restriction, including unsupported arrays, and correct
  the bare-case heading. Docs only; no further round for those edits.
- Tests: reviewer `suggestion`, our severity Important because duplicate
  non-channel keys can leave malformed TOML silently skipped. Take or record:
  pending TOOLING's design call. Review again: required if behavior changes.
  This is another malformed-input instance; no code fix was applied before
  asking TOOLING to extend duplicate detection to every assignment key.

Focused state: **stopped: recurring defect**, count Nit 1.

TOOLING approved treating any duplicate assignment key as malformed, within
the whitelist design. The parser now tracks every key. Both filenames have
duplicate-profile regression cases; all twenty-seven cases pass. Removing the
`seen[key]` guard failed both dedicated assertions (Scrut exit 50 via make
exit 2), and the source was restored. Focused Important 1 is next.

## Focused Important 1: stopped: recurring defect

All four aspects completed with valid results and no lasting
scope changes. Tests had no findings. Code and errors independently reported
the same invalid-escape bypass: a moving channel plus a double-quoted field
containing an invalid TOML escape passes the whitelist and is silently skipped.
Both reviewer labels Important; our severity Important, since malformed files
must reach manual review. Deduplicated into one unresolved finding.

Take or record: no code fix pending TOOLING's design call. Review again:
required after the fix; counts remain focused Nit 1 and Important 1.
The proposal sent to TOOLING rejects backslashes in double-quoted values
rather than parsing escapes, and rejects control characters in quoted values.

Comments reported a `suggestion`, our severity Nit: generic silent-skip prose
needed a Rust exception. Taken as a documentation-only fix; no extra round
for that edit. Focused end state: **stopped: recurring defect**.

TOOLING approved rejecting every double-quoted backslash and control characters
inside either quote form. Six both-filename regressions cover the boundary;
a positive literal-string case preserves literal backslashes. All thirty-four
targeted cases pass. Removing the escape check failed both escape assertions;
removing the control check failed all four control assertions. Both plants
exited 50 via Scrut, make exit 2, and source was restored.

TOOLING also set the future severity boundary for this class: malformed files
rustup rejects lose no real drift coverage because the toolchain is already
invalid. Such findings are our severity Nit, recorded rather than fixed.
Findings where rustup accepts the file and an exact pin is hidden remain
Important. This prospective design/severity decision is not a silent downgrade.
Focused Important 2 is next; counts persist.

## Focused closure and trims

Focused Important 2 completed all four aspects with valid results and no
findings. End state: **clean at Important** (Nit 1, Important 2).
The scope comparison found no lasting changes.

Trim-comments and trim-text each ran once with gpt-6.1-sol/low/872000 in
read-only mode. Both passed exit, nonempty-output and expected-shape checks.
All proposed rewrites were checked against the original text and applied.
Flags about pending statuses were marked as historical checkpoints; the plan's
known lint failure was clarified as `review-submodule-fixture`, distinct from
the Rust fixture's resolved ShellCheck declaration. No behavior changed.

## Baseline Semgrep and lint-and-fix

Semgrep ran in `/tmp/420-review/semgrep-clone`, a disposable shared clone of
head `3315c6a9`, with `SEMGREP_REPO_NAME=cboone/agent-harness-plugins`,
`--config auto` and `--baseline-commit 5205fada80635f7d9dd4a1967c94a256e60a99cb`.
Exit 0: 104 rules, six scanned files, approximately 100% parsed lines,
zero findings and an empty errors array. Five paths were ignored by the scan's
configuration. This is the required baseline scan, not a full-scan substitute.

`lint-and-fix --no-push` ran after the code and trims stopped changing.
Pinned dependencies were installed with `corepack yarn install --immutable`
because the worktree initially lacked Yarn state. Earlier formatter attempts
had failed for that missing state; no successful formatting is attributed to
those attempts.

Modes and commands:

- Markdownlint: check-only by project policy. `tests/AGENTS.md` says Scrut files
  are never reformatted; the global fix command reaches those files.
  `corepack yarn lint:md` passed.
- Prettier: targeted write pass on the changed prose, with embedded-language
  formatting off; `corepack yarn format:check` passed across the project.
- shfmt: targeted write pass on the two changed shell files, then the
  repository's full `shfmt -d $(bin/list-shell-scripts)` check passed.
- ShellCheck: no auto-fix; full repository selection passed.
- actionlint: no auto-fix; passed.
- `bin/check-fixture-environments --review-paths`: failed solely on the known
  `tests/fixtures/review-submodule-fixture` rooted-operand checks at 132–134
  and 254. This is the explicit out-of-scope failure named in the brief.

Lint status is **failure with the known baseline exception**, not clean.
The formatting fixes are committed; no push occurred from the lint workflow.
The parent workstream continues to the locked full suite under the brief,
preserving the known failure without changing the unrelated fixture.

## Full-suite queue hold

The single full-suite command waited for the shared lock without acquiring it.
TOOLING reserved the next slot after the git-worktree-stub workstream for the
earlier dots-skill waiter and directed this worker to pause retries until
TOOLING assigns the slot. Recorded retry PID 78785 and its sleep child 61781
were stopped; exec session 37425 ended with status 143, and both PIDs were
observed gone. The full suite never started, no lock was acquired or removed,
and no test run was interrupted. Awaiting TOOLING's slot assignment before
restarting the single required full-suite command.

## Final full-suite result and fixture correction

TOOLING assigned the suite slot after the queue hold. The single
`SCRUT_JOBS=2 make -k test-all` run acquired the lock, completed with exit 2,
and released it through the exit trap. Lock absence was confirmed afterward.
No second full-suite run occurred.

Scrut: **55 of 57 documents passed**, including all 34 Rust behavior cases.
Failures were `environment-isolation.md` and `run-scrut-documents.md`.
Lint also reproduced the known `review-submodule-fixture` rooted-operand
failure. Validation found a branch defect: the new Rust fixture and its caller
needed the shared Git-environment reset at entry. Both now source
`bin/lib/git-environment.bash` using the repository convention.

The branch defect was taken and fixed. Its reviewer label was validator failure;
our severity Important because the mandatory validation gate failed. Review
again: no extra round for test-only setup edits, with production behavior
unchanged. The failing guard supplied a measured negative control before the fix.

After the correction:

- Rust Scrut: **35 of 35 cases pass**, including the shared reset setup.
- `make validate`: **passes**, including the environment guard, JSON, plugin,
  catalog and generated-mirror validation.
- `make lint`: fails only at the known `review-submodule-fixture` path guard;
  Markdown, Prettier, ShellCheck and shfmt pass. Actionlint passed separately.
- At TOOLING's request, the isolated environment document was rerun once:
  **50 of 51 cases pass**, with only its known fixture-contract case at line 39
  still failing. All missing-reset effects from this branch are resolved.
- The runner document's one failing case was its existing stderr assertion at
  line 254: an extra macOS `child setpgid: Operation not permitted` diagnostic.
  TOOLING identified it as the known runner flake tracked by
  [the Scrut worker-group fix](https://github.com/cboone/agent-harness-plugins/pull/703). It was not
  changed or retried.

The full run remains **failed**, not clean. Its raw result precedes the final
fixture correction; the affected document and validators were rerun afterward.
TOOLING agreed to proceed with those explicit out-of-scope caveats.
Version checks after fetching main confirm `pin-everything` 1.2.5 to 1.2.6,
forward patch direction and catalog/generated version parity. No live config
changed. Final publication evidence includes the exact-tree tidy comparison
and PR link in the worker's mailbox handoff.
