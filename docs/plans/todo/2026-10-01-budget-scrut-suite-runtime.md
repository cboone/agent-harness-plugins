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
- **#527's root cause is the per-document timeout, not a per-case one.** scrut 0.4.3 sets no per-case timeout by default. Each document gets a 15-minute `total_timeout`, and documents run sequentially. `timeout in execution` names whichever case was running when the document's budget ran out. That is why the failing case moved between runs (lines 199 and 242). On this machine the document exceeds the budget even with nothing else running.
- **`bin/validate-plugins` spends its time starting processes.** A first timing gave 28s, 11s of it user time and 22s system time. A timestamped xtrace attributes about half of it to rule 19, `bin/check-cross-references`, 14s in that run. The hottest line there is `contains_line`, which runs `printf | grep -Fxq` about 2,000 times. The next costliest rules are 17, 16, 7 and 4, at 2 to 3s each, and rules 4 and 7 start one `jq` per field per plugin. Timings vary from run to run on this machine, so the Outcome table compares paired runs taken minutes apart instead.
- The copy step is small (674 files) and `build-codex-marketplace` takes 2.5s. Trimming the fixture copy would save little, and it would break the `aggregate-overflow` and `path-overhead` scenarios, which are tuned to the full catalog's token count.

## Approach

Fix the cost where it lives, in the validator that every fixture case runs. Split the slow document, and run each scrut document as its own CI job, so the suite takes as long as its slowest document. Restore the 10-minute CI ceiling, written down as a budget: every document's job finishes within half of it.

### 1. Speed up `bin/check-cross-references`

- `contains_line` matches in the shell instead of starting a `grep`.
- Each extraction pipeline in `collect_candidates`, and the composition and near-miss extractions, runs only when the body contains a substring that every match of its pattern must contain. A guard can only skip an extraction that would have found nothing.
- Each file's scannable body is computed once and passed to every check that reads it.
- A full pass selects candidate files and files with declaration comments in two `grep -l` runs over every file instead of two per file. A `grep` status above 1 stops the run, so a failure cannot empty the list and report success having checked nothing. The explicit-file path keeps its per-file checks.

### 2. Speed up `bin/validate-plugins`

- Required-field checks (rules 4, 7 and 12) use one `jq` run per manifest or catalog instead of one per field. A manifest with no JSON value reads as null, so every field is still reported.
- Rules 6, 6b, 8 and 15 read the catalog once instead of twice per entry, joining fields with the unit separator.
- Rule 17's byte and character counts use Bash builtins under a function-local `LC_ALL=C` instead of three processes each.

### 3. Split the validator scrut cases

The validator cases leave `tests/scrut/repo-tooling.md` for `tests/scrut/validate-plugins-catalog.md` (manifests, catalog version state and the Codex inventory budget) and `tests/scrut/validate-plugins-skills.md` (generated Codex skills, frontmatter, cross-references and review checklists). Release automation, version comparison, the shell script list and the byte-identical script checks stay in `repo-tooling.md`. No environment variable changes, so `Makefile` `SCRUT_ENV` and the `ci.yml` `scrut-env` block stay as they are.

### 4. Run each scrut document as its own CI job

A small job lists the documents under `tests/scrut/`, matching the files `scrut test` would read, and the reusable workflow runs as a matrix over them with `fail-fast: false`. The list comes from the tree, so a new document joins without registration and no shard list can drift from the suite. Everything stays under `tests/scrut/`, so `make test-scrut` and the review-checklist mapping for `tests/scrut/**` are unchanged.

### 5. Set the budget and document it

- `.github/workflows/ci.yml`: `timeout-minutes: 10`, with the budget stated beside it.
- `tests/AGENTS.md`: the budget, how to time one document, where the time usually goes, and how to read `timeout in execution` locally, where it is the document's 15-minute `total_timeout`. In CI the job timeout stops a slow document first. That covers #527's "name the resource problem" criterion, since scrut's own message cannot change.

### 6. Test coverage added for the changes

