# Review case corpus

The conventions of record for the frozen corpus of review cases with known
defects. The corpus exists so that competing code reviewers can be compared on
identical inputs: public benchmarks do not measure false positives on this
code, and judging tools on live pull requests judges each one on a different
diff.

The corpus data lives in the private repository `cboone/review-case-corpus`.
The tooling that reads it lives here, beside the harness that will consume it:

- [`bin/materialize-case`](../bin/materialize-case) checks a case out as a git
  worktree.
- [`bin/validate-corpus`](../bin/validate-corpus) checks every case against the
  schema below.
- [`tests/scrut/review-corpus.md`](../tests/scrut/review-corpus.md) exercises
  both against the throwaway corpus that
  [`tests/fixtures/review-corpus-fixture`](../tests/fixtures/review-corpus-fixture)
  builds.

Keeping the data out of this repository is deliberate. Frozen case files here
would be read by `bin/validate-json`, `bin/list-shell-scripts`,
`markdownlint-cli2` and `prettier --check .`, so a planted defect in JSON would
fail `make validate` and one in shell would be reported by `make lint-shell`.
Only `markdownlint-cli2` and Prettier take ignore entries. `bin/validate-json`
prunes `node_modules` and `.yarn` inside its `find`, and
`bin/list-shell-scripts` skips `dist/*` in a `case` arm, so silencing a case
there means editing the tool. Deliberately defective code also needs a pushable
home that is not this repository's ref namespace.

## What a case is

One case is one merged pull request's `BASE..HEAD` diff. That shape is uniform
across all three sources, is recoverable from the GitHub API, and is what a PR
replay pushes back out.

`gh pr view N --json baseRefOid,headRefOid` names both ends, but **do not use
`baseRefOid` as `BASE`**. It is a tip of the base branch, and whether it is
also the merge base depends on when the branch diverged. It was the merge base
for `snappy` pull request 70 and was not for pull request 3, whose branch left
`main` before the release commit `baseRefOid` names. Compute the merge base
instead:

```bash
git merge-base "$(gh pr view N --json baseRefOid --jq .baseRefOid)" "${HEAD_SHA}"
```

`BASE` has to be an ancestor of `HEAD` or `git diff BASE...HEAD` reports a
change the reviewer was never shown. `bin/validate-corpus` checks the ancestry,
so a case frozen from `baseRefOid` by mistake fails validation rather than
quietly measuring the wrong diff.

## Case layout

Each case is a directory under `cases/` holding these four files. Anything
else in the directory is reported as a warning, not an error:

```text
cases/001-snappy-tick-refresh-race/
├── CASE.md          human narrative; nothing machine-read
├── BASE             one line, one 40-character hex SHA
├── HEAD             one line, one 40-character hex SHA
└── defects.yaml     every machine-readable field
```

Case IDs are `NNN-<repo>-<slug>`, zero-padded so directory order is stable.
The source and the defect classes deliberately do not appear in the ID, so
reclassifying a case never renames its directory and never invalidates a
recorded result.

Both SHAs are the real upstream commits. They stay valid inside the corpus
repository because the objects are the same ones, pushed there under
`refs/cases/<id>/base` and `refs/cases/<id>/head`. Freezing this way means the
corpus no longer depends on an upstream repository never force-pushing.

**The case refs are not branches, and must not become branches.** Every frozen
tree carries its own `.github/workflows/`, and Actions runs `on: push`
workflows for `refs/heads/*` and `refs/tags/*`. Stored as `refs/heads/case/*`,
the case refs ran each source repository's CI inside the corpus repository,
which is the observation this rule rests on. A custom ref under `refs/cases/`
is stored and fetched identically and starts nothing.

`tests/scrut/review-corpus.md` asserts the tool-side half of this, that a
materialized cache holds no `refs/heads/*` at all, so a widened fetch refspec
would show up. The freezing procedure itself lives in the corpus repository and
is not under test here.

One consequence: `refs/cases/*` is outside what a clone or an `actions/checkout`
fetches, even at `fetch-depth: 0`. A consumer needs an explicit
`git fetch origin 'refs/cases/*:refs/cases/*'`.

