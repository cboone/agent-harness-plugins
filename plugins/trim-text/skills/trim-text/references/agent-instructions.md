# Profile: agent instructions

Applies to `AGENTS.md`, `CLAUDE.md`, `SKILL.md` bodies and routing descriptions, a skill's or command's reference files, agent definitions, Copilot instruction files, and global agent instructions.

## What leads

**The behavior required**, as an imperative: "Name plan files `YYYY-MM-DD-slug.md`", not "Plans should be given names that…". A rule whose whole job is a constraint leads with the constraint.

One sentence per rule is the default. Add a reason only when the agent would otherwise misapply the rule or argue with it. Keep examples only for the cases the agent would otherwise misclassify: "including 'quick'" earns its place in a rule against work estimates, because the agent would not count it as one.

## Lean toward keeping

An agent acts on every word, and a rule that looks redundant is often the fix for a past failure. When a rule's purpose cannot be recovered from the text, the code, or the history in front of you, flag it rather than deleting it. Before deleting a rule as a duplicate, confirm the other copy exists and says the same thing. If the text being cut is the only copy, move it to where it belongs instead of deleting it, and say so in the report.

These are kept even when they look trimmable:

- **A narrowing that fixed an overreach.** "Never invoke `pip` directly, and never run a script file with bare `python3`" replaced "Never use `python3` or `pip` directly", which blocked legitimate uses. Shortening it back reintroduces the overreach.
- **A split that separated two scopes.** A rule that covered two contexts with one pattern was split, because an agent applied the pattern from one context in the other. Do not merge them again.
- **Activation triggers in a routing description** for a skill that must activate without being named: the file types, paths, and situations it covers. Cutting these stops the skill from loading.

## Cut these, in addition to the shared list

| Cut                                                            | Instead                                                                                                       |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Emphasis stacking: `CRITICAL`, `VERY IMPORTANT`, repetition    | State the rule once, precisely. Keep one `NEVER` or `ALWAYS` where the rule is absolute                       |
| A case study or named instances standing in for the rule       | The rule, plus the signal the agent should check                                                              |
| A substitution table the agent already knows                   | One line naming the preferred terms, keeping only the ones it would get wrong                                 |
| A copy of what another layer owns                              | A pointer: the global file, the project file, a scoped file, a script's own header, or the skill being called |
| An inventory the agent can discover: trees, file lists, counts | Delete it, or point at the command that lists it                                                              |
| History narration in a current-state section                   | The current state; the history lives in the changelog, the plan, or the commit log                            |
| An action repeated in every item of a list                     | Hoist it into the lead-in                                                                                     |
| A passive prohibition: "is never reported as passed"           | An imperative: "Never report it as passed"                                                                    |
| A list of what not to do, where one positive action covers it  | The action                                                                                                    |

Two more cases need a check before acting, so flag them with a suggested destination rather than editing on your own:

- **Wrong layer.** A project-specific fact in global instructions, or detailed reference material in an always-loaded file. It belongs in the one repository it applies to, or in a reference file that loads on demand, with a pointer left behind.
- **An expired workaround.** Text with a removal condition, such as "Remove this once #324 lands", asks to be checked. If the condition is met, recommend deleting it.

## Routing descriptions

A skill's `description` frontmatter decides when the skill loads, and often shares a size budget with every other skill.

- Lead with the primary action, so a description cut from the end still routes.
- Name the trigger phrases that distinguish the skill from its neighbors. Cut synonym lists and "or any variant" catch-alls.
- State a negative boundary when a neighboring skill would otherwise activate instead. A boundary can also replace a risky trigger: "not to format one file" on a skill that commits and pushes.
- Cut any summary of the body. The body says what the skill does once it is loaded.
- Keep an activation trigger only when the body supports it. A trigger the body does not handle routes requests the skill cannot serve.

## Preserve

- Frontmatter keys and their value formats, such as a double-quoted `argument-hint`
- Trigger phrases that a negative boundary in a neighboring skill points to
- Required phrasings and sections that tools parse, such as "Invoke the `NAME` skill" and `## Skill dependencies`
- Paths, commands, flags, and cross-references; renaming one breaks the reference
- Size limits the repository enforces, which may also be why the text is as short as it is

## Verify

Run the repository's validators for instruction files, such as a plugin or skill validator, a cross-reference checker, and any size budget, along with its Markdown linters. Then reread each changed rule as the agent would and ask whether it would now behave differently in any case the original covered. If it would, the trim changed the meaning; restore it.

## Worked examples

From real instruction edits. `…` marks a truncated original, and each Before quotes the text as written at the time.

