# Plugin development

Read this before changing plugin sources, catalog metadata or plugin documentation. Unless the surrounding text says otherwise, paths in code spans are relative to the repository root. See [the root instructions](../AGENTS.md) for validation and writing conventions.

## Plugin layout

A typical skill plugin looks like:

```text
plugins/commit/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── commit/
        └── SKILL.md
```

Skills with longer reference material add a `references/` subdirectory:

```text
plugins/handle-secrets/
├── .claude-plugin/
│   └── plugin.json
├── README.md
└── skills/
    └── handle-secrets/
        ├── SKILL.md
        └── references/
            ├── anti-patterns.md
            ├── checklist.md
            └── ...
```

A skill can ship executable helpers too. `address-issue-in-worktree`, `create-worktree`, `publish-report-board`, `resolve-copilot-pr-feedback`, and `triage-dependabot-prs` each bundle a `scripts/` directory that the skill body invokes:

```text
plugins/create-worktree/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── scripts/
│   ├── compose-issue-prompt
│   ├── launch-workmux
│   └── manage-resource-claims
└── skills/
    └── create-worktree/
        └── SKILL.md
```

`create-worktree` and `address-issue-in-worktree` ship byte-identical copies of all three scripts. Rule 18 requires every `${CLAUDE_PLUGIN_ROOT}/scripts/NAME` reference in a `SKILL.md` body to resolve inside its own plugin, so the scripts cannot be shared across plugins. Three testcases in `tests/scrut/repo-tooling.md` fail if the copies drift, so change one and copy it to the other.

`resolve-copilot-pr-feedback` and `monitor-pr` share `resolve-copilot-threads` the same way, guarded by a fourth testcase. `monitor-pr` calls only its read-only `fetch` and `fetch-reviews` commands, to observe Copilot's findings and format drift before it decides whether to dispatch to the resolver. Sharing the file rather than restating the parser's clean-or-drift rules in prose is the point: one classifier, so the watch and the resolver cannot disagree about what counts as clean.

A skill refers to each script it ships by its plugin-root path, so `create-worktree` names `${CLAUDE_PLUGIN_ROOT}/scripts/compose-issue-prompt`, `${CLAUDE_PLUGIN_ROOT}/scripts/launch-workmux` and `${CLAUDE_PLUGIN_ROOT}/scripts/manage-resource-claims`, and `resolve-copilot-pr-feedback` and `monitor-pr` each name `${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads` against their own copy. Claude Code substitutes that placeholder with the installed plugin root. Rule 18 of `bin/validate-plugins` scans only `SKILL.md` bodies, checking that every such reference resolves to a shipped, executable file and rejecting version-blind locator globs like `**/PLUGIN/scripts/NAME`. It does not scan reference material. Bundled scripts belong in `tests/scrut/`.

A script can carry files of its own. `publish-report-board` keeps its page templates in a plugin-root `templates/` directory, and its `report-board` script finds them relative to its own location rather than through `${CLAUDE_PLUGIN_ROOT}`, so the same lookup works in Codex CLI and OpenCode, where the placeholder is not substituted. Prettier formats those templates like any other HTML, which is why the data placeholder in each is a JSON string that still parses before rendering.

A hook plugin that targets all three harnesses (Claude Code, Codex CLI, and OpenCode) carries split manifests, harness-specific entry points, and any helper scripts or assets:

```text
plugins/notify/
├── .claude-plugin/
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── README.md
├── assets/
├── hooks/
│   ├── codex.hooks.json
│   └── hooks.json
├── opencode/
│   └── index.ts
└── scripts/
    ├── focus-pane
    └── notify
```

`hooks/codex.hooks.json` carries only the events Codex understands (a subset of the full Claude Code set in `hooks/hooks.json`). `opencode/index.ts` is the OpenCode TypeScript plugin; `bin/build-opencode-mirror` mirrors it to `dist/opencode/plugins/`. Anything under `assets/` and `scripts/` is bundled with the plugin and reachable from hook commands via `${CLAUDE_PLUGIN_ROOT}`.

