SCRUT_TEST_DIR := tests/scrut/

# Ambient variables the launcher scripts and stubs read. Unset them so results do
# not depend on the developer's shell; every testcase that needs one sets it
# explicitly on its own env line. See issue #330.
#
# This list is maintained by hand: add an entry whenever a launcher script or a
# fixture under tests/fixtures/ starts reading a new variable, or the suite
# silently becomes sensitive to the developer's environment again.
SCRUT_UNSET := -u TMUX -u TMUX_TMPDIR -u WORKMUX_TMUX -u WORKMUX_TERM \
	-u WORKMUX_LAUNCH_WAIT_SECONDS -u WORKMUX_LAUNCH_TIMEOUT_SECONDS \
	-u WORKMUX_CODEX_PROMPT_SUBMIT_DELAY_SECONDS \
	-u STUB_CAPTURE_TERM -u STUB_CAPTURE_TMUX \
	-u STUB_GH_API_FAIL -u STUB_GH_AUTH_FAIL -u STUB_GH_DIR -u STUB_GH_LOG -u STUB_COPILOT_GH_DIR \
	-u STUB_GIT_BRANCHES -u STUB_GIT_FAIL -u STUB_GIT_INVALID_REF -u STUB_GIT_WORKTREE_PORCELAIN \
	-u STUB_GIT_WORKTREE_PORCELAIN_FILE -u STUB_WORKMUX_EXIT -u STUB_WORKMUX_SKIP_WORKTREE \
	-u STUB_WORKMUX_SLEEP \
	-u STUB_STATE -u STUB_TMUX_FAIL_COMMAND -u STUB_TMUX_LOG -u STUB_TMUX_PANES \
	-u TZDIR -u WORKTREE_RESOURCES_FILE -u REVIEW_CHECKLISTS_DIR \
	-u REVIEW_CASE_CORPUS_DIR -u GITHUB_REPOSITORY \
	-u CODEX_REFERENCE_CONTEXT_WINDOW -u CODEX_ENABLED_SKILL_PERCENT -u CODEX_OTHER_SKILL_RESERVE_TOKENS \
	-u STUB_CURL_DIR -u STUB_CURL_ERROR -u STUB_CURL_FAIL -u STUB_CURL_LOG -u STUB_CURL_TOKEN \
	-u STUB_SCRUT_PIDS \
	-u STUB_GH_GRAPHQL_FAIL -u BUGS_GATHER_NOW -u BUGS_TEST_ZENHUB_TOKEN \
	-u ZENHUB_GRAPHQL_TOKEN -u XDG_CACHE_HOME -u XDG_CONFIG_HOME