All machine-readable metadata sits in `defects.yaml`, which gives a harness a
single file to parse and keeps `CASE.md` free to be prose.

## The `defects.yaml` schema

```yaml
case: 001-snappy-tick-refresh-race
source: fix-commit
repo: https://github.com/cboone/snappy
languages: [go]
origin:
  introduced_by_pr: 3
  ground_truth: bf706bb192e8d7e7f1e29de0b3e9256fad5f76a5
defects:
  - id: D1
    file: internal/tui/update.go
    lines: [98, 112]
    class: concurrency
    severity: p1
    description: "handleTick schedules a refresh while a previous refresh is in flight, so results interleave."
    added_in: initial
```

### Top-level fields

| Field       | Required | Meaning                                                                                                                                                                                                                                                                                                   |
| ----------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `case`      | yes      | The case ID. Must equal the directory name.                                                                                                                                                                                                                                                               |
| `source`    | yes      | One of the three sources below.                                                                                                                                                                                                                                                                           |
| `repo`      | yes      | Clone URL of the repository the case was frozen from.                                                                                                                                                                                                                                                     |
| `languages` | yes      | Non-empty list of the languages the diff touches.                                                                                                                                                                                                                                                         |
| `origin`    | no       | Provenance. `introduced_by_pr` is the pull request the case is frozen from and is not validated. `ground_truth` is the later fix commit, for a `fix-commit` case, and when present must be a full 40-character lowercase hex SHA, because an abbreviation stops identifying the commit as upstream grows. |
| `defects`   | yes      | Non-empty list of the known defects.                                                                                                                                                                                                                                                                      |

### Defect fields

