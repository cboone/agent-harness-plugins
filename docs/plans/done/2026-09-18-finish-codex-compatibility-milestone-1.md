# Finish Codex compatibility milestone 1

Tracking: [issue #434](https://github.com/cboone/agent-harness-plugins/issues/434). Roadmap: [Codex consumption improvements](../todo/2026-09-15-codex-consumption-improvements.md). Evidence: [Codex consumption review](../../reviews/codex-consumption.md).

## Outcome

Complete milestone 1 by replacing the audit's provisional Codex assumptions with a reproducible current baseline, defining one shared workflow contract with capability-based harness adapters, preserving routing descriptions independently from catalog summaries within Codex's discovery budget, declaring skill dependencies consistently, and adding deterministic checks for those rules.

This milestone establishes the contract that milestones 2 and 3 will apply. It does not migrate every workflow body, repair installed README links, redesign worktree handoffs, expand notifications, or run the complete Git and review evaluation suite.

## Current state

The branch starts at `046f1389`, with no milestone 1 changes. The local baseline on 2026-09-18 is Codex CLI `0.155.0`. Its command surface includes both marketplace management and individual plugin management:

- `codex plugin marketplace add|list|upgrade|remove`
- `codex plugin add|list|remove`

`codex plugin marketplace add` accepts a local path, `owner/repo[@ref]`, or a Git URL with `--ref`. `codex features list` reports `plugin_hooks` as removed and `hooks` as stable.

Current OpenAI documentation also establishes these behaviors that supersede the review's `0.154.0` observations:

- Codex explicitly invokes skills through `$skill` mentions or the `/skills` selector and implicitly selects them from the `SKILL.md` `description`.
- The initial skill inventory includes names, descriptions, and paths. It uses at most 2 percent of the model context window, or 8,000 characters when the context window is unknown. Over budget, Codex shortens descriptions first and may then omit skills with a warning.
- `agents/openai.yaml` supports interface metadata, invocation policy, and tool dependencies. It does not declare skill-to-skill dependencies.
- Plugin hooks no longer require the removed `plugin_hooks` feature. Unmanaged hooks, including plugin hooks, require review and trust through `/hooks` before execution, and a changed hook definition requires review again.
- Codex supports `PreCompact`, `PostCompact`, `SubagentStart`, `SubagentStop`, `Interrupt`, and `SessionEnd` in addition to the events named in the audit.
- Sandbox scope, approval policy, project trust, tool availability, and active interaction mode remain host constraints. Workflow text cannot override them.

The upstream renderer at `openai/codex` revision `36b84c81ec01` (`codex-rs/ext/skills/src/render.rs`, 2026-09-17) matches that description and adds the detail a budget check needs:

- Each skill renders as `- {name}: {description} (file: {path})` plus a newline, with the description truncated to 1,024 characters.
- A known context window yields a budget of 2 percent of its tokens, counted at approximately four bytes per token. An explicitly configured token budget is capped at 10,000. Without either, the budget is 8,000 characters.
- Codex may replace shared path prefixes with aliases when that renders the catalog more completely or cheaply.
- Its extension-compatible catalog renders an entry's `short_description` in place of its `description` when one is present.

That revision is from `main` and may postdate `0.155.0`; step 1 confirms the installed CLI's behavior.

Measured against the `046f1389` content on 2026-09-19:

- The catalog has 62 plugins and 61 skills. `notify` is hook-only and is the only plugin with `.codex-plugin/plugin.json`.
- Canonical skill descriptions total 33,758 characters, with a mean of 553; 54 exceed 320 characters. The generated catalog summaries total 7,799 characters.
- Qualified `plugin:skill` names total 2,103 characters. Installed paths total about 6,190 characters, assuming a `~/.codex/plugins/cache/agent-harness-plugins/<plugin>/<version>/skills/<skill>/SKILL.md` layout.
- Names and paths alone therefore exceed the 8,000-character fallback. No description content lets the full catalog fit it, so the fallback is a documented degraded case in which Codex shortens descriptions.

The repository conflicts with that baseline in these milestone 1 surfaces:

- `README.md` documents marketplace-only plugin management, the removed feature flag, and obsolete hook limitations. Its known-limitations section says `notify` wires only `Stop` on Codex, while `plugins/notify/hooks/codex.hooks.json` wires `Stop`, `UserPromptSubmit`, `PreToolUse:request_user_input`, and `PreCompact:auto`.
- `plugins/notify/README.md` repeats the marketplace-only installation, tells users to run `codex features enable plugin_hooks`, and pins its support statement to `0.154.0`. Review finding 17 repeats the outdated claim that `notify` wires only `Stop`.
- `bin/build-codex-marketplace` replaces every generated skill routing description with the plugin's catalog summary.
- `bin/validate-plugins` rule 17 measures only description characters against a 12,000-character repository limit, excluding names, paths, and line syntax. It errors when the generated descriptions exceed that limit.
- `docs/plugin-development.md`, `plugins/create-plugin/`, and the skill sources do not define a harness-neutral adapter or a required-versus-optional skill dependency contract. `plugins/create-plugin/skills/create-plugin/references/skill-md.md` still says Codex descriptions come from marketplace summaries.

Skill composition today:

- 31 of the 61 `SKILL.md` files name another plugin in a form `bin/check-cross-references` extracts. Most of those mentions are suggestions, redirects, pairings, or information rather than composition.
- 16 composition references across 10 skills use the phrasing "invoke the `NAME` skill": `merge-main` and `rebase-onto-main` invoke `commit`; `monitor-pr` invokes `lint-and-fix`, `merge-main`, and `resolve-copilot-pr-feedback`; `pin-everything`, `pr`, `resolve-copilot-pr-feedback`, and `upgrade-everything` invoke `lint-and-fix`; `refresh-project-scaffolding` invokes `add-community-files`, `pin-everything`, and `review-dependabot-config`; `review-dependabot-config` invokes `lint-and-fix` and `pin-everything`; `triage-dependabot-prs` invokes `monitor-pr`, and `create-issue` from `references/actions.md`.
- `bootstrap-project` and `refresh-project-scaffolding` also invoke skills the user selects from a listed set, through "the Skill tool", without naming each invocation.

The review and roadmap reached `main` in `9b530390`. Issue #434 still links them on `chore/review-repo-for-codex-usage` and carries its own copy of the milestone checklist.

## Design decisions

### Baseline policy

Record the exact CLI version used for each baseline or evaluation, but support the current stable Codex CLI rather than encoding `0.155.0` as a permanent minimum. Documentation examples must be checked against both the installed CLI help and current official documentation. If they disagree, record the discrepancy and avoid claiming unsupported behavior.

Keep primary consumer instructions in `README.md`. Keep dated command, feature, hook, budget, and validation evidence in `docs/reviews/codex-consumption.md` so the README does not become a historical log.

### Shared workflow and harness adapters

The canonical `SKILL.md` remains one shared workflow. Instructions select behavior by available capability and active restrictions, not by assuming that a harness name implies a fixed tool set.

Define these adapter areas in `docs/plugin-development.md`:

1. **Invocation:** documentation renders `/skill` for Claude Code, `$skill` or `/skills` selection for Codex, and the supported OpenCode form. Generated prompts carry the skill identity and arguments separately until the destination harness renders them.
2. **Skill composition:** a parent loads a referenced skill through the host's supported skill mechanism, passes arguments and the continuation contract, then resumes from the named step. Every composition reference uses the phrasing "Invoke the `NAME` skill", so validation can tell composition from other mentions. A `$skill` mention in generated prose is not treated as a nested tool call.
3. **Capabilities:** instructions request the capability they need, such as a structured question, interruptible wait, browser, artifact writer, or local file operation. They use a documented fallback only when that capability is absent.
4. **Authority and permissions:** prior user authorization controls workflow intent. Plan or read-only mode, sandbox roots, network policy, hook trust, and tool approval still control what the host permits. A skill preserves authorization without promising to bypass those controls.
5. **Continuation:** nested workflows return a machine-readable status, relevant outputs, and a resume target. Failure or missing capability returns control to the parent with accurate state instead of silently substituting another workflow.

Add short copyable authoring templates for each adapter area. Keep product-specific examples adjacent to the shared rule so future changes do not create separate Claude and Codex workflow forks.

### Routing descriptions and catalog summaries

Use `SKILL.md` frontmatter `description` as the sole routing and implicit-activation description for every harness. Use `.claude-plugin/marketplace.json` `description`, plugin manifest descriptions, plugin README opening paragraphs, and root README "What it does" cells as catalog summaries.

Remove the Codex generator's description replacement. Rewrite canonical skill descriptions where necessary so each starts with the primary use case and includes concise scope boundaries and decisive trigger phrases. Do not require catalog summaries to carry routing detail.

Do not add repository-private keys to portable plugin manifests or `agents/openai.yaml`. Add `agents/openai.yaml` only when a skill needs supported interface metadata, an explicit invocation-policy override, or an MCP tool dependency. Do not add `interface.short_description`: Codex's extension-compatible catalog renders a short description in place of `description`, so one would silently replace the routing description.

### Discovery inventory budget

Mirror Codex's own rule: the inventory budget is 2 percent of the model's context window, with an 8,000-character fallback when the context window is unknown.

- **Cost model:** for every generated skill, render `- {name}: {description} (file: {path})` plus a newline, using the name form and installed path layout observed in the baseline. Until the name form is observed, count the longer qualified `plugin:skill` form. Normalize paths to the observed cache layout with a fixed-length placeholder for the home directory, so results do not depend on the machine. Ignore Codex's path aliasing, which only lowers the cost.
- **Primary gate:** record the baseline's reference model and its context window as constants in `bin/validate-plugins`. Convert rendered bytes to tokens at four bytes per token, matching Codex. Subtract an explicit reserve for the usage-instruction framing and for Codex's bundled system skills, both observed in the baseline. Fail when the full catalog exceeds the remaining budget.
- **Fallback:** when the reference context window is overridden to empty, apply the 8,000-character budget exactly as Codex does. Fixtures use this path. On every normal run, print a one-line summary of the full catalog's cost against both budgets, so the degraded fallback case stays visible without a warning on each run.
- **Per-description guidance:** keep the 1,024-character error. Replace the generated-only 320-character warning with one warning threshold for routed descriptions, derived from the primary budget's average per-skill allowance and recorded beside the budget constants.
- **Resilience to shortening:** because Codex shortens descriptions before omitting skills, each routing description opens with its primary action and decisive trigger, so a shortened description still routes.

Do not raise the recorded budget to fit content; tighten descriptions instead. Revisit the constants only when the baseline's reference model changes, and record that change in the review.

### Skill dependencies

Represent skill-to-skill dependencies in prose using a validator-readable convention in each caller's `SKILL.md`:

```markdown
## Skill dependencies

- **Required:** `lint-and-fix`
- **Optional:** `review-branch`
```

Use `None` when a category is empty. A required dependency means the workflow cannot honestly complete the dependent step without that installed skill. An optional dependency improves the workflow, but its absence has a documented in-skill fallback or omission.

- **Composition reference:** an instruction written as "Invoke the `NAME` skill", with or without a leading slash in the name, in a `SKILL.md` or any file under its `references/`. A reference file's composition counts against its owning `SKILL.md`. Suggestions to the user, redirects to an adjacent skill, "Pairs with" text, and informational mentions are not composition and need no declaration.
- **Selection-driven composition:** when a workflow invokes skills the user selects from a listed set, as `bootstrap-project` and `refresh-project-scaffolding` do, declare each candidate as optional. A selected candidate that is not installed is skipped and reported as skipped with its installation path. It is never presented as completed, and the remaining selections continue.
- **Use of a declaration:** a declared name must appear in the skill's `SKILL.md` or references in one of the spellings `bin/check-cross-references` extracts.

Before a consequential dependent step, resolve every required skill using the host's advertised skill inventory. If one is unavailable, report the missing skill and installation path, preserve completed work, and stop before the dependent side effect. Never silently replace a missing required workflow. Optional dependencies follow their documented fallback without being presented as completed.

Keep `agents/openai.yaml dependencies.tools` limited to supported MCP tool declarations. External executables remain documented as requirements rather than being mislabeled as skill dependencies.

### Versioning

- Every plugin whose generated Codex output changes receives at least a patch bump in `.claude-plugin/plugin.json`, mirrored to `.codex-plugin/plugin.json` where present, even when its canonical source is otherwise unchanged. Codex consumers see changed routing behavior, and release detection in `.github/workflows/release.yml` watches only canonical `./plugins/<name>/` sources.
- Bump each plugin once on this branch relative to `main`, at the highest level any of its changes requires, in the commit that first changes it.
- `create-plugin` takes a minor bump, because the skills it creates gain the dependency section and routing rules. Confirm the level with the `check-versions` skill.
- `notify` takes a patch bump for its README correction.

## Implementation plan

### 1. Capture the supported baseline

Update `docs/reviews/codex-consumption.md` in place with a dated milestone 1 baseline section containing:

- the current commit and `codex --version` output;
- `codex plugin --help`, marketplace subcommand help, and the hook and plugin rows of `codex features list`;
- official documentation links for plugins, skills, hooks, sandbox and approvals, plus the upstream renderer revision consulted;
- the supported hook event set and hook-trust workflow, including review again after a hook definition changes;
- the reference model and its context window, the rendered name form and installed path layout for plugin skills, and the usage-instruction framing and bundled system skills that determine the reserve;
- whether `codex plugin marketplace upgrade` refreshes an installed plugin whose version is unchanged;
- the observed differences from the 2026-09-15 audit, including finding 17's outdated premise;
- explicit limits on what was inspected locally versus confirmed from documentation or upstream source.

If the installed CLI's rendered skill list cannot be observed directly, use the upstream renderer at a revision matching the installed CLI and say so.

Update `README.md` to describe marketplace registration separately from plugin installation, listing, removal, and refresh. Include selective installation and troubleshooting examples. Replace the feature-flag instructions with `/hooks` review and trust guidance. Correct the known-limitations section so it contains only current limitations, describes the four Codex events `notify` wires, and links deferred implementation problems to milestones 2 through 4. Keep the `install` and `codex-cli-known-limitations` anchors and every other anchor that other files link.

Update `plugins/notify/README.md` the same way: plugin installation through `codex plugin add`, `/hooks` review and trust including review again after an upgrade changes a hook, and a support statement phrased against the current stable CLI rather than `0.154.0`. Apply the `notify` patch bump and regenerate mirrors.

Use command examples verified against CLI `0.155.0`, but phrase prose in terms of the supported current-stable policy. Do not add a permanent version gate without evidence that newer interfaces are incompatible.

### 2. Publish the adapter authoring contract

Add a "Cross-harness workflow adapters" section to `docs/plugin-development.md` containing the five adapter areas and templates from the design decisions. Include examples for:

- user-facing invocation versus programmatic skill composition, using the canonical composition phrasing;
- capability detection before fallback selection;
- preserving existing authorization while respecting active host restrictions;
- required dependency failure before consequential actions;
- optional dependency fallback, including a skipped selection-driven candidate;
- parent continuation status and resume targets.

Update `plugins/create-plugin/skills/create-plugin/references/skill-md.md`, and the skill-creation step and final checklist in `plugins/create-plugin/skills/create-plugin/SKILL.md`, so newly created skills follow the routing-description, adapter, and dependency conventions. Leave the reference's description-sourcing paragraph for step 6, when that behavior changes. Apply the `create-plugin` minor bump and regenerate mirrors.

Do not retrofit every workflow body in this milestone. Record the Git and review chain as the first adopter for milestone 2 and the remaining catalog as milestone 3.

### 3. Declare and validate skill dependencies

Start from the composition inventory in the current state and confirm it with a fresh search, since phrasing varies ("using the Skill tool", "via the Skill tool"). Where a composition reference uses other phrasing, change only that phrase to the canonical form and leave the rest of the workflow body for milestones 2 and 3. Classify each dependency as required or optional based on whether the caller can meet its advertised outcome without it; selection-driven candidates are optional.

Add the `## Skill dependencies` block to each composing skill, and apply a patch bump to each plugin that has not already been bumped on this branch. Add the preflight and missing-dependency behavior to the shared adapter contract, while leaving per-workflow adoption details for milestones 2 and 3.

Extend `bin/check-cross-references`, which already scans every `SKILL.md` and reference file as rule 19, to enforce:

- declared dependencies resolve to a canonical `plugins/*/skills/NAME/SKILL.md`;
- a dependency is not both required and optional;
- every composition reference in the canonical phrasing is declared;
- every declaration is used;
- required and optional sections use the documented form, with `None` for an empty category.

Widen `CANDIDATE_PREFILTER` to admit files whose only candidates are the dependency block, as the script's header requires. Describe the new checks in the "Skill cross-references" section of `docs/plugin-development.md`. If the checks move into a separate script instead, register it in the `Makefile` `SCRUT_ENV` block, the CI `scrut-env` list, and `bin/list-shell-scripts` coverage.

Extend `tests/fixtures/cross-reference-fixture` with a second skill directory, such as `plugins/other/skills/other/SKILL.md`, so declarations can resolve. Add passing and failing cases to `tests/scrut/check-cross-references.md` for missing, unused, duplicate, unresolved, and malformed declarations, a selection-driven optional declaration, and exempt mentions (a suggestion, a redirect, and "Pairs with" text) that need no declaration. Use the `write-scrut-tests` skill before editing those snapshots.

### 4. Replace the compatibility budget check

Refactor validation rule 17 in `bin/validate-plugins` so it evaluates the generated Codex inventory using the cost model and budgets from the design decisions, replacing the separate canonical and generated description totals and the `CODEX_SKILL_DESCRIPTION_BUDGET` variable. Rewrite the rule's header comment, which describes the generator's replacement, to describe the new behavior. Keep the per-description validity checks, then add deterministic checks for:

- non-empty `name` and `description` fields;
- the official 1,024-character maximum for an individual description;
- the routed-description warning threshold;
- total inventory cost against the primary budget, or against the 8,000-character fallback when the reference context window is overridden to empty;
- a clear diagnostic showing the total, budget, reserve, largest entries, and remediation, plus the one-line summary against both budgets.

At this boundary the generator still writes catalog summaries, so the check measures the summary inventory. If that inventory already exceeds the primary budget, combine this boundary with steps 5 and 6 rather than weakening the check.

Add scenarios to `tests/fixtures/validate-plugin-fixture` and Scrut coverage under `tests/scrut/repo-tooling.md` for a passing inventory, a single oversized description, aggregate overflow of the primary budget, name and path overhead that pushes an otherwise passing description total over the budget, and selection of the 8,000-character fallback when the context window is empty. Exercise the limits through overrides; do not raise the recorded budget to accommodate current content.

### 5. Tighten canonical routing descriptions

Audit all canonical `plugins/*/skills/*/SKILL.md` descriptions. Tighten them as needed to retain:

- the primary action in the opening clause, so a shortened description still routes;
- natural-language triggers that distinguish adjacent skills;
- important negative boundaries that prevent false activation;
- hard prerequisites only when they affect selection.

Size them so the inventory built from canonical descriptions fits the primary budget, measuring with the step 4 cost model against a local build with the description replacement removed. Do not commit that trial build. Apply a patch bump to each changed plugin that has not already been bumped on this branch. The generator still writes catalog summaries at this boundary, so the Codex inventory is unchanged.

### 6. Preserve routing descriptions in the Codex distribution

Change `bin/build-codex-marketplace` to copy `SKILL.md` files unchanged. Remove `rewrite_skill_description` and any marketplace-description lookup used only for rewriting.

Add a deterministic check that every generated `SKILL.md` is byte-identical to its canonical source. This covers the `name`, the `description`, and the dependency block, and makes any future harness-specific transformation an explicit design change rather than a silent generator behavior. The OpenCode mirror links canonical skills, so it preserves them by construction.

Apply a patch bump to every remaining plugin whose generated output changed, per the versioning decision. Update `README.md`, `docs/plugin-development.md`, and the description-sourcing paragraph in `plugins/create-plugin/skills/create-plugin/references/skill-md.md` to remove the claim that Codex routing descriptions come from marketplace summaries. Regenerate both Codex and OpenCode mirrors only from canonical sources.

### 7. Close milestone 1 with evidence

Update the milestone 1 checklist in `docs/plans/todo/2026-09-15-codex-consumption-improvements.md` only after its four deliverables pass. Update `docs/reviews/codex-consumption.md` findings 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 17, and 20 with their current disposition: resolved by milestone 1, contract established with adoption pending, or deferred to a named later milestone. Finding 3 has an established invocation convention, finding 5 has corrected authoring and distribution wording, finding 8 has a decided `agents/openai.yaml` policy, and finding 17 needs its premise corrected while notification expansion stays in milestone 3.

Update issue #434 so its milestone 1 checklist matches the roadmap and its tracking-document links point to `main`.

Move this plan to `docs/plans/done/` only when all acceptance criteria are satisfied. Keep both the plan and roadmap as repository history, per the repository's plan policy.

## Commit boundaries

Use focused, GPG-signed Conventional Commits without amending:

1. `docs: record current Codex compatibility baseline`
2. `docs: define cross-harness adapter conventions`
3. `feat: declare cross-skill dependencies`
4. `chore: check the Codex skill inventory budget`
5. `fix: tighten skill routing descriptions`
6. `feat: preserve skill routing descriptions for Codex`
7. `docs: complete Codex compatibility milestone 1`

Combine adjacent boundaries only when the implementation and its validation cannot remain independently passing, as step 4 describes. Apply version changes as the versioning decision describes.

## Validation

After each relevant boundary:

1. Run targeted Scrut suites for changed repository tooling and cross-reference fixtures.
2. Run `make build` and inspect canonical-to-generated diffs. Never hand-edit `.agents/` or `dist/`.
3. Run `make validate` and confirm the new inventory and dependency checks execute.
4. Run Markdown formatting and linting through the repository commands.

Before milestone completion:

1. Run `make test-all` and observe the final result.
2. Run `make build`, then confirm `git status --porcelain -- .agents dist` is empty.
3. Run the isolated Codex smoke checks:
   - Create a temporary `CODEX_HOME` outside the repository and run every Codex command with it, leaving the real Codex home untouched.
   - Register this worktree as a local-path marketplace so the branch content is tested; `cboone/agent-harness-plugins` without a ref fetches the default branch.
   - Authenticate inside the temporary home with `printenv OPENAI_API_KEY | codex login --with-api-key` or an interactive `codex login`. Never copy `auth.json` or other credential files from the real Codex home.
   - List the marketplace and plugins, install a representative skill plugin and `notify`, inspect skill discovery, review and trust the `notify` hooks through `/hooks`, then remove the plugins and the marketplace.
   - Run `codex logout`, then delete the temporary home.
4. Verify one explicit `$skill` invocation and one natural-language activation against the routing metadata. These are smoke checks for the milestone 1 contract, not the milestone 2 connected-workflow evaluation.
5. Verify the same canonical skill still loads in Claude Code and that the OpenCode mirror remains structurally current.
6. Use the `check-versions` skill before creating the PR.

Record the CLI version, model, configuration, commands, results, and relevant transcripts in the review. Redact account identifiers, tokens, and absolute home paths, writing `$CODEX_HOME` or `~` instead. Keep model-backed activation checks informational until the roadmap's repeatability requirement is met.

## Acceptance criteria

Milestone 1 is complete when all of the following are true:

- The root and `notify` READMEs' install, plugin-management, hook-event, and hook-trust guidance matches the supported current stable Codex CLI, the root README accurately describes the Codex events `notify` wires, and the required README anchors remain.
- The review contains a dated, reproducible baseline that distinguishes direct observation from official documentation and upstream source, and records the reference model and budget constants.
- `docs/plugin-development.md` defines shared invocation, composition, capability, authority, permission, and continuation adapters with copyable conventions, including the canonical composition phrasing.
- Every generated Codex `SKILL.md` is byte-identical to its canonical source, so Codex receives the canonical routing descriptions instead of catalog summaries.
- Routing descriptions and catalog summaries have separate documented ownership and validation.
- The deterministic inventory check models Codex's rendered lines, including names and paths, passes the 2 percent budget of the recorded reference model, applies the 8,000-character fallback when the context window is unknown, and reports the full catalog's cost against both budgets.
- Every composition reference is declared, classified as required or optional, and resolves, with defined missing-dependency behavior, including the skip-and-report behavior for selection-driven candidates.
- Every plugin whose Codex output changed carries a version bump, and the `check-versions` skill passes.
- Initial deterministic checks cover routing preservation, inventory size, and dependency declarations.
- `make test-all` passes, generated mirrors are current, and the isolated Codex smoke checks are recorded without copying or exposing credentials.
- The roadmap, the review, and issue #434 accurately mark completed, adoption-pending, and deferred work without claiming milestone 2 or 3 compatibility.

## Deferred work

The following remain outside milestone 1 and retain their roadmap ownership:

- applying adapters to the Git and review chain and evaluating connected workflows: milestone 2;
- catalog-wide invocation examples, helper resolution, worktree prompt transport, installed README links, configuration examples, notification expansion, and conditional reference loading: milestone 3;
- full macOS and Linux matrices, multiple caches, symlinks, paths with spaces, restricted destinations, complete hook payload coverage, and release-grade real-Codex evaluations: milestone 4;
- catalog recategorization from issue #394 and configuration-budget tooling from issue #373.
