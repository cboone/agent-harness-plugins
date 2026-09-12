# Vacuous Passes

A check that runs on nothing passes. It is indistinguishable, from the outside, from a check that ran and found nothing.

## The catalogue

Every entry below is a measured instance rather than a hypothetical.

### The instrument read zero files

A format or lint check whose file selection matched nothing reports success. The output often says so, in a line nobody reads: a count of files checked, sitting above a green summary.

**Control:** assert the reported count is non-zero, or plant a violation in a file you believe is selected and confirm the check goes red.

### A glob that matches nothing

An extensionless script was added to a Python linter's file selection as `extend-include = ["measure-trace"]`. That matches nothing, because the tool globs with a literal path separator and a pattern without a `/` matches only at the repository root. With an unused import planted, the spelling reported "All checks passed". The fix was `["**/measure-trace"]`.

The same branch produced the same failure shape twice. A spell checker needed `extend-identifiers` rather than `extend-words`, because it splits an identifier into words before judging it, so the obvious entry suppressed nothing while reporting success.

**Control:** the planted violation is not optional. A vacuous run of a selection-based tool looks exactly like a clean one.

### A delegated check the instrument skips when its dependency is absent

A workflow linter delegates shell checking inside `run:` blocks to an external shell linter. With that linter absent from `PATH`, it skips every `run:` block **and exits 0**. A planted quoting violation exits 1 with the dependency present and 0 without, and pointing the tool at a nonexistent path behaves like the latter.

The same tool resolves local action references through the git project root, so run outside a checkout it skips every local-action check in the same silence and exits 0. A first attempt at measuring its coverage produced three false negatives for exactly that reason.

**Control:** print the dependency's version in the same job, and plant one violation of the delegated class. Then the acceptance criterion can be written in the sharpest possible form: run the tool with the dependency removed, against the plant, and confirm it exits **0**. That is the vacuous pass, and it is what the install step exists to prevent.

### A value that compares false against every bound

Two decay checks divided a measured peak by a first peak nothing validated. A blank readback gives `0 / 0`, and `nan > 0.02 * want` is **false**, so a run in which nothing was drawn at all read as a healthy fade and reported one. It had been passing for two issues.

Every comparison against a not-a-number value is false, including `==` against itself. **Which way that lands depends on how the check is phrased, and only one of the two phrasings is vacuous:**

| Phrasing                     | On a not-a-number value    |
| ---------------------------- | -------------------------- |
| `if error > tolerance: fail` | Does not fire. **Passes.** |
| `assert error <= tolerance`  | Is false. Correctly fails. |

So this is not a hazard of floating-point bounds in general. It is a hazard of expressing a bound as a **failure condition**, which is the natural way to write one in a shell script, a CI gate, or any check that reports rather than asserts. The assertion form is safe here by construction, which is a reason to prefer it where the language offers both.

**Control:** assert the value is a number, or assert the denominator, before comparing it. Where the check must stay in failure-condition form, add the not-a-number case as its own arm rather than relying on the comparison to catch it.

### An assertion compiled out in the mode that ships

A suite run only in a debug configuration says nothing about a release artifact whose assertions are gone. The inverse also happens: an assertion whose argument is evaluated for effect in one configuration and elided in another.

Measured caveat from the source project: in that language `assert` is an ordinary function, so its argument is evaluated in every optimize mode and the classic C hazard does not exist. The plant designed to be discriminating therefore stayed green in all three modes. Do not assume the hazard, and do not assume its absence. Plant and see.

**Control:** run the suite in every mode that ships. Then pin the mode and give the pin its own control, or a refactor that drops the pin leaves a green job testing the same mode twice, which is this failure one level up. See `./references/structural-uncoverability.md`.

### A snapshot assertion too loose to fail

A snapshot test whose expected output is mostly wildcards still passes. This happens by accretion: a pattern is widened once to absorb a legitimate difference and then never narrowed.

It also happens by tooling. After a bulk snapshot update, review the diff to confirm glob and regex patterns were not replaced with the literals from the run that produced them, and that a literal you cared about was not replaced with a glob.

**Control:** plant a change in the pinned text and confirm the snapshot goes red. Include the exit code in every expectation, since an assertion on output alone passes over a crash that printed the right thing first.

### A grep-based assertion defeated by a rename

Several CI assertions grep a built artifact for a declaration's name. Nothing links the needle to the declaration, so renaming the declaration makes the assertion vacuous and green at the same moment.