| Field           | Required | Meaning                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| --------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`            | yes      | Short identifier, unique within the case.                                                                                                                                                                                                                                                                                                                                                                                                   |
| `file`          | yes      | Path as it appears at `HEAD`. Must be in the `BASE..HEAD` diff.                                                                                                                                                                                                                                                                                                                                                                             |
| `lines`         | yes      | Two integers, start and end, both inside the file at `HEAD`.                                                                                                                                                                                                                                                                                                                                                                                |
| `class`         | yes      | One of the four classes below.                                                                                                                                                                                                                                                                                                                                                                                                              |
| `severity`      | yes      | `p1`, `p2` or `p3`.                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `description`   | yes      | One sentence saying what is wrong. Always double-quote it: a defect description very often contains a colon followed by a space, as in `RefreshResultMsg{DiskErr: true}`, which YAML refuses to parse, so the whole case fails as unreadable rather than as a bad description. The validator cannot enforce the quoting field by field, because an unquoted description has already made the file unparseable before any field is examined. |
| `added_in`      | yes      | `initial`, or the run ID that discovered the defect.                                                                                                                                                                                                                                                                                                                                                                                        |
| `discovered_by` | no       | The reviewer that found a defect the corpus did not list. Present only on later additions; see Findings the corpus does not list.                                                                                                                                                                                                                                                                                                           |

### Closed sets

`source` is one of:

| Value             | Meaning                                                                          |
| ----------------- | -------------------------------------------------------------------------------- |
| `fix-commit`      | A later `fix:` commit or revert located the defect. The fix is the ground truth. |
| `copilot-comment` | A Copilot review comment located the defect and a change followed.               |
| `planted`         | The defect was inserted deliberately at a known location.                        |

`class` is exactly these four, and adding a fifth is a deliberate change to
what the benchmark measures rather than a data entry, because recall is
reported per class:

| Value            | Covers                                                                                                     |
| ---------------- | ---------------------------------------------------------------------------------------------------------- |
| `logic`          | Wrong result, wrong branch, off-by-one, missing bound or nil guard.                                        |
| `error-handling` | A failure swallowed, misreported, or reported as success.                                                  |
| `concurrency`    | A race, a lock misuse, an ordering or visibility defect.                                                   |
| `input-handling` | Security-relevant handling of untrusted input: injection, escaping, path and symlink handling, validation. |

`p1` is what [`REVIEW.md`](../REVIEW.md) calls Important: it would break
behavior, lose or leak data, or break the build or a release. The `p1`-to-`p2`
mapping comes from the Code Review Rules block in [`AGENTS.md`](../AGENTS.md),
which puts a checklist's Important rules at P1 and the rest at P2 or lower.
`p3` is a third level local to this corpus, for a real but minor finding, with
no counterpart in either file.

## The reviewer must not reach the answer key

`CASE.md` and `defects.yaml` live on the corpus repository's `main`. The frozen
commits live in orphan histories that share no ancestor with `main`, and
`bin/materialize-case` builds its worktree from a local bare cache that has
fetched only those two refs. So `main` is not reachable from a materialized
worktree and neither file can be read from inside it.

This is not a detail. A reviewer that can read the corpus metadata measures
nothing, and the failure would be invisible in the results. The materializer
additionally checks the tree it just wrote for a `cases/` directory, a
`CASE.md` or a `defects.yaml`, and refuses a case whose own head commit carries
them. `tests/scrut/review-corpus.md` asserts the property by running the same
`git show` against the corpus and against the worktree, so the absence cannot
pass for a command that reads nothing anywhere.

The same reasoning applies to commit messages. A case's `HEAD` is a real pull
request head that predates its fix, so no message in the materialized history
describes the defect. A synthesized case must keep that property.

## Freezing a case

1. Identify the pull request. For a `fix-commit` case, blame the fix back to the
   pull request that introduced the defect; the fix itself is the ground truth,
   not the case. For a `copilot-comment` case, use the pull request the comment
   was left on, with `HEAD` set to the comment's `original_commit_id`, which is
   the commit the comment was anchored to and still holds the defect. For a
   `planted` case, use a clean commit and the commit that plants the defect.

   For a `copilot-comment` case, take the line numbers from
   `original_start_line` and `original_line`, never from `line`. GitHub
   recomputes `line` against the pull request's latest diff, so on a pull
   request with review rounds it points at where the code ended up after the
   finding was addressed, which is the one place the defect is not.

1. Set `HEAD` to the commit under review, then compute `BASE` as the merge base
   of `headRefOid` and the pull request's `baseRefOid`, as above. For a
   `copilot-comment` case, confirm the anchor commit is an ancestor of the
   merged head; if the branch was force-pushed it will not be, and the comment's
   line numbers refer to a commit the branch no longer contains.
1. Fetch the head commit into the corpus repository and record both ends with
   `git update-ref` at `refs/cases/<id>/base` and `refs/cases/<id>/head`, then
   push them with `git push origin 'refs/cases/*:refs/cases/*'`. One fetch is
   enough, because the base is an ancestor of the head. Fetching a full
   40-character SHA can be fetched from GitHub while it is still reachable from
   some ref there, which is exactly why this step exists: once the branch is
   force-pushed or deleted that fetch stops working and only the corpus copy
   remains.
1. Write the four files, then run `bin/validate-corpus --corpus DIR <id>`.

## Adding a planted case

Follow the [`plant-defects`](../plugins/plant-defects/README.md) discipline:
commit the clean state first, plant one defect at a time, revert between
plants, and record what happened rather than what was expected. Planting is the
only source where every defect is known rather than only the noticed ones,
which is what makes it the cleanest recall measurement.

Four things learned from planting the cases that are here.

**A plant the project's own instruments catch is not a corpus case.** It is a
result about the instruments, and the right response is to record it and plant
somewhere else. All three plants ran into this. Weakening an atomic ordering in
`cboone/fosforo` is impossible: its source canaries assert the exact text of
every `.release` store and `.acquire` load, so case 018 had to move to a gate
call site instead. The Rust sanitizer plant failed
`sanitize_branch_name_with_special_chars` until the test was relaxed alongside
it, which became case 017's second defect and improved the case. Three of the
four Markdown defect kinds this corpus admits are caught by `markdownlint`
here, which left case 020 only one shape to take.

**Record the build and test evidence in `CASE.md`, with counts.** A plant that
does not compile is not a passing plant, and a suite that reports nothing is
not a passing suite: `zig build test` printed no output and exited zero for
case 018, and only `--summary all` showed that 325 tests had actually run.

**Planted diffs are much smaller than the rest.** The planted cases here touch
one or two files; the fix-commit and Copilot cases run to ten or thirty. A
per-source score comparison has to account for that, because a reviewer doing
well on the planted set and badly on case 002 has not been measured on the same
task twice.

**A case drawn from this repository changes two files, not one**, because
`plugins/` is mirrored into `dist/codex/plugins/` and CI fails on drift. Run
`make build` so the case stays green, list only the `plugins/` path in
`defects.yaml`, and see the `dist/` rule under Curation rules for how the
scorer must treat a finding against the copy.

## What the corpus actually holds

Recorded because the mix is not the one that was planned, and the gap is
information about the source material rather than a shortfall to fix.

Twenty cases and 59 defects: 9 from fix commits, 7 from Copilot comments, 4
planted. All four defect classes appear in all three sources. By language,
7 Go, 7 across the shell family (`shell`, `zsh`, `yaml`, `jq`), 3 Lean, 3
Markdown, 2 Rust, 1 Zig.

Two constraints shaped that. **There is no public Rust of ours**: both Rust
cases come from upstream `raine/workmux`, and the frozen trees carry its
license. **Lean is genuinely thin**: across three public Lean repositories
there are 14 `*.lean` fix commits and 37 Copilot comments on `.lean` files, and
most of the comments are docstring drift, redundant imports or proof-style
suggestions rather than defects. Three Lean cases is close to what exists. The
planted set is 4 rather than 5 for a related reason: a planted Lean defect
cannot be shown to compile without bootstrapping Mathlib, and an unverified
plant is worth less than the real-history case that replaced it.

## Findings the corpus does not list

A reviewer will report defects the corpus has no entry for. Where inspection
confirms one is real, append it to `defects.yaml` with `added_in` set to the
run ID that found it and a `discovered_by` field naming the reviewer, and
record in that run's report that the corpus missed it.

Scoring must then exclude a defect from the recall denominator of any run that
predates its `added_in`. Without that rule, every addition quietly lowers the
scores of every earlier run and the runs stop being comparable.

## Curation rules

**Markdown cases.** Most Markdown review comments are prose or consistency
nits rather than defects. Admit only mechanically wrong Markdown: a relative
link to a file that does not exist, a reference-style link with no definition,
a table row with a dropped column, or a documented flag the code does not have.

**Cases drawn from this repository.** `plugins/` is mirrored into
`dist/codex/plugins/`, so a defect here appears twice in the diff. List only
the canonical `plugins/` path as the defect and record the mirror path in
`CASE.md`. A finding against the mirror is neither a second catch nor a false
positive, and the scorer has to know that.

**Copilot cases.** Thread resolution is not evidence that a comment was acted
on: 244 of 246 Copilot threads in this repository and 50 of 51 in `snappy` are
resolved. Use the commits titled `fix: address Copilot PR review feedback
(round N)` instead, which pair a thread batch directly to its fix diff.

**Provenance.** Only public repositories are sources. Client code stays out
entirely, and the `swing-left` organization is excluded: its public
repositories are hiring-process artifacts and everything substantive in it is
private.

## Using the corpus

```bash
export REVIEW_CASE_CORPUS_DIR=~/Development/review-case-corpus

bin/validate-corpus
bin/materialize-case 001-snappy-tick-refresh-race "${TMPDIR}/case"
```

`bin/materialize-case` reports `CASE=`, `WORKTREE=`, `BASE=` and `HEAD=` lines,
so a harness can read the worktree path and pass `--base "${BASE}"` to the
reviewer under test without parsing the corpus itself. Worktree registrations
left behind by a removed directory are cleared with `--prune`.

`bin/materialize-case` writes its object cache to `<corpus>/.cache/cases.git`
unless `--cache` says otherwise, so a corpus repository must ignore `.cache/`
or a `git add -A` there would commit a bare repository and its worktree
registrations.

One precondition on the isolation guarantee above: it holds because the default
cache never fetches `main`. A `--cache` pointed at the corpus's own `.git`
would give a worktree from which `main` is reachable, and the metadata check
would not catch it, because that check inspects only the checked-out tree.

`bin/validate-corpus` needs `jq` and mikefarah `yq` v4. It reports GitHub
Actions annotations and a summary carrying the case and defect counts, so a run
that checked nothing cannot be mistaken for a clean one.
