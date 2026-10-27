# Capture directory cleanup review

Issue: <https://github.com/cboone/agent-harness-plugins/issues/640>.

The shared reference now requires cleanup by this run's exact printed path, forbids pattern removal, and leaves the directory in place when its path is lost. All three consuming plugins have patch bumps; `make build` regenerated the copies successfully.

## Local review

Small-change path, one Nit round of `review-pr-with-codex`. Fresh standalone read-only runs used `gpt-6.1-sol`, high effort and an 872000-token window through the installed helper. Code and comments succeeded with no findings: clean at Nit. Errors, tests and types were omitted because only prose and manifest versions changed. Simplify was not selected. No runtime behavior changed, so no new executable test or defect planting applies.

Reviewed snapshot: `20578460924a335503bba517d6fb4830cb9bc912`. The scope comparison found no lasting changes and no scope movement. The initial repository-local helper invocation refused to launch; the installed helper ran the review. Reviewers could not reach GitHub from their read-only runs; the parent verified repository ownership and active, non-fork status before editing.

## Dependency setup and validation

The initial `make test-all` exited 2 at `yarn lint` because Yarn could not find the `node_modules` state file. TOOLING relayed authorization to run the documented install and resume the brief. `corepack yarn install --immutable` passed.

The `check-versions` skill verified forward patch bumps for all three consumers, marketplace coverage and manifest-only version ownership. `lint-and-fix --no-push` ran `make format` followed by `make lint`; both passed, with no plugin changes. Its continuation is paused at the test failure below.

## Test failure and scope stop

The resumed `make test-all` exited 2. Lint and validation passed; 30 of 31 Scrut documents passed. Only `tests/scrut/launch-workmux.md` failed, with Scrut exit 50. An isolated rerun through `make test-scrut SCRUT_TEST_DIR=tests/scrut/launch-workmux.md` also exited 2: 40 of 62 cases passed and 22 failed. Early failures report missing workmux stub output and a missing `prompt_path`; a later await-slow case reports exit 124.

The launcher, its stub and its tests have no diff against `origin/main`. TOOLING reproduced the failure independently and identified the existing load and flakiness reports: <https://github.com/cboone/agent-harness-plugins/issues/439>, <https://github.com/cboone/agent-harness-plugins/issues/397> and <https://github.com/cboone/agent-harness-plugins/issues/435>. TOOLING relayed authorization to accept the local test gate when this document is the only failure, disclose it in the PR, and require green PR CI. This exception applies here. The launcher remains outside scope and unchanged.
