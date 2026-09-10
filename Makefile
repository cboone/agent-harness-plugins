SCRUT_TEST_DIR := tests/scrut/

# Ambient variables the launcher scripts and stubs read. Unset them so results do
# not depend on the developer's shell; every testcase that needs one sets it
# explicitly on its own env line. See issue #330.
#
# This list is maintained by hand: add an entry whenever a launcher script or a
# fixture under tests/fixtures/ starts reading a new variable, or the suite
# silently becomes sensitive to the developer's environment again.
SCRUT_UNSET := -u TMUX -u TMUX_TMPDIR -u WORKMUX_TMUX -u WORKMUX_TERM \
	-u WORKMUX_LAUNCH_WAIT_SECONDS -u WORKMUX_CODEX_PROMPT_SUBMIT_DELAY_SECONDS \
	-u STUB_CAPTURE_TERM -u STUB_CAPTURE_TMUX -u STUB_GIT_WORKTREE_PORCELAIN \
	-u STUB_STATE -u STUB_TMUX_FAIL_COMMAND -u STUB_TMUX_LOG -u STUB_TMUX_PANES

# Every scrut test resolves the script or fixture it exercises through one of
# these variables. Defining them once keeps the test and update targets from
# drifting apart, and .github/workflows/ci.yml passes the same list to the
# reusable scrut workflow.
SCRUT_ENV := \
	CHECK_CROSS_REFERENCES_BIN="$(CURDIR)/bin/check-cross-references" \
	COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/compose-issue-prompt" \
	COMPUTE_CATALOG_STATE_BIN="$(CURDIR)/bin/compute-catalog-state" \
	LIST_SHELL_SCRIPTS_BIN="$(CURDIR)/bin/list-shell-scripts" \
	REPO_ROOT="$(CURDIR)" \
	COPILOT_REVIEW_DATA_DIR="$(CURDIR)/tests/data/copilot-reviews" \
	CROSS_REFERENCE_FIXTURE_BIN="$(CURDIR)/tests/fixtures/cross-reference-fixture" \
	CREATE_WORKTREE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree/scripts/launch-workmux" \
	CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/launch-workmux" \
	GIT_WORKTREE_STUB_BIN="$(CURDIR)/tests/fixtures/git-worktree-stub" \
	RESOLVE_COPILOT_THREADS_BIN="$(CURDIR)/plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads" \
	TMUX_STUB_BIN="$(CURDIR)/tests/fixtures/tmux-stub" \
	UNIX_SOCKET_FIXTURE_BIN="$(CURDIR)/tests/fixtures/create-unix-socket" \
	WORKMUX_STUB_BIN="$(CURDIR)/tests/fixtures/workmux-stub"

# Resolved by bin/list-shell-scripts so a newly added script is linted without
# anyone remembering to widen a glob here.
SHELL_SCRIPTS = $(shell ./bin/list-shell-scripts)

.DEFAULT_GOAL := help

.PHONY: help lint lint-markdown lint-shell format validate build test-scrut test-scrut-update test-all

help:
	@echo "Targets:"
	@echo "  lint               Run all linters (Markdown, shell, workflows)"
	@echo "  lint-markdown      markdownlint + prettier --check"
	@echo "  lint-shell         shellcheck + shfmt on every Bash script"
	@echo "  format             Auto-fix Markdown and formatting"
	@echo "  validate           Validate JSON and plugin structure"
	@echo "  build              Regenerate the Codex and OpenCode mirrors"
	@echo "  test-scrut         Run the scrut suites"
	@echo "  test-scrut-update  Re-record scrut expectations"
	@echo "  test-all           lint + validate + test-scrut"
	@echo ""
	@echo "Requires: yarn (via corepack), shellcheck, shfmt, actionlint, scrut."

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

build:
	bin/build-codex-marketplace
	bin/build-opencode-mirror

test-scrut:
	@command -v scrut > /dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	env $(SCRUT_UNSET) $(SCRUT_ENV) scrut --shell bash test "$(SCRUT_TEST_DIR)"

test-scrut-update:
	@command -v scrut > /dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	env $(SCRUT_UNSET) $(SCRUT_ENV) scrut --shell bash update --replace --assume-yes "$(SCRUT_TEST_DIR)"

test-all: lint validate test-scrut