# Every scrut test resolves the script or fixture it exercises through one of
# these variables. Defining them once keeps the test and update targets from
# drifting apart, and .github/workflows/ci.yml passes the same list to the
# reusable scrut workflow.
SCRUT_ENV := \
	NOTIFY_BIN="$(CURDIR)/plugins/notify/scripts/notify" \
	CHECK_NOTIFICATIONS_BIN="$(CURDIR)/tests/fixtures/check-notifications" \
	CHECK_CROSS_REFERENCES_BIN="$(CURDIR)/bin/check-cross-references" \
	BUILD_REVIEW_CHECKLISTS_BIN="$(CURDIR)/bin/build-review-checklists" \
	REVIEW_CHECKLIST_FIXTURE_BIN="$(CURDIR)/tests/fixtures/review-checklist-fixture" \
	BUILD_CODEX_MARKETPLACE_BIN="$(CURDIR)/bin/build-codex-marketplace" \
	CODEX_TRANSLATION_FIXTURE_BIN="$(CURDIR)/tests/fixtures/codex-translation-fixture" \
	COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/plugins/address-issue-in-worktree/scripts/compose-issue-prompt" \
	CREATE_WORKTREE_COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/plugins/create-worktree/scripts/compose-issue-prompt" \
	LIST_SHELL_SCRIPTS_BIN="$(CURDIR)/bin/list-shell-scripts" \
	MATERIALIZE_CASE_BIN="$(CURDIR)/bin/materialize-case" \
	VALIDATE_CORPUS_BIN="$(CURDIR)/bin/validate-corpus" \
	REVIEW_CORPUS_FIXTURE_BIN="$(CURDIR)/tests/fixtures/review-corpus-fixture" \
	REPO_ROOT="$(CURDIR)" \
	COPILOT_REVIEW_DATA_DIR="$(CURDIR)/tests/data/copilot-reviews" \
	COPILOT_AUDIT_DATA_DIR="$(CURDIR)/tests/data/copilot-audit" \
	COPILOT_GH_STUB_BIN="$(CURDIR)/tests/fixtures/copilot-gh-stub" \
	COPILOT_GH_DATA_DIR="$(CURDIR)/tests/data/copilot-gh" \
	CROSS_REFERENCE_FIXTURE_BIN="$(CURDIR)/tests/fixtures/cross-reference-fixture" \
	CATALOG_RELEASE_FIXTURE_BIN="$(CURDIR)/tests/fixtures/catalog-release-fixture" \
	VALIDATE_PLUGIN_FIXTURE_BIN="$(CURDIR)/tests/fixtures/validate-plugin-fixture" \
	CREATE_WORKTREE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree/scripts/launch-workmux" \
	ADDRESS_ISSUE_IN_WORKTREE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/address-issue-in-worktree/scripts/launch-workmux" \
	DEPENDABOT_PRS_BIN="$(CURDIR)/plugins/triage-dependabot-prs/scripts/dependabot-prs" \
	DEPENDABOT_PRS_DATA_DIR="$(CURDIR)/tests/data/dependabot-prs" \
	GH_STUB_BIN="$(CURDIR)/tests/fixtures/gh-stub" \
	GIT_WORKTREE_STUB_BIN="$(CURDIR)/tests/fixtures/git-worktree-stub" \
	MANAGE_RESOURCE_CLAIMS_BIN="$(CURDIR)/plugins/address-issue-in-worktree/scripts/manage-resource-claims" \
	CREATE_WORKTREE_MANAGE_RESOURCE_CLAIMS_BIN="$(CURDIR)/plugins/create-worktree/scripts/manage-resource-claims" \
	REPORT_BOARD_BIN="$(CURDIR)/plugins/publish-report-board/scripts/report-board" \
	REPORT_BOARD_DATA_DIR="$(CURDIR)/tests/data/report-board" \
	COPILOT_ROUNDS_REPORT_BIN="$(CURDIR)/bin/copilot-rounds-report" \
	COPILOT_ROUNDS_REPORT_DATA_DIR="$(CURDIR)/tests/data/copilot-rounds-report" \
	RECORD_TRAFFIC_BIN="$(CURDIR)/bin/record-traffic" \
	RECORD_TRAFFIC_DATA_DIR="$(CURDIR)/tests/data/record-traffic" \
	BUGS_GATHER_BIN="$(CURDIR)/plugins/publish-report-board/scripts/bugs-gather" \
	BUGS_GATHER_DATA_DIR="$(CURDIR)/tests/data/bugs-gather" \
	CURL_STUB_BIN="$(CURDIR)/tests/fixtures/curl-stub" \
	RESOLVE_COPILOT_THREADS_BIN="$(CURDIR)/plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads" \
	MONITOR_PR_RESOLVE_COPILOT_THREADS_BIN="$(CURDIR)/plugins/monitor-pr/scripts/resolve-copilot-threads" \
	REVIEW_SCOPE_BIN="$(CURDIR)/plugins/review-until-clean/scripts/review-scope" \
	RUN_SCRUT_DOCUMENTS_BIN="$(CURDIR)/bin/run-scrut-documents" \
	SCRUT_STUB_BIN="$(CURDIR)/tests/fixtures/scrut-stub" \
	GIT_CONFIG_GLOBAL=/dev/null \
	GIT_CONFIG_SYSTEM=/dev/null \
	TMUX_STUB_BIN="$(CURDIR)/tests/fixtures/tmux-stub" \
	UNIX_SOCKET_FIXTURE_BIN="$(CURDIR)/tests/fixtures/create-unix-socket" \
	WORKMUX_STUB_BIN="$(CURDIR)/tests/fixtures/workmux-stub"

# Resolved by bin/list-shell-scripts so a newly added script is linted without
# anyone remembering to widen a glob here.
SHELL_SCRIPTS = $(shell ./bin/list-shell-scripts)

.DEFAULT_GOAL := help

.PHONY: help lint lint-markdown lint-shell format validate validate-corpus build test-scrut test-scrut-update test-all

help:
	@echo "Targets:"
	@echo "  lint               Run all linters (Markdown, shell, workflows)"
	@echo "  lint-markdown      markdownlint + prettier --check"
	@echo "  lint-shell         shellcheck + shfmt on every Bash script"
	@echo "  format             Auto-fix Markdown and formatting"
	@echo "  validate           Validate JSON and plugin structure"
	@echo "  validate-corpus    Validate the review case corpus (needs REVIEW_CASE_CORPUS_DIR)"
	@echo "  build              Regenerate bundled review checklists and the Codex and OpenCode mirrors"
	@echo "  test-scrut         Run the scrut documents in parallel (SCRUT_JOBS=N to limit)"
	@echo "  test-scrut-update  Re-record scrut expectations"
	@echo "  test-all           lint + validate + test-scrut"
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

format:
	yarn lint:fix
	@command -v shfmt > /dev/null && shfmt -w $(SHELL_SCRIPTS) || true

validate:
	bin/validate-json
	bin/validate-plugins

# Deliberately outside validate and test-all. The corpus lives in a separate
# repository, so it is absent on most checkouts and in CI, and a merge gate that
# depends on it would fail for everyone who has not cloned it.
validate-corpus:
	bin/validate-corpus

# The checklists come first: the Codex mirror copies plugins/, copies included.
build:
	bin/build-review-checklists
	bin/build-codex-marketplace
	bin/build-opencode-mirror

test-scrut:
	@command -v scrut > /dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	env $(SCRUT_UNSET) $(SCRUT_ENV) bin/run-scrut-documents "$(SCRUT_TEST_DIR)"

# One sequential scrut call, so the rewritten expectations come back in one
# stream to review.
test-scrut-update:
	@command -v scrut > /dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	env $(SCRUT_UNSET) $(SCRUT_ENV) scrut --shell bash update --replace --assume-yes "$(SCRUT_TEST_DIR)"

test-all: lint validate test-scrut
