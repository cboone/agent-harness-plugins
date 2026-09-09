SCRUT_TEST_DIR := tests/scrut/

.PHONY: test-scrut test-scrut-update test-all

test-scrut:
	@command -v scrut >/dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/compose-issue-prompt" \
	COPILOT_REVIEW_DATA_DIR="$(CURDIR)/tests/data/copilot-reviews" \
	CREATE_WORKTREE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree/scripts/launch-workmux" \
	CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/launch-workmux" \
	GIT_WORKTREE_STUB_BIN="$(CURDIR)/tests/fixtures/git-worktree-stub" \
	RESOLVE_COPILOT_THREADS_BIN="$(CURDIR)/plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads" \
	TMUX_STUB_BIN="$(CURDIR)/tests/fixtures/tmux-stub" \
	UNIX_SOCKET_FIXTURE_BIN="$(CURDIR)/tests/fixtures/create-unix-socket" \
	WORKMUX_STUB_BIN="$(CURDIR)/tests/fixtures/workmux-stub" \
	scrut --shell bash test "$(SCRUT_TEST_DIR)"

test-scrut-update:
	@command -v scrut >/dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/compose-issue-prompt" \
	COPILOT_REVIEW_DATA_DIR="$(CURDIR)/tests/data/copilot-reviews" \
	CREATE_WORKTREE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree/scripts/launch-workmux" \
	CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/launch-workmux" \
	GIT_WORKTREE_STUB_BIN="$(CURDIR)/tests/fixtures/git-worktree-stub" \
	RESOLVE_COPILOT_THREADS_BIN="$(CURDIR)/plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads" \
	TMUX_STUB_BIN="$(CURDIR)/tests/fixtures/tmux-stub" \
	UNIX_SOCKET_FIXTURE_BIN="$(CURDIR)/tests/fixtures/create-unix-socket" \
	WORKMUX_STUB_BIN="$(CURDIR)/tests/fixtures/workmux-stub" \
	scrut --shell bash update --replace --assume-yes "$(SCRUT_TEST_DIR)"

test-all: test-scrut