- `tests/scrut/check-cross-references.md`: a full scan with findings in its first and last files, which fails if the scan stops early or reorders, and a full-scan `repository-paths` declaration, which fails if declaration comments stop being read.
- `tests/fixtures/validate-plugin-fixture`: the `long-description` scenario uses a 200-character, 240-byte description, so a character count that regressed to bytes fails the case.

`bin/` and `tests/` are not plugins, so no version bumps are needed.

## Critical files

- `bin/check-cross-references`, `bin/validate-plugins`
- `tests/scrut/repo-tooling.md`, `tests/scrut/validate-plugins-catalog.md`, `tests/scrut/validate-plugins-skills.md`, `tests/scrut/check-cross-references.md`, `tests/fixtures/validate-plugin-fixture`
- `.github/workflows/ci.yml`, `tests/AGENTS.md`

## Verification

1. Capture `bin/validate-plugins` and `bin/check-cross-references` output and exit status before and after, on the real repository and on several fixture scenarios (`valid`, `invalid-review-checklist`, `near-miss-invocation`, `aggregate-overflow`, `missing-openai-yaml`, `unknown-frontmatter-field`, `leading-zero`), and diff them.
2. Run the merge-base and new `bin/validate-plugins` over mutated catalogs and manifests and diff their output.
3. Plant the defects each new guard and test case claims to catch, and confirm a case fails.
4. `make test-all`: every document passes with no per-document timeout.
5. On `ubuntu-latest`, every per-document job finishes within 5 minutes.

## Outcome

### Local, same Mac

| Measure                                   | Before             | After            |
| ----------------------------------------- | ------------------ | ---------------- |
| `bin/check-cross-references`              | 11s                | 4.5s             |
| `bin/validate-plugins`                    | 24s                | about 12s        |
| One `validate-plugin-fixture` run         | 28s                | about 16s        |
| `repo-tooling.md`                         | over 900s, aborted | 5s (25 cases)    |
| `validate-plugins-catalog.md` (13 cases)  | part of the above  | 209s             |
| `validate-plugins-skills.md` (16 cases)   | part of the above  | 238s             |
| `make test-all`, before the merge of main | could not pass     | 567s, 638 of 638 |

### CI on `ubuntu-latest`

| Measure                                       | Time                                |
| --------------------------------------------- | ----------------------------------- |
| Single job before this work, 582 cases        | 9m17s                               |
| Single job with the speedups alone, 641 cases | 6m24s                               |
| Per-document jobs, wall clock, 641 cases      | 2m25s                               |
| Slowest document                              | `validate-plugins-skills.md`, 2m16s |

The case count rose from 638 to 641 when main, with three new argument-hint cases, was merged in. The single job with the speedups alone was 64 percent of the ceiling, over the half the budget allows, which is why the per-document jobs were added.

### Behavior preserved

For well-formed input, the validators' output and exit status are unchanged:

- Output captured before the change is byte-identical after it, on the real repository under Bash 5 and macOS Bash 3.2, and on the seven fixture scenarios above.
- Twelve mutated catalogs and manifests produce identical errors from the merge-base and new `bin/validate-plugins`: missing, false, null and empty fields, empty and missing names, bad sources, versioned entries, a shorter or mismatched Codex catalog, and an empty manifest.

Three differences remain, all on malformed input, and none changes whether the run passes:

- A marketplace `source` that is not a string prints as compact JSON on one line. The old output spread it over several lines, which split the `::error::` annotation.
- A required field holding only newlines counts as present. The old shell comparison stripped trailing newlines and reported it missing.
- A newline inside a marketplace name or source splits that entry's line, so its errors are attributed differently and counted more than once. The old output spread such a value over several lines too.

## Follow-up, not in this work

With no arguments, `bin/check-cross-references` exits on `main "${@}"` under macOS Bash 3.2 (`@: unbound variable`). This predates the work, and `bin/validate-plugins` reaches it through a Bash 5 `env bash` on this machine.
