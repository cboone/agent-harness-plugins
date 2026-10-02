# Bring the scrut suite under a deliberate budget (#533, #527)

## Context

Issue #533: the scrut job took 9m17s on `ubuntu-latest` against a 10-minute timeout, and #465 raised the timeout to 20 to unblock CI. The issue asks to measure first, then choose a budget the suite sits comfortably inside. Issue #527: `validate-plugin-fixture` cases in `tests/scrut/repo-tooling.md` fail with `timeout in execution` and no output under load. One PR closes both.

### Measurements (2026-10-01, this Mac, documents run one at a time)

| Document                    | Time                              |
| --------------------------- | --------------------------------- |
| `repo-tooling.md`           | **900s, aborted (rc=2)**          |
| `manage-resource-claims.md` | 51s                               |
| `launch-workmux.md`         | 37s (31 cases sleep 1s by design) |
| `review-corpus.md`          | 20s                               |
| other nine documents        | 47s combined                      |

Findings:

- **The time is concentrated, not spread.** Twelve documents take 155s together. `repo-tooling.md` alone exceeds 15 minutes. Its 25 `validate-plugin-fixture` cases each run a full `bin/build-codex-marketplace` plus `bin/validate-plugins` over a repository copy.
- **#527's root cause is the per-document timeout, not a per-case one.** scrut 0.4.3 sets no per-case timeout by default. Each document gets a 15-minute `total_timeout`, and documents run sequentially. `timeout in execution` names whichever case was running when the document's budget ran out. That is why the failing case moved between runs (lines 199 and 242). On this machine the document now exceeds the budget even with nothing else running.
- **`bin/validate-plugins` takes 28s (11s user, 22s system).** The high system time means the cost is process spawning, not computation. A timestamped xtrace attributes about half of it to rule 19, `bin/check-cross-references` (14s on its own). The hottest line there is `contains_line`, which runs `printf | grep -Fxq` about 2,000 times. The next costliest rules are 17, 16, 7 and 4, at 2–3s each, and rules 4 and 7 spawn one `jq` per field per plugin.
- The copy step is small (674 files) and `build-codex-marketplace` takes 2.5s. Trimming the fixture copy would save little, and it would break the `aggregate-overflow` and `path-overhead` scenarios, which are tuned to the full catalog's token count.

## Approach

Fix the cost where it lives: in the validator that every fixture case runs. Also split the slow document, so a timeout names a narrow suite and each part has its own budget. Then restore a 10-minute CI ceiling, written down as the budget.

### 1. Rename the plan file

Move this file to `docs/plans/todo/2026-10-01-budget-scrut-suite-runtime.md` to follow the dated naming convention, then commit it.

### 2. Speed up `bin/check-cross-references`

- Replace `contains_line` with a Bash-builtin newline-delimited membership test, which spawns no processes.
- Re-profile with `PS4='+${EPOCHREALTIME} ${LINENO} '` and remove the next hotspots the same way. Candidates are the repeated `printf "${body}" | grep | sed | sort` pipelines in `collect_candidates`, and the `scannable_lines` reruns across `check_compositions`, `check_near_misses` and `check_declarations` for the same file, which could compute once per file. Output must stay byte-identical.
- Follow the `write-bash-scripts` skill.

### 3. Speed up `bin/validate-plugins`

- Rules 4, 7 and 12 call `jq` once per required field. Collapse each into one `jq` call per manifest or entry that reports the missing fields, keeping the existing `::error::` text.
- Re-profile, and treat any rule still above about 1s the same way where the change is mechanical. Error messages and ordering stay identical, because the scrut snapshots assert on them.

### 4. Split `tests/scrut/repo-tooling.md`

Move the validator sections (lines 5–302: version state, Codex inventory budget, generated Codex skills, the frontmatter allowlist, cross-reference warnings and stale review checklists) into a new `tests/scrut/validate-plugins.md`. Release automation, version comparison, the shell script list and the byte-identical script checks stay in `repo-tooling.md`. No environment variables change, so `Makefile` `SCRUT_ENV` and `ci.yml` `scrut-env` stay as they are. Follow the `write-scrut-tests` skill.

