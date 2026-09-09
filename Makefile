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

.PHONY: test-scrut test-scrut-update test-all

test-scrut:
	@command -v scrut >/dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	env $(SCRUT_UNSET) \
	COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/compose-issue-prompt" \
	CREATE_WORKTREE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree/scripts/launch-workmux" \
	CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/launch-workmux" \
	GIT_WORKTREE_STUB_BIN="$(CURDIR)/tests/fixtures/git-worktree-stub" \
	TMUX_STUB_BIN="$(CURDIR)/tests/fixtures/tmux-stub" \
	UNIX_SOCKET_FIXTURE_BIN="$(CURDIR)/tests/fixtures/create-unix-socket" \
	WORKMUX_STUB_BIN="$(CURDIR)/tests/fixtures/workmux-stub" \
	scrut --shell bash test "$(SCRUT_TEST_DIR)"

test-scrut-update:
	@command -v scrut >/dev/null || { echo "scrut is required: https://github.com/facebookincubator/scrut" >&2; exit 1; }
	env $(SCRUT_UNSET) \
	COMPOSE_ISSUE_PROMPT_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/compose-issue-prompt" \
	CREATE_WORKTREE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree/scripts/launch-workmux" \
	CREATE_WORKTREE_FROM_ISSUE_LAUNCH_WORKMUX_BIN="$(CURDIR)/plugins/create-worktree-from-issue/scripts/launch-workmux" \
	GIT_WORKTREE_STUB_BIN="$(CURDIR)/tests/fixtures/git-worktree-stub" \
	TMUX_STUB_BIN="$(CURDIR)/tests/fixtures/tmux-stub" \
	UNIX_SOCKET_FIXTURE_BIN="$(CURDIR)/tests/fixtures/create-unix-socket" \
	WORKMUX_STUB_BIN="$(CURDIR)/tests/fixtures/workmux-stub" \
	scrut --shell bash update --replace --assume-yes "$(SCRUT_TEST_DIR)"

test-all: test-scrut
