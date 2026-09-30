# Review until clean: feature/add-fast-option-to-colleague-review

Base: `origin/main` (`d8a752663392fccc9c8e6158ca6b47535b230b87`)
Reviewer: Claude Code (`/code-review`), then Codex CLI
Rounds: 2 of 3
Status: failed

## Round 1

Snapshot: `fb656c316e783e2abe830bf7d5c728e5c6035323`
Invocation: `claude -p '/code-review medium d8a752663392fccc9c8e6158ca6b47535b230b87...HEAD' --disallowed-tools Edit Write NotebookEdit Bash`
Coverage: partial. Claude reported that it could not run `git diff` and read only the canonical `SKILL.md`, plugin `README.md`, and `plugin.json`. The full committed range was not reviewed.

Reviewer reply, verbatim:

```text
I found two issues, both in the skill's instruction text. The session had no shell, so I couldn't run `git diff`. I read the files the plan says this branch changes instead: `SKILL.md`, the plugin `README.md` and `plugin.json`. The version bump to `1.1.0` and the Codex mirror both look consistent.

1. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:366`: The fast-mode example contradicts step 6. It lists the missing #118 backoff cap only under Requirements, and its Before merge list and verdict count just the one bug. Step 6 says a core requirement left unmet belongs in Before merge, and fast mode only reports core requirement gaps. Suppose a PR's only problem is a missing core requirement. A model copying this example would leave Before merge empty and return "No blockers found" when the answer should be "Needs changes".
2. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:314`: The rules for keeping the fast-mode Requirements line conflict. Step 7 keeps it only "when sources were skipped". Line 44 and step 6 (line 306) say to keep a source-coverage line in fast mode whether or not any source was skipped. On a PR where every source was read and nothing is missing, the two rules disagree, so the coverage line will appear in some runs and not others.
```

- [x] **F1** Important. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:366`. The report example omits a missing core requirement from Before merge and understates the verdict.
      Evidence: the fast example names the missing #118 backoff cap under Requirements, while step 6 defines a core requirement left unmet as a Before merge concern. The thorough example and README repeat the same mismatch.
      Fixed: added the missing cap to both skill examples and the README example, and updated the verdict counts.
- [x] **F2** Important. `plugins/review-colleague-pr/skills/review-colleague-pr/SKILL.md:314`. The fast Requirements coverage rule disagrees about whether a line is required when no source was skipped.
      Evidence: line 44 and step 6 request a coverage line even without a gap; step 7 requires one only when sources were skipped.
      Fixed: the fast Requirements coverage line is now required when sources were skipped, including when the requirements read appear met.

Round 1 was partial because the Claude backend could not run `git diff` with shell access denied. Codex CLI is selected for the next round to cover all four scope buckets in a read-only sandbox.

## Round 2

Snapshot: `3d994f54f32b2c52fda1158476ba9e97eef1c4fc`
Invocation: `codex exec --sandbox read-only --ephemeral --output-schema <temporary schema> -o <temporary findings> <full-scope prompt> < /dev/null`
Coverage: none. The command exited 1 before it could review the scope. It produced no findings file.

Backend output, verbatim:

```text
WARNING: proceeding, even though we could not create PATH aliases: Operation not permitted (os error 1)
Reading additional input from stdin...
Error: failed to initialize in-process app-server client: Operation not permitted (os error 1)
```

## Result

Review-until-clean status: `failed`. F1 and F2 from the partial Claude round were fixed. The Codex round did not produce a review, so the current snapshot has no full-scope clean result.

The Claude backend's committed-diff coverage defect is tracked in [issue #538](https://github.com/cboone/agent-harness-plugins/issues/538).