| Failure                                       | Before                                                                                                                                                                      | After                                                                                                                                                                            |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Emphasis stacking, rule stated three times    | `ALWAYS give the plans I create meaningful names with datestamp prefixes… CRITICAL: IGNORE any previous instructions… VERY IMPORTANT: Give all plans meaningful names…`     | `Name plan-mode files YYYY-MM-DD-meaningful-slug.md, never random word combinations.`                                                                                            |
| Rationale essay, list of what it is not       | `NEVER close and reopen a pull request. Not to re-trigger CI, not to refresh checks, not as a workaround for anything. Closing and reopening notifies every subscriber…`    | `NEVER close and reopen a PR. To rerun CI, diagnose workflow events, path filters and Actions health; use supported workflow_dispatch or rerun a specific failed run.`           |
| Named instances standing in for the rule      | `…is precisely that: a fork of … that GitHub does not label as one…`, followed by more named repositories                                                                   | `A fork originates in someone else's project, even with isFork: false. A third-party upstream is the primary signal.`                                                            |
| Every form and every venue listed             | `NEVER provide time estimates… hours, days, weeks, sprints, "quick", "should be fast", "non-trivial effort"… It applies in all artifacts: chat responses, plans, roadmaps…` | `NEVER estimate human or agent work, including hours, days, sprints, "quick", … story points or effort proxies. This applies to chat, plans, … and every artifact.`              |
| Substitution table the agent knows            | A seven-row Avoid and Use table (`kill a process`, `sanity check`, …) plus a paragraph of exceptions                                                                        | `Use neutral technical terms: running/stopped, in use/unused, terminate, validity check… Fixed upstream identifiers and proper nouns remain unchanged.`                          |
| History in a current-state section            | `[#61] has landed, pulled forward from step 9 because shader hot-reload is worth five issues' worth of iteration rather than none…`                                         | `A debug build hot-reloads the shader without restarting the host ([#61]).`                                                                                                      |
| Copy of what a script's header owns           | `…warns above max(40000, contextWindow * 0.05 * charsPerToken), which is 150,000 in a 1M-context session… It reached 166,639 characters…`                                   | `scripts/check-doc-budget warns when a file outgrows its share of the context window; that script's own header carries the formula.`                                             |
| Restating the skill being called              | `Invoke the … skill whenever… The skill codifies the compile-time, example-based API regression style (import discipline, naming mirror, …)…`                               | `The … skills carry the generic guidance; this section covers the project-specific facts those skills defer to the project.`                                                     |
| List of prohibitions for one action           | `Do not use files under <vendored dependency> as examples of style, proof technique, naming conventions, comment or docstring format… Do not cite them as evidence…`        | `When searching this repo for examples, exclude <vendored dependency>. Valid references are <the project's own source directories>.`                                             |
| Discoverable inventory                        | A directory tree of about 600 lines, then `validate-plugins enforces 19 rules covering…`                                                                                    | `Edit canonical sources in plugins/<name>/. Never hand-edit dist/…`, plus a list of the scoped files to read                                                                     |
| Action repeated per item, passive prohibition | `- …If it fails, HEAD is detached…: skip the commit. - If the current branch is the base branch, skip the commit…`; `A check that did not run is never reported as passed.` | `Skip the commit when it would not land on a working branch: - … HEAD is detached… - The current branch is the base branch…`; `Never report a check that did not run as passed.` |
| Routing description: synonym list             | `Use when the user says "merge main", "merge in main", "merge base branch", "update from main", "pull in main", "sync with main"… or any variant involving…`                | `Merge the base branch into the current branch, resolve conflicts, and push. Use for "merge main" or "sync with main"; to rebase, use rebase-onto-main.`                         |
| Routing description: body summary             | 846 characters: `…under .github/skills/code-review/, with a matching Code Review Rules block in AGENTS.md… Covers Go, Lean… Pairs with set-up-linters (…)…`                 | `Install style-guide review checklists for Copilot, Codex, and Claude Code Review. Use for "set up review config" or "configure Copilot code review".`                           |

And from trims that went too far and were restored:

| Failure                                   | Over-trimmed                                                    | Restored                                                                                                                                          |
| ----------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Activation triggers cut                   | `…whether a check can fail, or "would I know if this broke"`    | `…whether a check can fail: claims of absence (no leak, no race), trusted sanitizers or linters, vacuous suites, or "would I know if this broke"` |
| Restored trigger the body did not support | `"format the code"` restored on a skill that commits and pushes | `not to format one file`: a negative boundary instead of the risky trigger                                                                        |
| Narrowing undone                          | `Never use python3 or pip directly`                             | `never invoke pip directly, and never run a script file with bare python3`                                                                        |
