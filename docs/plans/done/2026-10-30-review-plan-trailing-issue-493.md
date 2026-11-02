# Match trailing plan issue numbers

Fix [issue 493](https://github.com/cboone/agent-harness-plugins/issues/493) without changing existing exact matches or newest-file fallback behavior.

## Prior art

- The existing `review-plan` rules normalize complete subjects but have no executable selection coverage. Extend those rules and give the skill a read-only comparison helper so tests exercise the shipped behavior.
- The repository's `pr/scripts/branch-issues` extracts several issue identities from branch segments. Reusing it would broaden the single-prefix contract; retain the existing category and prefix grammar instead.
- [Spec Kit's Git helper](https://github.com/github/spec-kit/blob/main/extensions/git/scripts/bash/git-common.sh) strips an optional namespace and validates numeric branch prefixes. Its [core feature lookup](https://github.com/github/spec-kit/blob/main/scripts/bash/common.sh) uses explicit feature state. Neither resolves dated plan basenames under this skill's existing contract. Keep branch-derived identity local and compare full subjects.

## Implementation

1. Retain the branch issue digits before removing its one optional prefix. Normalize plan basenames as today. Accept exact normalized equality first; otherwise accept only the complete branch subject followed by one hyphen and those same issue digits. A branch without an issue prefix gets no suffix tolerance. Both filename forms work by removing the leading prefix first, then applying this conditional trailing comparison once. Wrong issue suffixes and subject near-misses do not match.
1. Ship a Bash 3.2 compatible, read-only comparator in `plugins/review-plan/scripts/`, invoked by the skill. Document its inputs, outputs and failure handling. Update the README and bump the patch version from `1.1.0` to `1.1.1`; regenerate mirrors with `make build`.
1. Register Scrut coverage for absent, leading, trailing and both issue forms, numeric subjects, wrong suffixes, near-misses, case/punctuation normalization and single-removal boundaries. Commit tests before planting defects, then restore the real helper after each plant and record observed failures.

## Validation and handoff

Use the full local review order: anti-patterns and report-only simplify in parallel, focused Codex aspects, trims, Semgrep against the actual merge base in a disposable shared clone, then `lint-and-fix --no-push`. Record rounds and findings in the review ledger. Run `make test-all` without silent mode and `check-versions`. The known baseline lint failure in `tests/fixtures/review-submodule-fixture` remains outside scope and must be reported separately. Tidy to logical signed commits and verify the exact tree. Push and open a ready PR; report the review précis to TOOLING by mailbox. TOOLING merges. No live configuration changes.
