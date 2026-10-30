SCRUT_TEST_DIR := tests/scrut/

# Ambient variables the launcher scripts and stubs read. Unset them so results do
# not depend on the developer's shell; every testcase that needs one sets it
# explicitly on its own env line. See issue #330.
#
# Git and Codex budget inputs belong in bin/lib/git-environment.bash; run-scrut
# clears them before Scrut starts. Add other ambient inputs to this list when
# a launcher script or fixture starts reading them.
SCRUT_UNSET := -u TMUX -u TMUX_PANE -u TMUX_TMPDIR -u ATTENTION_LOG_DIR -u WORKMUX_TMUX -u WORKMUX_TERM \
	-u WORKMUX_LAUNCH_WAIT_SECONDS -u WORKMUX_LAUNCH_TIMEOUT_SECONDS \
	-u WORKMUX_CODEX_PROMPT_SUBMIT_DELAY_SECONDS \
	-u CODEX_THREAD_ID -u CLAUDECODE -u WORKMUX_CALLER_HARNESS -u STUB_RESOURCE_SCENARIO \
	-u STUB_CAPTURE_TERM -u STUB_CAPTURE_TMUX \
	-u STUB_GH_API_FAIL -u STUB_GH_AUTH_FAIL -u STUB_GH_DIR -u STUB_GH_LOG -u STUB_COPILOT_GH_DIR \
	-u WATCH_TEST_COUNT -u WATCH_TEST_SEQUENCE -u WATCH_TEST_SLEEP_LOG -u WATCH_TEST_CALLS -u WATCH_TEST_READ_DELAY \
	-u STUB_GH_PR_VIEW -u STUB_GH_PR_VIEW_STATE -u MERGE_FLOW_INTERVAL -u MERGE_FLOW_MAX_FAILURES -u MERGE_FLOW_LIFETIME \
	-u STUB_GIT_BRANCHES -u STUB_GIT_FAIL -u STUB_GIT_INVALID_REF -u STUB_GIT_WORKTREE_PORCELAIN \
	-u STUB_GIT_WORKTREE_PORCELAIN_FILE -u STUB_WORKMUX_EXIT -u STUB_WORKMUX_SKIP_WORKTREE \
	-u STUB_WORKMUX_SLEEP -u STUB_WORKMUX_RELEASE_FIFO \
	-u STUB_STATE -u STUB_TMUX_FAIL_COMMAND -u STUB_TMUX_LOG -u STUB_TMUX_PANES \
	-u TZDIR -u WORKTREE_RESOURCES_FILE -u CLAIMS_INTERRUPT_CONTROL -u REVIEW_CHECKLISTS_DIR \
	-u LOCK_TEST_DIRECTORY -u LOCK_TEST_REAL_MKDIR -u LOCK_TEST_REAL_RMDIR -u LOCK_TEST_REAL_RM -u LOCK_TEST_MODE \
	-u LOCK_TEST_BARRIER -u LOCK_TEST_ROLE -u LOCK_TEST_REAL_SLEEP -u BUGS_HANDOFF_SUBJECT_BIN \
	-u LOCK_TEST_REPORT_ORDER -u LOCK_TEST_ORDER_MARKER \
	-u REVIEW_CASE_CORPUS_DIR -u GITHUB_REPOSITORY \
	-u CLAUDE_MARKETPLACE -u CODEX_MARKETPLACE -u CODEX_DIST_DIR -u CODEX_DIST_LABEL \
	-u CODEX_STUB_MODES -u CODEX_STUB_SENTINEL -u CODEX_STUB_LOG_DIR \
	-u STUB_CURL_DIR -u STUB_CURL_ERROR -u STUB_CURL_FAIL -u STUB_CURL_LOG -u STUB_CURL_RESPONSE -u STUB_CURL_FAIL_BODY -u STUB_CURL_TOKEN \
	-u STUB_SCRUT_PIDS -u STUB_SCRUT_CHILD_PIDS \
	-u CHAIN_CODEX_STUB_MODE \
	-u EVAL_GH_AUTH -u EVAL_GH_LOG \
	-u STUB_GH_GRAPHQL_FAIL -u BUGS_GATHER_NOW -u BUGS_GATHER_HOST -u BUGS_TEST_ZENHUB_TOKEN \
	-u BACKLOG_GATHER_NOW -u BACKLOG_GATHER_HOST \
	-u ZENHUB_GRAPHQL_TOKEN -u XDG_CACHE_HOME -u XDG_CONFIG_HOME -u XDG_STATE_HOME \
	-u PUSH_NOTIFICATION_BACKEND -u PUSH_NOTIFICATION_CONFIG -u NTFY_SERVER -u NTFY_TOPIC -u NTFY_TOKEN

