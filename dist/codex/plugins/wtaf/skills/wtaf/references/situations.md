# Situations

Classify the situation before reading widely. It decides which sources matter and what the summary emphasizes.

## Repository patterns

Judge the pattern from signals in the repository, not from its owner's name. When signals conflict or are absent, treat the repository as personal and say nothing about the classification.

### Team or client repositories

Signals:

- A default branch other than `main`, such as `develop` or `master`, or a release branch flow.
- `CODEOWNERS`, required reviewers, or several recent commit authors.
- Deploy workflows, GitHub environments, release tags per app, or staging and production configuration.
- Tracker links or badges for a board outside GitHub Issues, such as ZenHub, Linear, or Jira.
- Branch names that start with an issue number, such as `4404-email-hash-secret`.
- Runbooks, RFCs, or incident docs under `docs/`.

Emphasize:

- Deploy state per environment, and whether production was checked directly rather than inferred from a log.
- Approvals and who the work waits on.
- Which items are filed as issues and which exist only in the conversation.
- The epic or parent issue the branch serves, and its other open children.
- Runbook or RFC progress when the work follows one.

Offer, when it fits, a short version the user can share with colleagues.

### Personal projects

Signals: a single author, `main` as the base, plans and roadmaps under `docs/plans/`, milestones on GitHub, reviews under `docs/reviews/`.

Emphasize:

- Phase, step, or milestone progress against the roadmap.
- Manual verification lists still to run, restated in full.
- Automated review rounds (such as Copilot) and CI on the PR.
- Dependencies on sibling repositories when the conversation mentions them.
- What is available to work on next once the current work lands.

## One-off situations

- **Home directory, scratch directory, or no repository.** The conversation is the main source. Mention any plans or notes in the directory, and skip the repository and GitHub steps without apology.
- **Fresh session, first prompt.** There is no conversation to recover. Build the story from the plan, commits, PR, and issue, and say that the summary comes from the repository alone.
- **After a compaction or resume.** Treat the compaction summary as the conversation, and verify its claims against the repository, since it may be stale.
- **After a gap ("it's a new day", "new week").** Things changed while the session was idle. Fetch remote-tracking refs, re-read PR and issue state, and report what moved since the last recorded state.
- **The user reports an outside change ("1714 is merged", "I deployed").** Verify it, then reframe the status around it.
- **Mid-merge, mid-rebase, cherry-pick, or detached HEAD.** Lead with that state in the verdict, since it blocks most next steps.
- **Changes the session did not make.** Uncommitted edits, commits by another author, or files touched by another agent. Report them as unexpected, with who or what made them when the history shows it. Never assume the user made them.
- **Several worktrees ("what is this worktree versus that one?").** For each worktree, give its path, branch, plan, PR, and last commit, then say how they relate: the same issue split in parts, a dependency, or unrelated work.
- **A lost earlier session.** Look for it as `./references/sources.md` describes. If it cannot be found, say so and fall back to the issue and plan it concerned.
- **Waiting on CI, approval, or a build.** Report what is pending and on whom, and suggest work that can proceed meanwhile.
- **Background work still running.** Name each task or monitor and its last known state; never claim a result that has not arrived.
- **The user's terms differ from the plan's.** Use the plan's term and note the difference once ("the plan calls these steps").
- **The user asks one narrow question.** Answer that question first, then give the rest of the summary in a line or two.