Worse, a positive control can be present and still not help: the control protected the binary being readable, not the needle still being right.

**Control:** these are two different goals and they need two different remedies, because neither one achieves the other.

- **A stale hard-coded needle** is what deriving the needle from the source fixes. Note what it does not fix: once the needle comes from the source, a rename moves the needle and the artifact together, so the check stays green. That is the correct behaviour for this goal, and it is why the next one is still needed.
- **A needle that no longer matches anything** is what asserting the count fixes. Require a specific non-zero count rather than mere presence, so a rename that leaves the search finding nothing fails rather than passing.

An arity guard has the same failure: a helper that looks for a name and counts what follows it stops being an arity test the moment the name moves, and degenerates into a second copy of the not-found check.

### A shell idiom that turns an absence into a zero

```bash
bytes="$(grep -oE '[0-9]+ bytes' "${report}" | head -1 | cut -d' ' -f1 || true)"
if [[ "${bytes}" -gt "${BOUND}" ]]; then
```

With no match, `bytes` is the empty string, which the shell reads as zero in an arithmetic context, and zero is inside every bound. The `|| true` added to survive `errexit` is what converts a missing measurement into a passing one.

**The same line passes a second way, and it is worth knowing because it looks nothing like the first.** Drop the `cut` and the capture keeps its `bytes` suffix, so a real report value gives `[[ 137152 bytes -gt ... ]]`, which bash rejects with `arithmetic syntax error`. Under `errexit` inside a condition the error does not stop the script: the test evaluates false, and the check reports no violation. So a malformed operand and a missing one both read as "inside the bound", one of them while printing an error nobody reads.

**Control:** validate the extracted value is a non-empty run of digits before comparing it, and fail if it is not. Then both readings become failures instead of passes.

## The remedy is a positive control

For every check that asserts an absence, arrange one thing that must be present.

- Assert the instrument reports a non-zero count of whatever it examines.
- Print the version of the dependency the instrument delegates to, in the same job.
- Find the string you know is there before trusting it not to find the string you hope is absent.
- Plant one violation of the class the instrument claims to detect, and keep the plant's diff in the plan so it can be reapplied.

State it as a rule about runs rather than about checks: **every null result should share a run with a positive control.** A report of "nothing found" from a run in which nothing else was found either is not evidence.

## The non-vacuous direction

Pair every bound with an assertion in the opposite direction, chosen so that a degenerate implementation fails.

```text
tonemap(w, w) == 1.0            a correct implementation satisfies this
tonemap(w * 0.99, w) < 1.0      and so does `return 1.0`, which this refuses
```

Ask of each assertion: which trivial implementation passes it? `return true`, `return 0`, `return the input unchanged`, `do nothing`. If one of them passes, the assertion is one-sided and needs its counterpart.

## Instances by toolchain

| Toolchain              | The vacuous pass                                                                          |
| ---------------------- | ----------------------------------------------------------------------------------------- |
| pytest                 | Exit 5 on `collected 0 items`, normalized to success by a wrapper or a `\|\| true`        |
| Jest or Vitest         | `--passWithNoTests` over a pattern matching no file; a suite with every case skipped      |
| Go                     | `no test files` per package, and a package excluded from a build tag the suite never sets |
| Cargo                  | A test target with no tests, or a `#[cfg(feature)]` test the CI feature set never enables |
| Swift                  | A test plan that excludes the target; `#if DEBUG` assertions absent from a release run    |
| Markdown or prose lint | A config whose `ignore` list has grown to cover the files being changed                   |
| Coverage tools         | A report over a binary that does not contain the code, which shows as absent, not as 0%   |
| Any containerized job  | A mounted path that is empty, so the tool runs correctly over nothing                     |

The last one generalizes: any indirection between the instrument and the files it is meant to read is a place where the set can become empty without the instrument noticing.

**Note which runners refuse an empty selection and which accept it, because the top two rows differ from the rest.** pytest exits 5 on collecting nothing, and Jest and Vitest fail with "no tests found", so in both the runner already tells you. The vacuity is introduced on top of that, by a wrapper that maps the refusal onto success or by the flag that asks for it, which is why those rows name the wrapper rather than the empty selection. Contrast `go test ./...`, which reports `no test files` and exits 0 on its own: there the runner is the vacuous one, and nothing has to be added. Check which kind you have before writing the control, since for the first kind the control is a test of your CI glue rather than of the runner.