### 5. Set the budget in CI and document it

- `.github/workflows/ci.yml`: set `timeout-minutes: 10`. Replace the comment with the budget: the suite should finish within about half the ceiling on `ubuntu-latest`. When it outgrows that, the fix is to cut runtime or shard the job, not to raise the ceiling. Sharding (a matrix over test directories) stays deferred while the single job fits.
- `tests/AGENTS.md`: add the budget and how to measure it (time each document on its own). Add how to read `timeout in execution` with empty output: it is the document's 15-minute `total_timeout`, and the named case is only where execution happened to be. That covers #527's "name the resource problem" criterion, since scrut's own message cannot change. Keep this file within the instruction-size limits.

### 6. Commits

Conventional Commits, signed with `-S`, each referencing both issues where relevant:

- `docs: add plan for scrut runtime budget (#533, #527)`
- `perf: stop check-cross-references forking per membership test (#527)`
- `perf: batch manifest field checks in validate-plugins (#527)`
- `test: split validator cases out of repo-tooling scrut suite (#533)`
- `ci: hold the scrut job to a 10-minute budget (#533)`

`bin/` and `tests/` are not plugins, so no version bumps are needed. Run the `check-versions` skill before the PR anyway.

PR body: `Closes #533` and `Closes #527`, with before and after timings.

## Critical files

- `bin/check-cross-references`, `bin/validate-plugins`
- `tests/scrut/repo-tooling.md` and the new `tests/scrut/validate-plugins.md`
- `.github/workflows/ci.yml`, `tests/AGENTS.md`

## Verification

1. Before and after, capture `bin/validate-plugins` and `bin/check-cross-references` stdout and stderr on the real repo and on several fixture scenarios (`valid`, `invalid-review-checklist`, `near-miss-invocation`, `aggregate-overflow`). Diff them: they must be byte-identical.
2. Re-time `bin/validate-plugins`, one `validate-plugin-fixture invalid-review-checklist` run, and each scrut document. Record the numbers in the PR.
3. `make test-scrut`: all documents pass with no per-document timeout. Observe the final result.
4. `make lint` and `make validate`, then `make test-all`.
5. After pushing, confirm the CI scrut job time on `ubuntu-latest` is under 5 minutes. If it is not, profile the next hotspot before opening the PR, rather than raising the timeout.

## Open risk

The size of the speedup is unknown until the profile-and-fix loop runs. If the validator changes alone do not bring `validate-plugins.md` comfortably under the local 15-minute document budget, step 4 still isolates it. The fallback is to shard that document's cases across two files, which does not touch the assertions.

## Outcome (local, same Mac)

| Measure                                       | Before             | After            |
| --------------------------------------------- | ------------------ | ---------------- |
| `bin/check-cross-references`                  | 11s                | 4.5s             |
| `bin/validate-plugins`                        | 24s                | about 12s        |
| One `validate-plugin-fixture` run             | 28s                | about 16s        |
| `repo-tooling.md` (51 cases before the split) | over 900s, aborted | 5s (25 cases)    |
| `validate-plugins.md` (26 cases)              | not separate       | 445s             |
| `make test-all`                               | could not pass     | 567s, 638 of 638 |

Every validator output captured before the change, on the real repository and on seven fixture scenarios, is byte-identical after it. Eleven mutated catalogs and manifests produce identical errors from the old and new `bin/validate-plugins`, with one intended exception: a marketplace `source` that is not a string now prints as compact JSON on one line, where the old output spread it over several and broke the `::error::` annotation. `bin/check-cross-references` is also identical under macOS Bash 3.2 when given explicit files.

Found along the way and left out of scope: with no arguments, `bin/check-cross-references` exits on `main "${@}"` under Bash 3.2 (`@: unbound variable`). This predates the branch, and `bin/validate-plugins` reaches it through a Bash 5 `env bash` on this machine.
