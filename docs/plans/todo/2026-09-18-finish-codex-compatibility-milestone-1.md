# Finish Codex compatibility milestone 1

Tracking: [issue #434](https://github.com/cboone/agent-harness-plugins/issues/434). Roadmap: [Codex consumption improvements](2026-09-15-codex-consumption-improvements.md). Evidence: [Codex consumption review](../../reviews/codex-consumption.md).

## Outcome

Complete milestone 1 by replacing the audit's provisional Codex assumptions with a reproducible current baseline, defining one shared workflow contract with capability-based harness adapters, preserving routing descriptions independently from catalog summaries, declaring skill dependencies consistently, and adding deterministic checks for those rules.

This milestone establishes the contract that milestones 2 and 3 will apply. It does not migrate every workflow body, repair installed README links, redesign worktree handoffs, expand notifications, or run the complete Git and review evaluation suite.

## Current state

The branch starts at `046f1389`, with no milestone 1 changes. The local baseline on 2026-09-18 is Codex CLI `0.155.0`. Its command surface includes both marketplace management and individual plugin management:

- `codex plugin marketplace add|list|upgrade|remove`
- `codex plugin add|list|remove`

Current OpenAI documentation also establishes these behaviors that supersede the review's `0.154.0` observations:

- Codex explicitly invokes skills through `$skill` mentions or the `/skills` selector and implicitly selects them from the `SKILL.md` `description`.
- The initial skill inventory includes names, descriptions, and paths. It uses at most 2 percent of the model context, or 8,000 characters when the context size is unknown, and may truncate descriptions or omit skills.
- `agents/openai.yaml` supports interface metadata, invocation policy, and tool dependencies. It does not declare skill-to-skill dependencies.
- Plugin hooks no longer require the removed `plugin_hooks` feature. Unmanaged hooks, including plugin hooks, require review and trust through `/hooks` before execution.
- Codex supports `PreCompact`, `PostCompact`, `SubagentStart`, `SubagentStop`, `Interrupt`, and `SessionEnd` in addition to the events named in the audit.
- Sandbox scope, approval policy, project trust, tool availability, and active interaction mode remain host constraints. Workflow text cannot override them.

The repository currently conflicts with that baseline in four milestone 1 surfaces:

- `README.md` documents marketplace-only plugin management, the removed feature flag, and obsolete hook limitations.
- `bin/build-codex-marketplace` replaces every generated skill routing description with the plugin's catalog summary.
- `bin/validate-plugins` measures only description characters against a 12,000-character repository limit, excluding skill names, paths, and inventory syntax from Codex's smaller current budget.
- `docs/plugin-development.md` and the skill sources do not define a harness-neutral adapter or a required-versus-optional skill dependency contract.

## Design decisions

### Baseline policy

Record the exact CLI version used for each baseline or evaluation, but support the current stable Codex CLI rather than encoding `0.155.0` as a permanent minimum. Documentation examples must be checked against both the installed CLI help and current official documentation. If they disagree, record the discrepancy and avoid claiming unsupported behavior.

Keep primary consumer instructions in `README.md`. Keep dated command, feature, hook, and validation evidence in `docs/reviews/codex-consumption.md` so the README does not become a historical log.

### Shared workflow and harness adapters

The canonical `SKILL.md` remains one shared workflow. Instructions select behavior by available capability and active restrictions, not by assuming that a harness name implies a fixed tool set.

Define these adapter areas in `docs/plugin-development.md`:

1. **Invocation:** documentation renders `/skill` for Claude Code, `$skill` or `/skills` selection for Codex, and the supported OpenCode form. Generated prompts carry the skill identity and arguments separately until the destination harness renders them.
2. **Skill composition:** a parent loads a referenced skill through the host's supported skill mechanism, passes arguments and the continuation contract, then resumes from the named step. A `$skill` mention in generated prose is not treated as a nested tool call.
3. **Capabilities:** instructions request the capability they need, such as a structured question, interruptible wait, browser, artifact writer, or local file operation. They use a documented fallback only when that capability is absent.
4. **Authority and permissions:** prior user authorization controls workflow intent. Plan or read-only mode, sandbox roots, network policy, hook trust, and tool approval still control what the host permits. A skill preserves authorization without promising to bypass those controls.
5. **Continuation:** nested workflows return a machine-readable status, relevant outputs, and a resume target. Failure or missing capability returns control to the parent with accurate state instead of silently substituting another workflow.

Add short copyable authoring templates for each adapter area. Keep product-specific examples adjacent to the shared rule so future changes do not create separate Claude and Codex workflow forks.

### Routing descriptions and catalog summaries

Use `SKILL.md` frontmatter `description` as the sole routing and implicit-activation description for every harness. Use `.claude-plugin/marketplace.json` `description`, plugin manifest descriptions, plugin README opening paragraphs, and root README "What it does" cells as catalog summaries.

Remove the Codex generator's description replacement. Rewrite canonical skill descriptions where necessary so each starts with the primary use case and includes concise scope boundaries and decisive trigger phrases. Do not require catalog summaries to carry routing detail.

Do not add repository-private keys to portable plugin manifests or `agents/openai.yaml`. Add `agents/openai.yaml` only when a skill needs supported interface metadata, an explicit invocation-policy override, or an MCP tool dependency. Do not use `interface.short_description` as a second routing-description source.

Replace the 12,000-character description-only check with a deterministic approximation of Codex's initial skill inventory. Count every generated skill's qualified identity, routed description, and normalized installed path plus fixed per-entry separators. Cap the total at 8,000 characters. Add an explicit reserve for host framing if the current CLI's rendered representation cannot be observed directly. Document the approximation and fail closed when a new skill exceeds it.

### Skill dependencies

Represent skill-to-skill dependencies in prose using a validator-readable convention in each caller's `SKILL.md`:

```markdown
## Skill dependencies

- **Required:** `lint-and-fix`
- **Optional:** `review-branch`
```

Use `None` when a category is empty. A required dependency means the workflow cannot honestly complete the dependent step without that installed skill. An optional dependency improves the workflow, but its absence has a documented in-skill fallback or omission.

Before a consequential dependent step, resolve every required skill using the host's advertised skill inventory. If one is unavailable, report the missing skill and installation path, preserve completed work, and stop before the dependent side effect. Never silently replace a missing required workflow. Optional dependencies follow their documented fallback without being presented as completed.

Keep `agents/openai.yaml dependencies.tools` limited to supported MCP tool declarations. External executables remain documented as requirements rather than being mislabeled as skill dependencies.

## Implementation plan

### 1. Capture the supported baseline

Update `docs/reviews/codex-consumption.md` in place with a dated milestone 1 baseline section containing:

- the current commit and `codex --version` output;
- `codex plugin --help`, marketplace subcommand help, and relevant feature output;
- official documentation links for plugins, skills, hooks, sandbox and approvals;
- the supported hook event set and hook-trust workflow;
- the observed differences from the 2026-09-15 audit;
- explicit limits on what was inspected locally versus confirmed from documentation.

Update `README.md` to describe marketplace registration separately from plugin installation, listing, removal, and refresh. Include selective installation and troubleshooting examples. Replace the feature-flag instructions with `/hooks` review and trust guidance. Correct the known-limitations section so it contains only current limitations and links deferred implementation problems to milestones 2 through 4.

Use command examples verified against CLI `0.155.0`, but phrase prose in terms of the supported current-stable policy. Do not add a permanent version gate without evidence that newer interfaces are incompatible.

### 2. Publish the adapter authoring contract

Add a "Cross-harness workflow adapters" section to `docs/plugin-development.md` containing the five adapter areas and templates from the design decisions. Include examples for:

- user-facing invocation versus programmatic skill composition;
- capability detection before fallback selection;
- preserving existing authorization while respecting active host restrictions;
- required dependency failure before consequential actions;
- optional dependency fallback;
- parent continuation status and resume targets.

Update `plugins/create-plugin/skills/create-plugin/references/skill-md.md` so newly created skills follow the routing-description, adapter, and dependency conventions. Apply the appropriate patch version bump to `create-plugin` and regenerate mirrors.

Do not retrofit every workflow body in this milestone. Record the Git and review chain as the first adopter for milestone 2 and the remaining catalog as milestone 3.

### 3. Preserve routing descriptions in the Codex distribution

Change `bin/build-codex-marketplace` to copy canonical skill descriptions unchanged. Remove `rewrite_skill_description` and any marketplace-description lookup used only for rewriting.

Audit all canonical `plugins/*/skills/*/SKILL.md` descriptions. Tighten them as needed to retain:

- the primary action in the opening clause;
- natural-language triggers that distinguish adjacent skills;
- important negative boundaries that prevent false activation;
- hard prerequisites only when they affect selection.

Keep each description concise enough for the whole-catalog inventory budget. Treat wording-only adjustments as patch changes under the repository's version policy. Regenerate both Codex and OpenCode mirrors only from canonical sources.

Update `README.md`, `docs/plugin-development.md`, and the create-plugin reference to remove the claim that Codex routing descriptions come from marketplace summaries.

### 4. Declare and validate skill dependencies

Inventory every skill-to-skill composition reference, starting with existing "Skill tool" instructions and backticked skill references in workflow steps. Classify each dependency as required or optional based on whether the caller can meet its advertised outcome without it.

Add the `## Skill dependencies` block to each skill that composes another skill. Add the preflight and missing-dependency behavior to the shared adapter contract, while leaving per-workflow adoption details for milestones 2 and 3.

Extend `bin/check-cross-references` or add a focused validator called from `bin/validate-plugins` to enforce:

- declared dependencies resolve to canonical skill directories;
- a dependency is not both required and optional;
- every programmatic skill-composition reference is declared;
- every declaration is used by the skill body;
- required and optional sections use the documented form;
- generated Codex and OpenCode copies preserve the declarations.

Extend `tests/fixtures/cross-reference-fixture` and `tests/scrut/check-cross-references.md` with passing and failing cases for missing, unused, duplicate, and unresolved dependency declarations. Use the `write-scrut-tests` skill before editing those snapshots.

### 5. Replace the compatibility budget check

Refactor validation rule 17 in `bin/validate-plugins` so it evaluates the generated Codex inventory rather than separate canonical and generated description totals. Keep the per-description validity checks, then add deterministic checks for:

- non-empty `name` and `description` fields;
- the official 1,024-character maximum for an individual description;
- the repository's concise-description preference;
- total inventory cost, including qualified names and installed paths;
- a clear diagnostic showing the total, cap, largest entries, and remediation.

Add fixture-driven Scrut coverage under `tests/scrut/repo-tooling.md` for a passing inventory, a single oversized description, aggregate overflow, and path/name overhead that pushes an otherwise passing description total over the cap. Do not raise the cap to accommodate current content.

Add a deterministic check that a generated skill's `name` and `description` equal its canonical source. This makes any future harness-specific transformation an explicit design change rather than a silent generator behavior.

### 6. Close milestone 1 with evidence

Update the milestone 1 checklist in `docs/plans/todo/2026-09-15-codex-consumption-improvements.md` only after its four deliverables pass. Update `docs/reviews/codex-consumption.md` findings 1, 2, 6, 7, 10, 11, 12, 13, and 20 with their current disposition: resolved by milestone 1, contract established with adoption pending, or deferred to a named later milestone.

Move this plan to `docs/plans/done/` only when all acceptance criteria are satisfied. Keep both the plan and roadmap as repository history, per the repository's plan policy.

## Commit boundaries

Use focused, GPG-signed Conventional Commits without amending:

1. `docs: record current Codex compatibility baseline`
2. `docs: define cross-harness adapter conventions`
3. `feat: preserve skill routing descriptions for Codex`
4. `feat: declare cross-skill dependencies`
5. `test: validate Codex compatibility metadata`
6. `docs: complete Codex compatibility milestone 1`

Combine adjacent boundaries only when the implementation and its validation cannot remain independently passing. Apply version changes in the commit that changes the corresponding plugin behavior or documentation.

## Validation

After each relevant boundary:

1. Run targeted Scrut suites for changed repository tooling and cross-reference fixtures.
2. Run `make build` and inspect canonical-to-generated diffs. Never hand-edit `.agents/` or `dist/`.
3. Run `make validate` and confirm the new inventory and dependency checks execute.
4. Run Markdown formatting and linting through the repository commands.

Before milestone completion:

1. Run `make test-all` and observe the final result.
2. Run `make build`, then confirm `git status --porcelain -- .agents dist` is empty.
3. Install the generated marketplace in an isolated Codex configuration, list the marketplace and plugins, install a representative plugin, inspect skill discovery, review hook trust, remove the plugin, and remove the marketplace.
4. Verify one explicit `$skill` invocation and one natural-language activation against the routing metadata. These are smoke checks for the milestone 1 contract, not the milestone 2 connected-workflow evaluation.
5. Verify the same canonical skill still loads in Claude Code and that the OpenCode mirror remains structurally current.
6. Use the `check-versions` skill before creating the PR.

Record the CLI version, model, configuration, commands, results, and relevant transcripts in the review. Keep model-backed activation checks informational until the roadmap's repeatability requirement is met.

## Acceptance criteria

Milestone 1 is complete when all of the following are true:

- The README's install, plugin-management, hook-event, and hook-trust guidance matches the supported current stable Codex CLI.
- The review contains a dated, reproducible baseline and distinguishes direct observation from official documentation.
- `docs/plugin-development.md` defines shared invocation, composition, capability, authority, permission, and continuation adapters with copyable conventions.
- Generated Codex skills preserve their canonical routing descriptions instead of receiving catalog summaries.
- Routing descriptions and catalog summaries have separate documented ownership and validation.
- The deterministic inventory check accounts for names and paths and fits within the current 8,000-character Codex fallback budget.
- Every programmatic skill dependency is classified as required or optional, resolves, and has defined missing-dependency behavior.
- Initial deterministic checks cover routing preservation, inventory size, and dependency declarations.
- `make test-all` passes, generated mirrors are current, and the isolated Codex smoke checks are recorded.
- The roadmap and review accurately mark completed, adoption-pending, and deferred work without claiming milestone 2 or 3 compatibility.

## Deferred work

The following remain outside milestone 1 and retain their roadmap ownership:

- applying adapters to the Git and review chain and evaluating connected workflows: milestone 2;
- catalog-wide invocation examples, helper resolution, worktree prompt transport, installed README links, configuration examples, notification expansion, and conditional reference loading: milestone 3;
- full macOS and Linux matrices, multiple caches, symlinks, paths with spaces, restricted destinations, complete hook payload coverage, and release-grade real-Codex evaluations: milestone 4;
- catalog recategorization from issue #394 and configuration-budget tooling from issue #373.