## Skill frontmatter

Three harnesses read every canonical `SKILL.md`, and each reads a different part of its frontmatter. Claude Code accepts around twenty fields, OpenCode documents five, and Codex CLI documents two. All three tolerate a field they do not recognize, and only `claude plugin validate --strict` reports one. Rule 21 of `bin/validate-plugins` holds this repository to the fields below, so a misspelling such as `disable-model-invokation` fails validation instead of doing nothing in all three.

| Field                      | Claude Code                  | Codex CLI             | OpenCode |
| -------------------------- | ---------------------------- | --------------------- | -------- |
| `name`                     | Required                     | Read                  | Read     |
| `description`              | Required routing description | Read                  | Read     |
| `license`                  | Read                         | Ignored               | Read     |
| `compatibility`            | Read                         | Ignored               | Read     |
| `metadata`                 | Read                         | Read                  | Read     |
| `allowed-tools`            | Read                         | Ignored               | Ignored  |
| `disable-model-invocation` | Read                         | Translated, see below | Ignored  |
| `paths`                    | Read                         | Ignored               | Ignored  |
| `context`                  | Read                         | Ignored               | Ignored  |
| `agent`                    | Read                         | Ignored               | Ignored  |
| `argument-hint`            | Read                         | Ignored               | Ignored  |

In that table _Read_ means the harness acts on the field, and _Ignored_ means it accepts the field with no effect anyone has observed. The two rest on different evidence: OpenCode's documentation states outright that unknown fields are ignored and names the five it reads, while for Codex _Ignored_ combines the measurement below with the absence of any handling for those fields in the CLI. Codex's documentation names only `name` and `description` and says nothing about the rest, so treat its _Ignored_ cells as what was observed rather than as a guarantee.

Measured against Codex CLI 0.155.1 and OpenCode 1.18.31: a skill carrying every field in that table loads in both, appears in the list of skills offered to the model, and produces no warning and no error. Neither harness rejects an unrecognized field and neither reports one, which is the reason the allowlist exists rather than a linter's opinion.

Widening the allowlist means measuring the new field first. Install a skill that carries it under a throwaway `CODEX_HOME` and a throwaway project directory, list what each harness offers the model with `codex debug prompt-input` and `opencode debug skill`, then record the outcome in the table above. A field Claude Code honors can be dropped silently by the other two, which changes what the skill does there without failing anywhere.

### Invocation policy

`disable-model-invocation: true` keeps a skill out of implicit selection in Claude Code. Codex ignores the field and offers the skill to the model anyway. Its counterpart is `policy.allow_implicit_invocation: false` in an `agents/openai.yaml` beside the skill, which withholds the skill from that list while explicit `$skill-name` invocation still works.

`bin/build-codex-marketplace` therefore translates the field rather than copying it. The generated `dist/codex` skill loses the frontmatter line and gains a manifest:

```yaml
policy:
  allow_implicit_invocation: false
```

Write the value as an unquoted `true` or `false`. A quoted value parses as a string, which neither the generator nor rule 16b reads, so the policy would be lost everywhere. `false` is Codex's own default, so it needs no manifest and passes through. A skill that already ships its own `agents/openai.yaml` fails the build rather than having it overwritten; merge the policy into that file by hand.

The whole path was confirmed end to end, not just the mechanism: a skill given the field was built, installed from a local marketplace under a throwaway `CODEX_HOME` with `codex plugin add`, and the resulting session listed a sibling skill while withholding the translated one, with no validation error on the generated manifest. Repeat that check rather than only the frontmatter edit whenever the manifest's contents change, since Codex reads the file the generator writes, comments and all.

This is the one sanctioned difference between a canonical skill and its Codex copy. Rule 16b of `bin/validate-plugins` reproduces exactly this edit independently of the generator and fails on any other difference, so a further harness-specific transformation has to change that rule on purpose.

