SCRUT_TEST_DIR := tests/scrut/

.PHONY: test-scrut test-scrut-update test-all

test-scrut:
	@command -v scrut >/dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/compose-issue-prompt" \
	CREATE_WORKTREE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree/scripts/launch-workmux" \
	CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/launch-workmux" \
	WORKMUX_STUB_BIN="$(CURDIR)/tests/fixtures/workmux-stub" \
	scrut --shell bash test "$(SCRUT_TEST_DIR)"

test-scrut-update:
	@command -v scrut >/dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/compose-issue-prompt" \
	CREATE_WORKTREE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree/scripts/launch-workmux" \
	CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/launch-workmux" \
	WORKMUX_STUB_BIN="$(CURDIR)/tests/fixtures/workmux-stub" \
	scrut --shell bash update --replace --assume-yes "$(SCRUT_TEST_DIR)"

test-all: test-scrut