# Every scrut test resolves the script or fixture it exercises through one of
# these variables. Defining them once keeps the test and update targets from
# drifting apart. CI invokes these targets and uses this same environment.
SCRUT_ENV := \
	VERSION_AUDIT_BIN="$(CURDIR)/bin/version-audit" \
	VERSION_AUDIT_STUB_BIN="$(CURDIR)/tests/fixtures/version-audit-stub" \
	NOTIFY_BIN="$(CURDIR)/plugins/notify/scripts/notify" \
	CODEX_FAILURE_WATCHER_BIN="$(CURDIR)/plugins/notify/scripts/watch-codex-failures" \
	CHECK_CODEX_FAILURES_BIN="$(CURDIR)/tests/fixtures/check-codex-failures" \
	ATTENTION_LOG_BIN="$(CURDIR)/plugins/attention-log/scripts/attention-log" \
	CHECK_NOTIFICATIONS_BIN="$(CURDIR)/tests/fixtures/check-notifications" \
	CHECK_CROSS_REFERENCES_BIN="$(CURDIR)/bin/check-cross-references" \
	BUILD_REVIEW_CHECKLISTS_BIN="$(CURDIR)/bin/build-review-checklists" \
	BUILD_SHARED_REFERENCES_BIN="$(CURDIR)/bin/build-shared-references" \
	REVIEW_CHECKLIST_FIXTURE_BIN="$(CURDIR)/tests/fixtures/review-checklist-fixture" \
	BUILD_CODEX_MARKETPLACE_BIN="$(CURDIR)/bin/build-codex-marketplace" \
	CODEX_TRANSLATION_FIXTURE_BIN="$(CURDIR)/tests/fixtures/codex-translation-fixture" \
	COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/plugins/workmux/scripts/compose-issue-prompt" \
	COMBINED_WORKTREES_CASE_BIN="$(CURDIR)/tests/fixtures/combined-worktrees-case" \
	COMBINED_REF_COLLISION_BIN="$(CURDIR)/tests/fixtures/combined-ref-collision" \
	PR_BRANCH_ISSUES_BIN="$(CURDIR)/plugins/pr/scripts/branch-issues" \
	LIST_SHELL_SCRIPTS_BIN="$(CURDIR)/bin/list-shell-scripts" \
	MATERIALIZE_CASE_BIN="$(CURDIR)/bin/materialize-case" \
	VALIDATE_CORPUS_BIN="$(CURDIR)/bin/validate-corpus" \
	REVIEW_CORPUS_FIXTURE_BIN="$(CURDIR)/tests/fixtures/review-corpus-fixture" \
	REPO_ROOT="$(CURDIR)" \
	COPILOT_REVIEW_DATA_DIR="$(CURDIR)/tests/data/copilot-reviews" \
	COPILOT_AUDIT_DATA_DIR="$(CURDIR)/tests/data/copilot-audit" \
	COPILOT_GH_STUB_BIN="$(CURDIR)/tests/fixtures/copilot-gh-stub" \
	COPILOT_SWEEP_CASE_BIN="$(CURDIR)/tests/fixtures/copilot-sweep-case" \
	COPILOT_ANCESTRY_CASE_BIN="$(CURDIR)/tests/fixtures/copilot-ancestry-case" \
	COPILOT_REPLY_CASE_BIN="$(CURDIR)/tests/fixtures/copilot-reply-case" \
	COPILOT_GH_DATA_DIR="$(CURDIR)/tests/data/copilot-gh" \
	CROSS_REFERENCE_FIXTURE_BIN="$(CURDIR)/tests/fixtures/cross-reference-fixture" \
	CHAIN_HELPER_FIXTURE_BIN="$(CURDIR)/tests/fixtures/chain-helper-fixture" \
	CHAIN_CODEX_STUB_BIN="$(CURDIR)/tests/fixtures/chain-codex-stub" \
	CATALOG_RELEASE_FIXTURE_BIN="$(CURDIR)/tests/fixtures/catalog-release-fixture" \
	ENVIRONMENT_ISOLATION_BIN="$(CURDIR)/tests/fixtures/environment-isolation" \
	CHECK_FIXTURE_ENVIRONMENTS_BIN="$(CURDIR)/bin/check-fixture-environments" \
	VALIDATE_PLUGIN_FIXTURE_BIN="$(CURDIR)/tests/fixtures/validate-plugin-fixture" \
	LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/workmux/scripts/launch-workmux" \
	DEPENDABOT_PRS_BIN="$(CURDIR)/plugins/dependabot/scripts/dependabot-prs" \
	DEPENDABOT_PRS_DATA_DIR="$(CURDIR)/tests/data/dependabot-prs" \
	GH_STUB_BIN="$(CURDIR)/tests/fixtures/gh-stub" \
	WORKTREE_GIT_STUB_BIN="$(CURDIR)/tests/fixtures/git-worktree-stub" \
	MANAGE_RESOURCE_CLAIMS_BIN="$(CURDIR)/plugins/workmux/scripts/manage-resource-claims" \
	RESOURCE_CLAIMS_INTERLEAVE_BIN="$(CURDIR)/tests/fixtures/resource-claims-interleave" \
	RESOURCE_CLAIMS_INTERLEAVE_STUB_BIN="$(CURDIR)/tests/fixtures/resource-claims-interleave-stub" \
	DIRECTORY_LOCK_STUB_BIN="$(CURDIR)/tests/fixtures/directory-lock-stub" \
	OWNER_WRITE_FAILURE_ENV="$(CURDIR)/tests/fixtures/owner-write-failure.bash" \
	CACHE_LOCK_HANDOFF_BIN="$(CURDIR)/tests/fixtures/cache-lock-handoff" \
	OWNER_LOCK_LIBRARY="$(CURDIR)/plugins/workmux/scripts/owner-lock.bash" \
	OWNER_LOCK_PROBE_BIN="$(CURDIR)/tests/fixtures/owner-lock-probe" \
	OWNER_CALL_CONTRACT_BIN="$(CURDIR)/tests/fixtures/check-owner-call-contract" \
	REPORT_BOARD_BIN="$(CURDIR)/plugins/publish-report-board/scripts/report-board" \
	REPORT_BOARD_DATA_DIR="$(CURDIR)/tests/data/report-board" \
	COPILOT_ROUNDS_REPORT_BIN="$(CURDIR)/bin/copilot-rounds-report" \
	COPILOT_ROUNDS_REPORT_DATA_DIR="$(CURDIR)/tests/data/copilot-rounds-report" \
	RECORD_TRAFFIC_BIN="$(CURDIR)/bin/record-traffic" \
	RECORD_TRAFFIC_DATA_DIR="$(CURDIR)/tests/data/record-traffic" \
	BUGS_GATHER_BIN="$(CURDIR)/plugins/publish-report-board/scripts/bugs-gather" \
	BUGS_GATHER_DATA_DIR="$(CURDIR)/tests/data/bugs-gather" \
	BACKLOG_GATHER_BIN="$(CURDIR)/plugins/publish-report-board/scripts/backlog-gather" \
	BACKLOG_GATHER_DATA_DIR="$(CURDIR)/tests/data/backlog-gather" \
	BACKLOG_GATHER_GH_STUB_BIN="$(CURDIR)/tests/fixtures/backlog-gather-gh-stub" \
	CURL_STUB_BIN="$(CURDIR)/tests/fixtures/curl-stub" \
	PUSH_NOTIFICATION_BIN="$(CURDIR)/plugins/push-notification/scripts/push-notification" \
	NTFY_CURL_STUB_BIN="$(CURDIR)/tests/fixtures/ntfy-curl-stub" \
	RESOLVE_COPILOT_THREADS_BIN="$(CURDIR)/plugins/monitor-pr/scripts/resolve-copilot-threads" \
	MONITOR_SKILL_FILE="$(CURDIR)/plugins/monitor-pr/skills/monitor/SKILL.md" \
	WATCH_CHANGES_STUB_BIN="$(CURDIR)/tests/fixtures/watch-changes-stub" \
	MERGE_FLOW_BIN="$(CURDIR)/plugins/monitor-pr/scripts/merge-flow" \
	MERGE_FLOW_DATA_DIR="$(CURDIR)/tests/data/merge-flow" \
	REVIEW_COMPLETION_BIN="$(CURDIR)/plugins/review-until-clean/scripts/check-completion" \
	SAVE_REVIEW_LEDGER_BIN="$(CURDIR)/plugins/review-until-clean/scripts/save-ledger" \
	REVIEWER_STUB_BIN="$(CURDIR)/tests/fixtures/reviewer-stub" \
	LEDGER_BARRIER_ENV="$(CURDIR)/tests/fixtures/ledger-reservation-barrier.bash" \
	LEDGER_COMMAND_STUB_BIN="$(CURDIR)/tests/fixtures/ledger-command-stub" \
	LEDGER_CONCURRENCY_BIN="$(CURDIR)/tests/fixtures/ledger-concurrency" \
	REVIEW_SUBMODULE_FIXTURE_BIN="$(CURDIR)/tests/fixtures/review-submodule-fixture" \
	REVIEW_SCOPE_BIN="$(CURDIR)/plugins/review-until-clean/scripts/review-scope" \
	REVIEW_PR_WITH_CODEX_REVIEW_SCOPE_BIN="$(CURDIR)/plugins/review-pr-with-codex/scripts/review-scope" \
	CODEX_ASPECTS_BIN="$(CURDIR)/plugins/review-pr-with-codex/scripts/codex-aspects" \
	CODEX_STUB_BIN="$(CURDIR)/tests/fixtures/codex-stub" \
	CODEX_LAUNCH_CANCEL_ENV="$(CURDIR)/tests/fixtures/codex-launch-cancel.bash" \
	RESULT_CHECK_JQ="$(CURDIR)/plugins/review-anti-patterns/skills/review-anti-patterns/references/result-check.jq" \
	RUN_SCRUT_DOCUMENTS_BIN="$(CURDIR)/bin/run-scrut-documents" \
	RUN_SCRUT_BIN="$(CURDIR)/bin/run-scrut" \
	SCRUT_STUB_BIN="$(CURDIR)/tests/fixtures/scrut-stub" \
	TMUX_STUB_BIN="$(CURDIR)/tests/fixtures/tmux-stub" \
	UNIX_SOCKET_FIXTURE_BIN="$(CURDIR)/tests/fixtures/create-unix-socket" \
	WORKMUX_STUB_BIN="$(CURDIR)/tests/fixtures/workmux-stub" \
	WORKMUX_RESOURCE_STUB_BIN="$(CURDIR)/tests/fixtures/workmux-resource-stub" \
	WORKMUX_RESOURCE_DIAGNOSTICS_BIN="$(CURDIR)/plugins/workmux/scripts/resource-diagnostics.bash" \
	WORKMUX_SANDBOX_CASE_BIN="$(CURDIR)/tests/fixtures/workmux-sandbox-case" \
	LAUNCH_SLEEP_STUB_BIN="$(CURDIR)/tests/fixtures/launch-sleep-stub"