OpenCode has no counterpart and ignores the field, so a skill that disables model invocation stays implicitly selectable there. OpenCode gates skills through the `skill` key of its own permission configuration instead, which matches on the skill name and is a user setting rather than something a plugin ships. Because OpenCode ignores every field it does not recognize, `bin/build-opencode-mirror` needs no translation step and stays relative symlinks to the canonical skills.

## Routing descriptions and catalog summaries

A plugin carries two kinds of description, written for different readers, and each has one owner:

- **Routing description:** the `description` in a skill's `SKILL.md` frontmatter. Harnesses use it to decide whether a request should activate the skill implicitly, and selectors show it beside the skill's name. Write it for selection.
- **Catalog summary:** the `description` in `.claude-plugin/marketplace.json`, repeated verbatim in the plugin's manifests, the opening paragraph of its README, and its root README "What it does" cell. Write it for a person browsing the catalog. It needs no routing detail.

Every harness routes on the same description. Claude Code loads the canonical `SKILL.md`, the OpenCode mirror links to it, and `bin/build-codex-marketplace` copies it into `dist/codex/` unchanged. Rule 16b of `bin/validate-plugins` permits one difference between a generated `SKILL.md` and its source, the [invocation policy translation](#invocation-policy), and the description is never it, so change a routing description in the canonical file, never through the generator.

A routing description:

1. Opens with the primary action, so a description shortened from the end still routes.
1. Names the trigger phrases a user would say, preferring the ones that distinguish the skill from its neighbors.
1. States a negative boundary when an adjacent skill would otherwise activate instead.
1. Mentions a hard prerequisite only when it affects selection. Other requirements belong in the README and the skill body.
1. Stays short, because every installed skill's description shares one discovery budget in Codex. The [Codex consumption review](reviews/codex-consumption.md#milestone-1-baseline) records that budget.

Rule 17 of `bin/validate-plugins` checks the budget. It renders each generated `dist/codex` skill as the line Codex lists, `- plugin:skill: description (file: path)` with the installed cache path, and charges `ceil(bytes / 4)` tokens per line. The catalog fails when it exceeds 2 percent of the reference model's context window, less a reserve for Codex's bundled system skills; with `CODEX_REFERENCE_CONTEXT_WINDOW` set empty, it is held to Codex's 8,000-character fallback instead. Every run prints the catalog's cost against both budgets. A description over 1,024 characters fails, and one over 150 characters, its average share of the budget, draws a warning. When the catalog fails, tighten the largest descriptions rather than raising the budget.

```yaml
description: >-
  Merge the base branch into the current branch, resolve conflicts, and push.
  Use for "merge main" or "sync with main"; to rebase, use rebase-onto-main.
```

Add `agents/openai.yaml` to a canonical skill only for supported interface metadata or an MCP tool dependency; no skill needs one today, and an invocation-policy override belongs in `disable-model-invocation`, which the generator [translates into that manifest](#invocation-policy) for Codex alone. Never set its `interface.short_description`: Codex prints that in place of `description`, silently replacing the routing description. Do not add keys this repository invents to portable plugin manifests or to `agents/openai.yaml`.

## Cross-harness workflow adapters

Each canonical `SKILL.md` is one workflow shared by Claude Code, Codex CLI, and OpenCode. Write each step against the capability it needs and the restrictions active in the session, not against a harness name: the tools a harness offers vary with its configuration, mode, and installed plugins. Put a harness-specific example beside the shared rule it illustrates instead of forking the workflow into per-harness copies.

New and substantially rewritten skills follow these conventions now. The Git and review chain adopts them in milestone 2 of the [Codex roadmap](plans/todo/2026-09-15-codex-consumption-improvements.md), and the rest of the catalog in milestone 3.

### Invocation

Name the skill, and render how to invoke it only where a person reads the result:

| Harness     | Explicit invocation                                                  |
| ----------- | -------------------------------------------------------------------- |
| Claude Code | `/commit`                                                            |
| Codex CLI   | `$commit`, or choose it from `/skills`                               |
| OpenCode    | Ask for the `commit` skill; the agent loads it with its `skill` tool |

Every harness also activates a skill implicitly when a request matches its routing description.

A generated prompt, such as a worktree handoff, carries the skill name and its arguments as separate values until it is rendered for its destination: the harness that will read the prompt, not the one writing it. Quote a rendered `$name` so shells and prompt transport pass it through literally.

```text
Skill: address-issue
Arguments: 42
Claude Code: /address-issue 42
Codex CLI: $address-issue 42
```

A `$name` mention in generated prose is text for a person or model to read. It is not a tool call, and writing one does not load the skill.

### Skill composition

A parent workflow composes another skill by loading it through the host's skill mechanism, passing its arguments and a continuation block, and resuming from a named step when it returns. Claude Code loads a skill with its `Skill` tool, Codex by reading the `SKILL.md` at the path its skill list advertises, and OpenCode with its `skill` tool.

Write every composition reference with the canonical phrase, so validation can tell composition from other mentions:

```markdown
Invoke the `lint-and-fix` skill with `--no-push`, passing this continuation block:
```

Suggestions to the user, redirects to an adjacent skill, "Pairs with" text, and informational mentions are not composition, so do not phrase them as "Invoke the … skill".

### Skill dependencies

Declare every skill a workflow composes in a `## Skill dependencies` section of its `SKILL.md`, placed before `## Workflow`:

```markdown
## Skill dependencies

- **Required:** `lint-and-fix`
- **Optional:** `review-branch`, `resolve-copilot-pr-feedback`
```

Write `None` for an empty category. A skill that composes nothing omits the section.

- **Required:** the workflow cannot honestly complete the dependent step without that skill.
- **Optional:** the skill improves the workflow, and its absence has a documented fallback or omission.
- **Selection-driven:** when a workflow invokes skills the user selects from a listed set, declare every candidate as optional.

A composition reference in a skill's `references/` files counts against the skill's own `SKILL.md`. Keep `agents/openai.yaml` `dependencies.tools` for MCP tools; document external executables as requirements rather than dependencies.

Before the first consequential step that needs a required skill, confirm the skill appears in the host's advertised skill list. If it is missing, report the skill and how to install it, preserve completed work, and stop before the dependent side effect. Never silently replace a missing required workflow:

```markdown
Before pushing, confirm that the `lint-and-fix` skill is available. If it is not, stop and report: "Required skill `lint-and-fix` is not installed. Install it with `/plugin install lint-and-fix@agent-harness-plugins` in Claude Code or `codex plugin add lint-and-fix@agent-harness-plugins` in Codex, then rerun." Leave the local commit in place.
```

A missing optional skill follows its documented fallback, and the result reports that step as skipped, never as completed. A selected candidate that is not installed is skipped and reported with its installation command, and the remaining selections continue:

```markdown
If a selected skill is not installed, record it as "skipped: not installed" with its installation command, and continue with the next selection. Report skipped selections separately from completed ones.
```

### Capabilities

Request the capability a step needs, check whether the session offers it, and use a documented fallback only when it does not. Availability, not the harness name, decides: one harness can offer a capability in one mode and not in another.

| Capability           | Where available                                                                    | Fallback                                                   |
| -------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Structured question  | Claude Code `AskUserQuestion`; Codex `request_user_input` where its mode offers it | Numbered options in plain text, then wait for the reply    |
| Interruptible wait   | A background monitor or scheduled wake-up                                          | Bounded polling that stays within the host command timeout |
| Browser              | A browser automation tool                                                          | Report the URL and what to check there                     |
| Artifact writer      | An artifact or canvas tool                                                         | Write a local file and report its path                     |
| Local file operation | Dedicated read, edit, and write tools                                              | Shell commands the sandbox permits                         |

```markdown
Ask the user which base branch to use. Use a structured question tool when the session offers one; otherwise list the branches as numbered options in plain text and wait for the reply.
```

### Authority and permissions

Prior user authorization decides what the workflow intends to do: a request to "commit and push" authorizes the push, so the skill does not ask again. The host still decides what it permits. Plan or read-only mode, sandbox writable roots, network policy, hook trust, and tool approval apply regardless of what a skill says, so a skill preserves the user's authorization without promising to bypass those controls. "No prompts" in a skill means the workflow adds no confirmation steps of its own; it cannot suppress a host approval.

```markdown
The user's request authorizes the push, so do not ask for confirmation. If the host blocks it (Plan or read-only mode, no network access in the sandbox, or a declined approval), stop before any step that depends on the push, report the blocked command and the restriction, and leave the local commit in place.
```

### Continuation

A child skill invoked by a parent ends with a structured result instead of a handoff, so the parent resumes without asking the user. The `lint-and-fix` Parent Continuation Contract is the reference form. The parent passes:

```text
Parent continuation:
- Caller: pr
- Resume target: step 6
- On success: continue with step 6
- On failure or skipped required work: stop and report the unresolved items
```

The child returns:

```text
Status: <success|no-op|failure|unavailable>
Outputs: <commit SHA, paths, or none>
Unresolved or skipped: <none|summary>
Caller resume target: step 6
```

A failure, or a capability the child needs but the session lacks, returns control to the parent with an accurate status. The child does not switch to another workflow, and the parent does not present the step as complete.

## Skill cross-references

Skills name each other and point at files by path, and a stale one fails only in the downstream project that loads the skill, long after the rename that broke it. `bin/check-cross-references` resolves them; rule 19 of `bin/validate-plugins` runs it over every `SKILL.md` and every file under a skill's `references/`.

What gets resolved, and against what:

| Spelling                                                    | Resolved against              |
| ----------------------------------------------------------- | ----------------------------- |
| `plugins/…`, `dist/codex/…`, `dist/opencode/…`              | the repository root           |
| `${CLAUDE_PLUGIN_ROOT}/…`                                   | the plugin shipping the skill |
| `./references/…`                                            | the skill directory           |
| `` `/name` `` and a backticked name beside the word "skill" | a directory under `plugins/`  |

`${CLAUDE_PLUGIN_ROOT}/scripts/…` is left to rule 18, which also checks the executable bit. A bare backticked name is not checked: nothing distinguishes `set-up-ci` from `lean-toolchain` without reading the sentence around it.

A string with a stand-in segment is skipped, so `plugins/PLUGIN-NAME/README.md`, `plugins/<name>/README.md`, and `./references/ci-<language>.md` need nothing. Two HTML comments cover the rest:

```markdown
<!-- validate-plugins: repository-paths -->
<!-- validate-plugins: ignore /config ./references/BASH.md -->
```

`repository-paths` declares that the `bin/` and `docs/` paths in this file name files in this repository. Without it they are skipped, because most of them name a file the skill _creates_ in the project it is run against (`bin/version-audit`, `docs/plans/todo/`), and because this repository's own layout matches, checking them everywhere would pass by coincidence rather than by correctness. Few files qualify: `create-plugin` is one, since its whole subject is this repository. Run `grep -rl 'validate-plugins: repository-paths' plugins/` for the current set.

The same script checks skill dependencies, which the [Skill dependencies](#skill-dependencies) convention defines:

- Every composition reference, "Invoke the `NAME` skill" with or without a slash before the name, in a `SKILL.md` or any file under its `references/`, is declared in that skill's `## Skill dependencies` section.
- The section has exactly one `- **Required:**` line and one `- **Optional:**` line, each holding `None` or backticked skill names separated by commas, and nothing else.
- Every declared name resolves to a `plugins/*/skills/NAME/SKILL.md`, appears in only one category, and appears only once.
- Every declared name is used: the skill names it, backticked with or without a leading slash, somewhere outside the section, as a selection list does for each candidate.

Other wording, such as "use the `review-branch` skill instead" or "run `/lint-and-fix` next", is not composition and needs no declaration. The exception is "invoke `NAME`" without the canonical phrase: it reads as composition but escapes the checks above, so it draws a warning when `NAME` is a skill that the owning skill neither declares nor is itself. Rewrite a real composition with the canonical phrase and declare it, and reword a mention that is not one. A warning does not fail validation. An ignore comment does not exempt a dependency finding.

`ignore` exempts an individual reference that resolves nowhere because it is an illustration rather than a reference at all: Claude Code's own `/config`, Cargo's `/target` gitignore pattern, a reference filename naming a layout convention a plugin being authored should follow. Write the entry exactly as the checker reports it. Several such comments may appear in one file, and an entry that matches nothing is itself reported, so an exemption cannot outlive the reference it was written for. Exemptions are file-scoped rather than line-scoped because most of the references that need one sit inside an ordered list or a table row, where an HTML comment would break the Markdown.

## Review checklists

A style guide can carry a pull request review checklist at `plugins/<guide>/skills/<guide>/references/review-checklist.md`, beside the rules it condenses. `set-up-review-config` installs these checklists into other repositories, where Copilot code review, Codex and Claude Code Review read them. A skill can read only files its own plugin ships, so `bin/build-review-checklists`, run by `make build`, copies each checklist byte for byte to `plugins/set-up-review-config/skills/set-up-review-config/references/checklists/<guide>.md`. Rule 20 of `bin/validate-plugins` fails when a copy is missing, stale or orphaned, or when `set-up-review-config`'s `references/guides.md` has no detection rules for it. Edit the source, never the copy.

A checklist is not the guide's essential checklist. It keeps only the rules a reviewer can check in a diff, leaves out what formatters enforce, and ranks each rule. The generator checks this format, except where noted:

- A level-1 heading ending in "Review Checklist", then a line naming the files it covers and the citation form, `<guide>: Rule name`. The generator does not check that line.
- Exactly three level-2 sections, in order: `## Important` (defects that change behavior, lose data or break tooling; Claude Important and Codex P1), `## Nits` (style rules no formatter enforces), and `## Do not flag` (accepted exceptions, and tool findings when the tool runs in CI).
- Every item is `- **Rule name**: explanation`. Reviewers cite the bold name, so renaming a rule changes what review comments say. Mark items that apply only to executable scripts, so sourced files are exempt.
- It must stand alone in another repository: no relative links, no `./references/` paths, no plugin-root placeholder, and no `validate-plugins` directives. Avoid a backticked slash before a word: rule 19, not the generator, reads it as a skill name and fails.
- No tables or code fences, so a target repository's Markdown formatter never rewrites an installed copy.
- At most 5,000 bytes. The cap keeps a checklist condensed; raise it in the generator deliberately, not to fit one file.

Derive every rule from the guide. When a guide's rule changes, update its checklist in the same change. A new checklist also needs an entry in `references/guides.md` with its detection and routing rules.

## Adding a plugin

1. Create the plugin directory under `plugins/`.
1. Add a `.claude-plugin/plugin.json` with metadata.
1. For every plugin with `hooks/hooks.json` in this repository, validator rule 14 requires a `.codex-plugin/plugin.json` sibling with a non-empty `hooks` field (usually `"hooks": "./hooks/hooks.json"`), regardless of its intended harness targets. Validate its events against the target Codex CLI hook schema. If the Claude Code hook file includes unsupported events, point the Codex manifest at a separate compatible hook file. See `plugins/notify/` at the repository root for the split-manifest pattern.
1. Register the plugin in `.claude-plugin/marketplace.json`.
1. Create a per-plugin `README.md` in the plugin directory.
1. Add a row to the appropriate category table in the root `README.md`. If the plugin requires external tools, add a bullet to the category's `**External tools:**` list.
1. If the plugin bundles a script, add scrut coverage under `tests/scrut/` and register any needed binary path in the `SCRUT_ENV` block in the `Makefile` and the matching `scrut-env` list in `.github/workflows/ci.yml`.
1. Regenerate the bundled review checklists and the Codex and OpenCode mirrors with `make build`, and commit the results.
1. If the plugin ships a skill, read the `Codex skill inventory` line that `make validate` prints. Every skill's line, name and versioned install path included, shares one Codex discovery budget, so a new skill can push the catalog over it even when its own description is short. If rule 17 fails, tighten the largest routing descriptions its error lists rather than raising the budget; see [Routing descriptions and catalog summaries](#routing-descriptions-and-catalog-summaries).
1. Run `make test-all` and fix anything it reports before opening a PR.

## README catalog format

The root `README.md` lists plugins in a compact 3-column table (Plugin, Trigger, What it does) per category, plus a 2-column table for hooks (Plugin, What it does). External-tool requirements appear below each table as a `**External tools:**` bullet list, one bullet per plugin (or per group of plugins sharing the same requirement).

A `## Contents` section sits between the intro paragraph and `## Install`. It is section-level navigation over the file's H2s: the `Install` and `Skills` bullets name their H3s inline, and the two `Using with` guides share a bullet. It never lists individual plugins, so adding a plugin does not touch it. Update it only when an H2 or a skills category is added, renamed, or removed, and keep every anchor resolvable, because markdownlint's MD051 checks them.

Do not rename `## Install`, `## Using with OpenCode`, or `### Codex CLI known limitations`, and do not add a second heading that slugifies to one of those. Every plugin README links to `../../README.md#install`, some also link the other two, and the `markdownlint-rule-relative-links` custom rule fails the build if a target fragment disappears.

Use the canonical `description` field from `marketplace.json` for the "What it does" column, verbatim, so the README stays a thin mirror of the catalog of record.

The opening paragraph of each `plugins/<name>/README.md` must also match that same `description` verbatim. The plugin README may elaborate freely after that first paragraph, but the first paragraph is the catalog entry. This keeps three surfaces (catalog, root README, plugin README) from drifting into three different accounts of what a plugin does.

The `Trigger` column shows the slash command (for example `/commit`), plus a required argument when the skill takes one (for example `/address-review <path>`). Auto-activation behavior for style-guide skills is not annotated in the table; cover it in the per-plugin README instead.

Categories used in the README, in order: Git, Issues and Worktrees, Code Review, Code Quality, Writing, Scaffolding, CI and Release, Agents. Their `marketplace.json` `category` slugs are the same names lowercased and hyphenated (`git`, `issues-and-worktrees`, `code-review`, `code-quality`, `writing`, `scaffolding`, `ci-and-release`, `agents`).

Hook plugins are the ninth category. They carry `"category": "workflow"` and are listed under their own H2 rather than in one of the tables above.

If a plugin needs a `## Recommended Permissions` section, use a copy-pasteable JSON block (`{"permissions": {"allow": [...]}}`), not prose bullets, and make sure every command the skill actually runs appears in it.

Every plugin with a hard external dependency must say so. Two forms are in use, both fine: a `**Requires:**` line in the header block next to `**Type:**` and `**Trigger:**` for one or two tools, or a `## Requirements` section before `## Usage` when the entry needs install instructions or caveats. Do not use both in one README.

## Versioning

Each plugin's `.claude-plugin/plugin.json` is the sole version source. If a plugin also has `.codex-plugin/plugin.json`, mirror that version there because validation requires the two manifests to agree. Marketplace entries are registration metadata and contain no version fields.

**Individual plugin `version`**:

- **Patch**: bug fixes, wording tweaks, prompt adjustments
- **Minor**: new capabilities or meaningful behavior changes
- **Major**: breaking changes (for example, removing or restructuring a skill)
- New plugins start at `1.0.0`

**Review checklists change two plugins**: A change to a style guide's `references/review-checklist.md` also changes its copy in `set-up-review-config`, so both plugins need a forward bump: a patch for rewording, and a minor bump for `set-up-review-config` when it gains a new guide. A generator change that alters the copies bumps `set-up-review-config`.

**Version checks on branch operations**: After merging, rebasing, or before creating a PR, use the `check-versions` skill to verify version correctness. Another branch may have already incremented a version, so always check.
