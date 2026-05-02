# Add OpenCode versions of the three hook plugins

## Context

This repository already mirrors all skills and commands into `dist/opencode/` (built by `bin/build-opencode-mirror` and validated by CI), so the `OPENCODE_CONFIG_DIR=dist/opencode` install path works for everything except hooks. The root README states:

> Hooks are not ported. OpenCode's hook system is incompatible with Claude Code's. Skills and commands are.

This branch closes that gap by shipping OpenCode-native equivalents of `block-rm-rf`, `update-docs-reminder`, and `notify` so users on either harness get the same behavior from the same repo.

OpenCode does not have Claude Code's stdin-JSON-plus-exit-code subprocess hook model. It exposes plugins instead: TypeScript modules loaded into OpenCode's Bun runtime that return a typed `Hooks` object. The relevant hook keys are `tool.execute.before`, `tool.execute.after`, `event` (filtered by `event.type`), and a separate declarative `permission` system in `opencode.json`. OpenCode has no plugin manifest, no marketplace, and no `${CLAUDE_PLUGIN_ROOT}` variable; instead the plugin function receives `{ client, project, directory, worktree, $, ... }`. Source: `https://opencode.ai/docs/plugins/`, `https://opencode.ai/docs/permissions/`, types in `@opencode-ai/plugin@1.14.x`.

## Approach

Co-locate the OpenCode implementation under each existing plugin directory (one TypeScript file per hook), extend the existing mirror builder to symlink the OpenCode source into `dist/opencode/plugin/`, and rewrite (not wrap) the bash logic in TypeScript. The existing Claude Code paths (`hooks/`, `scripts/`) stay untouched so the marketplace registration and Claude Code behavior are unaffected.

Rewriting in TypeScript rather than shelling to the existing bash via Bun's `$` is the right call because:

- `notify` cannot reuse the existing transcript-extraction logic at all. OpenCode's `session.idle` event does not carry a transcript path, so the plugin must call the SDK (`client.session.messages.list`) to find the last user message.
- `update-docs-reminder` already shells out to `git` for every check. Doing that orchestration in TS is shorter and clearer than the 412-line bash, and the regexes/skip rules port verbatim.
- `block-rm-rf` is a single regex.
- It removes the hard runtime dependency on `bash` and `jq` being available inside OpenCode's environment.

The trade-off is that we now maintain two implementations per hook. Mitigation: keep regexes, skip rules, and config schema identical so behavior stays in lock-step, and verify both paths during testing.

## Repository layout changes

```text
plugins/block-rm-rf/
├── .claude-plugin/plugin.json     unchanged
├── hooks/hooks.json               unchanged
├── scripts/check-rm               unchanged
├── opencode/
│   └── index.ts                   NEW
└── README.md                      updated

plugins/notify/
├── .claude-plugin/plugin.json     unchanged
├── hooks/hooks.json               unchanged
├── scripts/notify                 unchanged
├── opencode/
│   └── index.ts                   NEW
└── README.md                      updated

plugins/update-docs-reminder/
├── .claude-plugin/plugin.json     unchanged
├── hooks/hooks.json               unchanged
├── scripts/check-docs             unchanged
├── opencode/
│   └── index.ts                   NEW
└── README.md                      updated
```

The existing Claude Code structure is preserved exactly, so `.claude-plugin/marketplace.json` does not change.

## Per-plugin design

### `plugins/block-rm-rf/opencode/index.ts`

Hook key: `tool.execute.before`, filtered to `input.tool === "bash"`. Read `output.args.command` and apply the same regex the bash script uses (`/\brm\s+(-[a-zA-Z]*r|-R|--recursive)/`). On match, `throw new Error("Use 'trash' instead of recursive rm. ...")`. The thrown message is what OpenCode surfaces as the rejection reason, mirroring the Claude Code stderr-plus-exit-2 contract.

Source of the regex and message: `plugins/block-rm-rf/scripts/check-rm`.

The README will also document the declarative alternative for users who want zero-code coverage:

```jsonc
// opencode.json
{
  "permission": {
    "bash": { "rm -*r*": "deny", "rm --recursive*": "deny" }
  }
}
```

This is glob-not-regex and does not surface a custom remediation message, so the TS plugin is the higher-fidelity option and remains the recommendation.

### `plugins/update-docs-reminder/opencode/index.ts`

Hook key: `tool.execute.after`, filtered to `input.tool === "bash"` and `input.args.command` matching `\bgit\s+commit\b`. Port the eight heuristic checks from `plugins/update-docs-reminder/scripts/check-docs` verbatim:

- `check_new_scripts` (added files in `bin/`, `scripts/`, `cmd/`)
- `check_new_directories` (top-level dirs not present at HEAD~1)
- `check_dependency_changes` (lockfiles, manifests)
- `check_config_changes` (`.env.example`, `docker-compose`, `Dockerfile`)
- `check_ci_changes` (`.github/workflows/`, `.github/actions/`)
- `check_new_env_vars` (diff scan for `os.Getenv`, `process.env`, etc.)
- `check_cli_flags` (diff scan for argparse/clap/cobra/pflag patterns)
- `check_public_api` (diff scan for new exported symbols)

Reuse the same `SKIP_PREFIXES`, `TEST_FILE_PATTERNS`, `DOC_FILE_PATTERNS` constants and the same per-project `.update-docs-reminder.json` config schema (with `enabled`, `skip_prefixes`, `checks`).

Surface the reminder by appending it to `output.output` so the agent reads it on the next turn. OpenCode has no `additionalContext` equivalent; this is the closest analogue to Claude Code's PostToolUse stdout behavior.

Run git commands via Bun's `$` shell helper, e.g. `await $\`git diff-tree --no-commit-id --name-only -r HEAD\``.

Skip conditions are identical to the bash script: merge commits, conventional `style/chore/docs/ci/test` prefixes, test-only changes, doc-only changes, first commit (no `HEAD~1`).

### `plugins/notify/opencode/index.ts`

Hook key: `event`, dispatching by `event.type`:

| OpenCode event                    | Maps from Claude Code                                      | Notification                                                                                                             |
| --------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `session.idle`                    | `Stop`                                                     | Title `Claude Code`, subtitle `<project> @ <branch>`, message = last user message (truncated to 80 chars), sound `Glass` |
| `permission.asked`                | `Notification:permission_prompt` and `:elicitation_dialog` | Subtitle empty, message `Needs permission…`, sound `Ping`                                                                |
| `experimental.session.compacting` | `PreCompact:auto`                                          | Subtitle empty, message `Auto-compacting…`, sound `Ping`                                                                 |

Fidelity loss to document in the README:

- OpenCode does not distinguish `idle_prompt` vs `elicitation_dialog` vs `permission_prompt` the way Claude Code does. We collapse the latter two into `permission.asked` and drop the standalone `idle_prompt` (its closest analogue, `session.idle`, is already used for the Stop notification).
- `experimental.session.compacting` is marked experimental in OpenCode; the README notes this may break with OpenCode upgrades.
- The last-user-message lookup uses `client.session.messages.list({ id: event.properties.sessionId })` (or whichever shape the SDK exposes for the event payload — confirm during implementation by reading `@opencode-ai/sdk` types). If unavailable, fall back to a generic "Task completed" message, matching the bash fallback.

`terminal-notifier` is invoked via Bun's `$` with the same flags as the bash script (`-title`, `-subtitle`, `-message`, `-sound`, `-group claude-code`, `-activate com.apple.Terminal`). macOS-only, same as the existing plugin.

## Mirror builder changes

`bin/build-opencode-mirror` currently scans `plugins/*/skills/*/SKILL.md` and `plugins/*/commands/*.md`. Add a third pass:

1. For each `plugins/*/opencode/index.ts`, take the parent plugin name as the symlink name.
2. Symlink it into `dist/opencode/plugin/<plugin-name>/index.ts` as a relative path back to the canonical source.
3. Validate that no two plugins claim the same name (unlikely since they live under unique dirs, but keep the duplicate-detection pattern from skills/commands for consistency).
4. Add the count to the summary at the bottom of the script.

Rationale for `dist/opencode/plugin/<plugin-name>/index.ts` rather than `dist/opencode/plugin/<plugin-name>.ts`: OpenCode's auto-load directory takes flat `.ts` files, but using a subdirectory leaves room for future per-plugin assets (a co-located `package.json` if any plugin grows npm deps, locally-defined types, etc.). Confirm OpenCode resolves directory entries with an `index.ts` during implementation; if it does not, fall back to flat `<plugin-name>.ts` symlinks.

The exact subdirectory name (`plugin` vs `plugins`) needs one verification step against OpenCode's own loader: docs reference `.opencode/plugins/` (project) and `~/.config/opencode/plugins/` (global), but with `OPENCODE_CONFIG_DIR=dist/opencode` set, OpenCode treats the dir as the global config root and the lookup path may differ by one character. Resolve before merging by reading the loader code in `github.com/anomalyco/opencode` (the repo `github.com/sst/opencode` redirects there) or by running OpenCode against the mirror.

CI already runs `bin/build-opencode-mirror && git diff --exit-code dist/` in `.github/workflows/ci.yml` (line 43), so the new symlinks get validated for free; no CI change needed.

## README changes

Per-plugin READMEs (`plugins/block-rm-rf/README.md`, `plugins/notify/README.md`, `plugins/update-docs-reminder/README.md`): add an "OpenCode" section after the existing Claude Code section, documenting:

- Installation: rely on `OPENCODE_CONFIG_DIR=$(pwd)/dist/opencode` (or symlink the `opencode/index.ts` into `~/.config/opencode/plugin/`).
- Behavior parity and any documented fidelity gaps.
- Required runtime tools (still `trash`, still `terminal-notifier`).
- For `block-rm-rf`: include the alternative declarative `permission` config snippet.

Root `README.md`:

- Remove the "Hooks are not ported" bullet from "Known limitations" (line 490).
- Optionally annotate each Hooks subsection (Security / Workflow) noting that OpenCode versions are included.
- The "Using with OpenCode" section (line 478) needs a short mention that hooks are now mirrored alongside skills and commands.

## Versioning

Per the repo's versioning rules in `CLAUDE.md`:

- `plugins/block-rm-rf/.claude-plugin/plugin.json`: `1.0.0` → `1.1.0` (new capability)
- `plugins/notify/.claude-plugin/plugin.json`: `1.0.3` → `1.1.0` (new capability)
- `plugins/update-docs-reminder/.claude-plugin/plugin.json`: `1.0.0` → `1.1.0` (new capability)
- Mirror these three bumps in `.claude-plugin/marketplace.json` entries.
- Marketplace `metadata.version` does not bump (catalog unchanged — same plugins, expanded surface).

Run `check-versions` skill before opening the PR to confirm.

## Files to modify or create

Create:

- `plugins/block-rm-rf/opencode/index.ts`
- `plugins/notify/opencode/index.ts`
- `plugins/update-docs-reminder/opencode/index.ts`

Modify:

- `bin/build-opencode-mirror` (add the third discovery pass and symlink loop)
- `plugins/block-rm-rf/README.md` (OpenCode section)
- `plugins/notify/README.md` (OpenCode section)
- `plugins/update-docs-reminder/README.md` (OpenCode section)
- `plugins/block-rm-rf/.claude-plugin/plugin.json` (version bump)
- `plugins/notify/.claude-plugin/plugin.json` (version bump)
- `plugins/update-docs-reminder/.claude-plugin/plugin.json` (version bump)
- `.claude-plugin/marketplace.json` (mirror the three version bumps)
- `README.md` (drop the "Hooks are not ported" limitation; brief note in "Using with OpenCode")

Auto-regenerated (committed):

- `dist/opencode/plugin/block-rm-rf/index.ts` (symlink)
- `dist/opencode/plugin/notify/index.ts` (symlink)
- `dist/opencode/plugin/update-docs-reminder/index.ts` (symlink)

Do not modify:

- `plugins/*/hooks/hooks.json`, `plugins/*/scripts/*` (Claude Code paths stay byte-identical)
- `dist/opencode/skills/`, `dist/opencode/commands/`

Cleanup decision: the research subagent created `docs/plans/todo/2026-04-29-opencode-hooks-research.md` as a side effect during planning. Either keep it as supporting reference for the implementer or delete it before merging. Recommend deleting unless you want a permanent OpenCode-format reference in the repo.

## Reference material to reread during implementation

- `plugins/block-rm-rf/scripts/check-rm` — regex and message
- `plugins/notify/scripts/notify` — `terminal-notifier` flag set, truncation logic, last-user-message extraction
- `plugins/update-docs-reminder/scripts/check-docs` — eight heuristic regexes, skip rules, per-project config schema
- `bin/build-opencode-mirror` — symlink-and-validate pattern to copy from
- `.github/workflows/ci.yml` line 43 — mirror validation step
- `https://opencode.ai/docs/plugins/` and `@opencode-ai/plugin` types — current `Hooks` interface

## Verification

1. `bin/build-opencode-mirror && git diff dist/` — exits clean (matches what CI checks).
2. In a scratch repo with `OPENCODE_CONFIG_DIR=$(pwd)/dist/opencode` set:
   - Ask OpenCode to run `rm -rf foo` → expect rejection with the trash remediation message.
   - Stage a meaningful change, run a non-skip-prefixed `git commit`, expect the documentation reminder to appear in the agent's next turn.
   - Trigger `session.idle` (finish a turn), expect a macOS notification with project + branch + last user message.
   - Trigger a permission prompt, expect a "Needs permission…" notification.
3. In Claude Code on the same checkout: confirm `block-rm-rf`, `notify`, and `update-docs-reminder` still behave exactly as before (no regression in the unchanged Claude Code paths).
4. Run the `check-versions` skill before opening the PR.

## Out of scope

- Publishing OpenCode plugins to npm.
- Extracting shared logic between bash and TypeScript implementations.
- Adding scrut tests for the new TypeScript plugins (could be follow-up work).
- A unified harness-agnostic plugin manifest format.
- Porting any non-hook plugin behavior.