# Resolved by bin/list-shell-scripts so a newly added script is linted without
# anyone remembering to widen a glob here.
SHELL_SCRIPTS = $(shell ./bin/list-shell-scripts)

.DEFAULT_GOAL := help

.PHONY: help lint lint-markdown lint-shell format validate validate-corpus build test-scrut test-scrut-update test-bash32 test-all

help:
	@echo "Targets:"
	@echo "  lint               Run all linters (Markdown, shell, workflows)"
	@echo "  lint-markdown      markdownlint + prettier --check"
	@echo "  lint-shell         shellcheck + shfmt on every Bash script"
	@echo "  format             Auto-fix Markdown and formatting"
	@echo "  validate           Validate JSON and plugin structure"
	@echo "  validate-corpus    Validate the review case corpus (needs REVIEW_CASE_CORPUS_DIR)"
	@echo "  build              Regenerate bundled review checklists and the Codex mirror"
	@echo "  test-scrut         Run the scrut documents in parallel (SCRUT_JOBS=N to limit)"
	@echo "  test-scrut-update  Re-record scrut expectations"
	@echo "  test-all           lint + validate + test-scrut"
	@echo "  test-bash32        Empty-list regressions under macOS /bin/bash 3.2"
	@echo ""
	@echo "Requires: yarn (via corepack), shellcheck, shfmt, actionlint, scrut."
	@echo "validate-corpus additionally needs jq and mikefarah yq v4."

