# Build a frozen corpus of review cases with known defects

Issue [#505](https://github.com/cboone/agent-harness-plugins/issues/505). Consumers: [#506](https://github.com/cboone/agent-harness-plugins/issues/506) (local harness and scoring), [#507](https://github.com/cboone/agent-harness-plugins/issues/507) (PR-bot replay).

## Context

Choosing between code reviewers currently rests on impressions. Public benchmarks do not measure false positives on this code, and comparing tools on live pull requests judges each one on different inputs. A small frozen set of cases with known defects removes both problems: every tool sees identical inputs, the known defects give recall ground truth, and re-running the set when a tool updates is cheap.

This plan builds the corpus and the tooling that reads it. The runner, the scoring and the PR replay are #506 and #507.

Two mechanics were verified before planning. `gh pr view N --json baseRefOid,headRefOid` returns the true merge base, confirmed equal to `git merge-base` for PR #503, and the pull request head. Fetching an arbitrary full 40-character SHA from a public GitHub repository succeeds, so a case can be frozen and re-materialized without a full clone.

## Decisions

These were the issue's open questions.

**The corpus data lives in a new private repository, `cboone/review-case-corpus`. The tooling stays here.** Four separate gates in this repository would otherwise read frozen case files: `bin/validate-json` finds every `*.json` in the tree, `bin/list-shell-scripts` selects every tracked executable file with a bash shebang, `markdownlint-cli2` matches `**/*.md`, and `prettier --check .` matches everything else including `*.yaml`. A planted defect in JSON would fail `make validate`, and one in shell would be reported by `make lint-shell`. Three of those gates can be silenced with ignore entries, but `bin/list-shell-scripts` has no ignore mechanism beyond a hardcoded `dist/*` skip at lines 37 to 40, so it would need a code change. On top of that, this repository's `REVIEW.md` and `.github/skills/code-review/SKILL.md` would be applied by review bots to any pull request carrying corpus cases, and the planted-defect commits need a pushable home that is not this repository's ref namespace.

Tooling stays here because #506's harness will live here and because copies drift. This repository already carries the cost of that: `plugins/AGENTS.md` line 7 requires three worktree helpers to stay byte-identical across two plugins. The corpus repository gets no copy of the scripts; its README points here.

**The corpus repository is private.** #507 already proposes a separate public scratch repository for the bot replay, so nothing is lost: the replay path becomes corpus (private) to scratch (public), and because every case's source code comes from a public repository to begin with, that push exposes nothing that was not already public. The free bot tiers that need a public repository apply to the scratch repository, not to the corpus. Two consequences: a private repository consumes Actions minutes for its own CI, which here is one small `yq` and Prettier job, and making the corpus public later as a benchmark in its own right stays available as a decision rather than being taken now.

**A case is one merged pull request's `BASE..HEAD` diff.** This is uniform across all three sources, is recoverable from the API, and is the shape #507 replays.

**Freezing means pushing both commits into the corpus repository as branches.** `case/<id>/base` and `case/<id>/head`. `BASE` and `HEAD` hold the real upstream 40-character SHAs, which stay valid in the corpus repository because the objects are the same. The corpus stops depending on upstream never force-pushing, and the issue's four files per case are sufficient with no fifth file recording a remote.

**Rust is kept, but no Rust case can come from your own history.** `cboone/scrut` and `cboone/workmux` are forks with zero commits by you touching any `*.rs`. Rust cases therefore come from upstream `workmux`'s own fix commits and from defects planted on a clean upstream commit. A private corpus is not redistribution, so this is unremarkable now; the frozen trees still carry their upstream `LICENSE` files unchanged and `CASE.md` still records upstream and license, because that is what the decision to go public later would turn on.

**Zig is added as a sixth language.** `cboone/fosforo` is yours, public, and by a wide margin the best concurrency material available: 706 commits, 79 fix commits, 54 of them matching concurrency keywords, and 107 Copilot comments.

**`swing-left` is excluded entirely.** Its three public repositories are hiring-process artifacts, and every substantive repository in the org is private. `vote-forward` lists no repositories at all.

## Design

### Case layout, in the corpus repository

```text
cases/001-snappy-tick-refresh-race/
├── CASE.md          human narrative; no machine-read fields
├── BASE             one line, 40-hex SHA
├── HEAD             one line, 40-hex SHA
└── defects.yaml     all machine-readable metadata
```

Case IDs are `NNN-<repo>-<slug>`, zero-padded so directory order is stable. Source and defect class live in `defects.yaml`, not in the ID, so reclassifying a case does not rename its directory.

All machine-readable metadata goes in `defects.yaml`, giving the harness a single parse target and keeping `CASE.md` purely narrative:

```yaml
case: 001-snappy-tick-refresh-race
source: fix-commit # fix-commit | copilot-comment | planted
repo: https://github.com/cboone/snappy
languages: [go]
origin:
  introduced_by_pr: 3
  ground_truth: bf706bbf0000000000000000000000000000000 # the fix commit
defects:
  - id: D1
    file: internal/tui/update.go
    lines: [98, 112]
    class: concurrency # logic | error-handling | concurrency | input-handling
    severity: p1 # p1 | p2 | p3
    description: handleTick schedules a refresh while a previous refresh is in flight, so results interleave.
    added_in: initial
```

`class` is a closed set of exactly the four the issue names, so per-class recall stays meaningful. `severity` uses this repository's existing vocabulary, where `p1` is what `REVIEW.md` calls Important.

### The metadata must never reach the reviewer

`tests/data/write-realtime-audio-code-evals/README.md` line 7 already states the principle for this repository's other eval corpus: "The evaluator receives only the selected artifacts, never the criteria or a prior conclusion." The same property is required here and is easy to lose. `bin/materialize-case` builds the worktree from the frozen `HEAD` commit alone; `CASE.md` and `defects.yaml` live on the corpus repository's `main` and are never copied into it. Because each case's `HEAD` is a real pull request head that predates its fix, no commit message in the materialized history describes the defect.

### Findings the corpus does not list

A finding that inspection confirms is a real defect is appended to `defects.yaml` with `added_in: <run-id>` and a `discovered_by: <reviewer>` field, and the run report records it as a corpus miss. The scorer must exclude a defect from the recall denominator of any run that predates its `added_in`, or later additions silently depress earlier reviewers' scores and runs stop being comparable.

### Tooling, in this repository

Both scripts follow the `bin/` house style: `#!/usr/bin/env bash`, `set -euo pipefail`, `function name() {`, an `errors=0` accumulator with `error()` emitting `::error::`, and the repository-wide exit convention of 0 for success, 1 for findings, 2 for a usage or precondition error.

`bin/materialize-case` takes a case ID, a target directory, and `--corpus <dir>` defaulting to `${REVIEW_CASE_CORPUS_DIR}`. It reads `BASE` and `HEAD`, fetches either SHA if absent, adds a detached worktree at `HEAD`, and prints `WORKTREE=` and `BASE=` lines so #506's harness can pass `--base "$BASE"` straight through. It resolves the corpus through an argument or environment variable rather than relative to itself, because scrut runs each testcase from a temporary directory; `bin/list-shell-scripts` lines 16 to 20 carry that same note.

Unlike every other script in `bin/`, this one takes flags, so the model to copy is `plugins/triage-dependabot-prs/scripts/dependabot-prs` lines 26 to 53, which has the established `usage()` and `die()` shape.

`bin/validate-corpus` checks, per case: the four files exist, `BASE` and `HEAD` are single 40-hex lines, `defects.yaml` parses, `class` and `severity` are in their closed sets, `added_in` is present, and every defect's `file` exists at `HEAD`, has its `lines` range inside that file, and appears in the `BASE..HEAD` diff. That last check is what stops a stale line range from quietly surviving. It needs `yq`, which is a new tool dependency for this repository and so also needs a line in the `Makefile` help text, a setup step in CI, and a mention in `AGENTS.md`'s "Shell tools must be available on `PATH`".

`defects.yaml` is YAML because the issue specifies it. The alternative was JSON, which would inherit `bin/validate-json`'s syntax gate and the `jq` validation idiom in `plugins/publish-report-board/scripts/report-board` for free. That saving does not apply here: the case files live in a repository with its own CI, so only the validator's own parser needs `yq`.

## Work

Staged so the framework is reviewable before twenty cases rest on it.

### 1. Framework, in this repository

1. `docs/review-case-corpus.md`: the conventions of record. `CASE.md` structure, the `defects.yaml` schema with its two closed sets, the case ID scheme, the freezing procedure, the unlisted-finding rule and its scoring consequence, and the `dist/` duplicate rule below. Linked from `docs/AGENTS.md`.
1. `bin/materialize-case` and `bin/validate-corpus`.
1. `tests/fixtures/review-corpus-fixture`: prints the root of a throwaway corpus holding two cases in a real temporary git repository. A real `git init` rather than an extension of `tests/fixtures/git-worktree-stub`, which matches exact invocations by design and handles none of `worktree add`, `fetch` or `rev-parse <sha>`. `tests/fixtures/cross-reference-fixture` is the shape to copy.
1. `tests/scrut/review-corpus.md`: materialize a case and assert the worktree is at `HEAD`, that `BASE=` is reported, and that no `CASE.md` or `defects.yaml` reached the worktree. Then `validate-corpus` against a good copy plus one targeted mutation per rule, the way `tests/fixtures/validate-plugin-fixture` exercises `validate-plugins`. Report counts alongside findings so a run that checked nothing cannot pass as a vacuous zero, following `tests/scrut/repo-tooling.md` lines 317 to 349.
1. Register `MATERIALIZE_CASE_BIN`, `VALIDATE_CORPUS_BIN` and `REVIEW_CORPUS_FIXTURE_BIN` in both the `Makefile`'s `SCRUT_ENV` and `.github/workflows/ci.yml`'s `scrut-env`, per `tests/AGENTS.md`. Add any new `STUB_*` variable to `SCRUT_UNSET`. Add a `yq` setup step to CI and a `validate-corpus` note to `make help`.

### 2. The corpus repository

Create `cboone/review-case-corpus`, private, with a README stating that it holds deliberately defective code frozen for benchmarking review tools and that nothing in it should be used. Add `cases/`, its own CI running `yq` and Prettier, and a pointer to `bin/materialize-case` here.

### 3. Twenty cases

Target mix, covering all four classes within each source: Go 7, shell 5, Lean 3, Rust 2, Markdown 2, Zig 1.

**Source (a), fix commits, nine cases.** The case is the pull request that introduced the defect, resolved from the fix commit by blame; the fix is the ground truth. Candidate pool, each needing its introducing pull request resolved before it becomes a case:

- Go, concurrency and error handling: `snappy` `5e2fc30` (shared lock in `IsHeld`), `bf706bb` (auto-snapshot against refresh in `handleTick`), `d473129` (double lock release), `43856f5` (config path errors silently swallowed), `847d6f2` (nil guard on service flags)
- Go, input handling and logic: `fm` `61832f7` (multiple email IDs accepted), `3cdbe09` (unset sort and limit), `gh-problemas` `227f8a1` (width not clamped for narrow terminals), `stipple` `aa7395a` (missing cell bounds check)
- Shell, security-relevant input handling: `tmux-binding-help` `15290ae` (temp file symlink race), `0709d5e` (malformed mouse event parsing), `gh-actions` `fe4073e` (workflow-command data not encoded), `9b00cd4` (interpolated workflow inputs not bound through env)
- Shell, logic: `compbox` `583aba6` (unbounded DSR flush loop), `701350e` (backslash interpretation on screen restore)
- Lean, logic: `non-shannon-inequalities` `399c9ba` (scoped vector relabeling), `c166513` (subset order not normalized)
- Rust, concurrency: upstream `workmux` `a2c2dd6`, `f667351`, `ef84e23`, `71ab04f`; input sanitization `ff0b6ca`
- Markdown: this repository's `1ffc6147` (reference-style relative links and pipe-less tables) and `e39782f1` (unescaped fixture temp path inside a trap)

**Source (b), Copilot comments acted on, six cases.** `isResolved` is useless as a filter here: 244 of 246 Copilot threads in this repository and 50 of 51 in `snappy` are resolved. Use instead the commits titled `fix: address Copilot PR review feedback (round N)`, which pair a thread batch directly to its fix diff: `strider` `bd5f270`, `ea1e3bb`, `5589fdf`, `46f4ef2`; `gh-problemas` `cd6a3d1`, `00f1276`, `f032202`, `fbc9558`; `fm` `3dc8e11`, `aee61b6`. `HEAD` is the comment's `original_commit_id`, which is the commit the comment was anchored to and still holds the defect. Draw three from Go, one from shell, one from Lean, one from Markdown.

**Source (c), planted, five cases.** One per class at minimum. Follow the `plant-defects` discipline: commit the clean state first, plant one defect at a time, revert between plants, and record what happened rather than what was expected. Languages: Rust on a clean upstream `scrut` commit, Zig on `fosforo` for concurrency, plus Go, shell and Lean. This is the only source where every defect is known rather than only the noticed ones, so it carries the cleanest recall measurement.

## Hazards

- **The `dist/` mirror doubles every diff** in cases drawn from this repository, because `plugins/` is copied into `dist/codex/plugins/`. Each such case lists only the canonical `plugins/` path as the defect and records the mirror path in `CASE.md`. The scorer must count a finding on the mirror as neither a second catch nor a false positive. Document this in `docs/review-case-corpus.md`.
- **Markdown cases need a curation rule.** 1037 of this repository's 1285 Copilot comments land on `.md`, and nearly all are prose or consistency nits rather than defects. Admit only mechanically wrong Markdown: a relative link to a file that does not exist, a reference-style link with no definition, a table row with a dropped column, or a documented flag the code does not have.
- **Concurrency is the scarcest class.** Real material exists only in Go `snappy`, Zig `fosforo`, upstream `workmux`, and the one shell TOCTOU fix. If a real case cannot be found for a language, plant one and say so in `CASE.md` rather than reclassifying a logic defect.
- **Making the corpus public later reintroduces a redistribution decision**, because the Rust cases carry upstream `scrut` and `workmux` code. Keeping each frozen tree's `LICENSE` intact and recording provenance in `CASE.md` is what keeps that decision open rather than foreclosed.
- **Adding a Prettier-excluded Markdown area has a precedent and a cost.** If any corpus Markdown ends up in this repository, read `.markdownlint.jsonc` lines 36 to 42 first: MD049 is already disabled because `docs/plans/done/` and `dist/` are Prettier-excluded and carry mixed emphasis.

## Verification

1. `make lint`, `make validate` and `make test-scrut` in this repository, observing each final result rather than an intermediate line.
1. `bin/validate-corpus` over the populated corpus exits 0 and reports 20 cases with 0 errors. Confirm it is not vacuous by mutating one case's line range and checking that the run fails.
1. `bin/materialize-case 001-snappy-tick-refresh-race "${TMPDIR}/case"`, then confirm `git -C "${TMPDIR}/case" rev-parse HEAD` equals the case's `HEAD` file, that `git -C "${TMPDIR}/case" diff --stat "$(cat BASE)" HEAD` lists the files `defects.yaml` names, and that the worktree holds no `CASE.md` or `defects.yaml`.
1. Materialize the same case twice into separate directories and confirm both trees are identical, which is the reproducibility claim in the issue's "Done when".
1. For each planted case, diff the plant against its clean parent and confirm the changed lines match the `lines` range recorded in `defects.yaml`.
1. Run one reviewer against two materialized cases by hand before #506 exists, to confirm a reviewer can be pointed at a worktree with `--base` and produces findings that `defects.yaml` can be matched against. This is a smoke check of the interface, not a measurement.
