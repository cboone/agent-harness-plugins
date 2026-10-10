# Add the trim-text skill

## Context

`trim-comments` works well on code comments, and most of its standard is about writing rather than code: lead with what the reader needs, then the minimum why; one behavior per sentence; plain words; real values; wording that stays true; and a cut list of consequence chains, self-justification, asides and arguments for decisions already made. `trim-text` applies that standard to other kinds of text through per-kind profiles. The first two profiles are PR and issue bodies, and agent instructions. `pr` and `commit` use it while drafting.

`trim-comments` stays unchanged. Code comments are out of scope for `trim-text`, and its routing description sends them to `trim-comments`. Folding the comments profile in, and sharing the core standard between the two plugins through a `make build` copy like the review checklists, is a later decision.

## Design

### Shared standard (`SKILL.md`)

- **The standard:** lead with what the reader needs, then the minimum why, nothing else. "What" depends on the profile.
- **Write text that stays true:** no line numbers, no counts, versions, dates or "currently" unless they explain the text; anchor claims to what sits beside them.
- **Cut these:** the profile-independent rows of the `trim-comments` cut table, restated for prose: trivia, drifting facts, self-justification, consequence chains, arguments for settled decisions, two vantage points, asides about alternatives, lists of what something is not, and anything the surrounding context already says.
- **Keep these:** generalized from "someone would otherwise fix the code and break it" to "a reader would otherwise do the wrong thing", plus deliberate oddities, external constraints, required absences and necessary pointers.
- **One behavior per sentence, plain words, name real values, active voice, check for misreadings,** carried over with prose examples.
- **Preserve meaning:** every claim in the result appears in the original, none is added, and none is weakened or strengthened. This replaces tests as the main verification.
- **Do not touch:** quotations, legal and license text, changelog history, other people's text, generated files and mirrors, text that must match another file verbatim, code blocks, frontmatter keys, link targets and heading anchors that something links to.
- **Style defers** to the user's and the repository's instructions already in context.

### Profiles (`references/`)

Each profile states what "the what" is, a default length, extra cut and keep rules, what to preserve, how to verify, and worked examples from real work.

- `references/pr-and-issue-bodies.md`: PR descriptions and issue bodies, including drafts from `pr`. Preserve templates, checklists, closing keywords and issue references, section headings a repository requires, and trailers.
- `references/agent-instructions.md`: `AGENTS.md`, `CLAUDE.md`, `SKILL.md` bodies and routing descriptions, instruction references, Copilot instruction files and global instructions. Leans toward keeping and flagging, because a rule that looks redundant may be the fix for a past failure. Preserve frontmatter keys, trigger phrases, cross-references, required phrases such as "Invoke the `NAME` skill", and size limits.

Text that fits neither profile, such as pasted text or a commit message body, gets the shared standard alone.

### Inputs and outputs

| Input                                   | Output                                                                        |
| --------------------------------------- | ----------------------------------------------------------------------------- |
| File paths                              | Edit in place, verify, commit locally like `trim-comments`; never push        |
| Pasted text or a draft from a skill     | Return the rewrite; edit nothing                                              |
| A PR or issue reference                 | Show a before-and-after diff, then ask before `gh pr edit` or `gh issue edit` |
| No argument, on a branch with a PR open | Treat as that PR's body, as above                                             |

Options: paths or a PR or issue reference, `--profile <name>` to override detection, `--dry-run` and `--no-commit`. Existing commit messages are out of scope, since rewriting them needs an amend or a rebase.

### Composition with `pr` and `commit`

- `pr` step 7: after drafting the body and before writing the tmpfile, invoke `trim-text` on the draft with the PR profile, passing a continuation block. Optional dependency: when it is missing, use the draft unchanged and say so in the final report. `pr` never prompts, so the draft mode never asks.
- `commit` step 5: when the message has a body, invoke `trim-text` on the body only, with the shared standard. The subject keeps `commit`'s own rules. Optional, with the same fallback.

## Worked examples

Sourced from real work, as `trim-comments`' were: GitHub edit history of PR bodies, review feedback on PR descriptions, git history of instruction files in this and other `cboone` repositories, the global instructions history, and session transcripts. Client (`swing-left`) material is anonymized before it is used. Classes without a real example are discussed with Chris before inventing one.

## Changes

1. `plugins/trim-text/`: `.claude-plugin/plugin.json` at `1.0.0`, `README.md`, `skills/trim-text/SKILL.md` and the two profile references.
2. `.claude-plugin/marketplace.json`: register under `writing`; root `README.md` row in the Writing table.
3. `plugins/pr/`: step 7 composition, `## Skill dependencies` optional entry, README mention; `1.9.8` to `1.10.0`.
4. `plugins/commit/`: step 5 composition, new `## Skill dependencies` section, README mention; `1.3.2` to `1.4.0`.
5. `make build` and commit the regenerated mirrors.

Load `write-markdown` before Markdown edits. Commit at logical boundaries with signed Conventional Commits.

## Verification

- `make build`, then `make test-all`, observing the final result; read the Codex skill inventory line for the description budget.
- Run the `check-versions` skill.
- Dry-run the skill on real samples: one PR body from the examples, and one instruction file in this repository, checking the meaning-preservation rule by hand.