lint: lint-markdown lint-shell
	@command -v actionlint > /dev/null || { echo "actionlint is required: https://github.com/rhysd/actionlint" >&2; exit 1; }
	actionlint

lint-markdown:
	yarn lint

lint-shell:
	@command -v shellcheck > /dev/null || { echo "shellcheck is required: https://www.shellcheck.net" >&2; exit 1; }
	@command -v shfmt > /dev/null || { echo "shfmt is required: https://github.com/mvdan/sh" >&2; exit 1; }
	shellcheck $(SHELL_SCRIPTS)
	shfmt -d $(SHELL_SCRIPTS)
	bin/check-fixture-environments --review-paths

format:
	yarn lint:fix
	@command -v shfmt > /dev/null && shfmt -w $(SHELL_SCRIPTS) || true

validate:
	bin/validate-json
	bin/check-fixture-environments
	env -u CODEX_REFERENCE_CONTEXT_WINDOW -u CODEX_ENABLED_SKILL_PERCENT \
		-u CODEX_OTHER_SKILL_RESERVE_TOKENS -u CLAUDE_MARKETPLACE bin/validate-plugins

# Deliberately outside validate and test-all. The corpus lives in a separate
# repository, so it is absent on most checkouts and in CI, and a merge gate that
# depends on it would fail for everyone who has not cloned it.
validate-corpus:
	bin/validate-corpus

# The checklists and shared references come first: the Codex mirror copies
# plugins/, copies included.
build:
	bin/build-review-checklists
	bin/build-shared-references
	bin/build-codex-marketplace

test-scrut:
	@command -v scrut > /dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	env $(SCRUT_UNSET) $(SCRUT_ENV) bin/run-scrut-documents "$(SCRUT_TEST_DIR)"

# One sequential scrut call, so the rewritten expectations come back in one
# stream to review.
test-scrut-update:
	@command -v scrut > /dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	env $(SCRUT_UNSET) $(SCRUT_ENV) bin/run-scrut --shell bash update --replace --assume-yes "$(SCRUT_TEST_DIR)"
	env $(SCRUT_UNSET) $(SCRUT_ENV) bin/run-scrut-documents "$(SCRUT_TEST_DIR)"

test-bash32:
	@/bin/bash -c '[[ $${BASH_VERSINFO[0]} == 3 && $${BASH_VERSINFO[1]} == 2 ]]' || \
		{ echo 'test-bash32 requires /bin/bash 3.2' >&2; exit 1; }
	$(MAKE) test-scrut SCRUT_TEST_DIR=tests/scrut/bash-empty-lists.md

test-all: lint validate test-scrut
