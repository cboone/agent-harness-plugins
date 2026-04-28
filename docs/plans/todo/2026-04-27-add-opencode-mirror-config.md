# Add OpenCode Mirror Config

## Context

This repository is structured as a Claude Code plugin marketplace. Each plugin lives at `plugins/<plugin>/` and contributes either a skill (at `plugins/<plugin>/skills/<skill>/SKILL.md`) or a command (at `plugins/<plugin>/commands/<command>.md`). We want these skills and commands to be usable in OpenCode as well, without restructuring the repo or maintaining a parallel layout.

OpenCode loads skills and commands from a fixed set of directories:

| Type     | OpenCode-native (global)                    | OpenCode-native (project)          |
| -------- | ------------------------------------------- | ---------------------------------- |
| Skills   | `~/.config/opencode/skills/<name>/SKILL.md` | `.opencode/skills/<name>/SKILL.md` |
| Commands | `~/.config/opencode/commands/<name>.md`     | `.opencode/commands/<name>.md`     |

OpenCode also supports a critical extension point: the `OPENCODE_CONFIG_DIR` environment variable. When set, OpenCode treats that directory as a full additional config root and walks `skills/`, `commands/`, `agents/`, `modes/`, `plugins/`, `tools/`, and `themes/` inside it. Loading is additive: the custom directory layers on top of `~/.config/opencode/` and `.opencode/` rather than replacing them.

This means a flat mirror tree generated inside this repo, plus one env var the user exports once, lights up every skill and command in OpenCode without touching `~/.config/opencode/` or symlinking into Claude Code's plugin paths.

### Compatibility findings

Verified end-to-end against `opencode 1.14.28` using `OPENCODE_CONFIG_DIR` pointed at a temporary mirror with one symlinked skill (`commit`) and one symlinked command (`setup-ci`).

- **Skill frontmatter**: OpenCode recognizes `name`, `description`, `license`, `compatibility`, `metadata`. Unknown fields are silently ignored, so Claude Code's existing SKILL.md files load verbatim. Folder-name-must-equal-`name` is already enforced in the repo. Confirmed: `opencode debug skill` returned the `commit` skill with full description and 10,710 bytes of content.
- **Skill name regex**: `^[a-z0-9]+(-[a-z0-9]+)*$`. All 27 existing skills already conform.
- **Command files**: each `.md` becomes one command, with the filename (minus extension) as the command name. Subdirectories are not supported. The body of the markdown file is automatically used as `template`; no `template:` frontmatter field is required. Confirmed: `opencode debug config` resolved `setup-ci`'s body verbatim into `command["setup-ci"].template`. The Claude-Code-only frontmatter fields `disable-model-invocation` and `argument-hint` were silently dropped; only `description` survived alongside the auto-generated `template`.
- **Argument syntax**: OpenCode supports `$ARGUMENTS`, `$1`, `$2`, plus `` !`cmd` `` and `@file` placeholders. The first overlaps with Claude Code; the latter two are OpenCode-only and currently unused in this repo.
- **`${CLAUDE_PLUGIN_ROOT}` is not expanded**: 7 of 11 commands and 1 skill use `@${CLAUDE_PLUGIN_ROOT}/references/...` to inline reference files at runtime. `CLAUDE_PLUGIN_ROOT` is a Claude-Code-specific variable; OpenCode does not document any equivalent. The literal text passes through unchanged in the resolved config. This means the affected commands and skill will work for their inline content but their reference inclusions will not resolve. Affected commands: `add-goreleaser-homebrew`, `scaffold-go-cli`, `scaffold-go-library`, `scaffold-new-repo`, `scaffold-rust-cli`, `setup-ci`, `setup-secret-scanning`. Affected skill: `create-plugin`. See "Open Questions" for handling options.
- **Claude Code compat path interaction**: OpenCode also loads skills from `~/.claude/skills/` by default. If the user already has skills installed there, OpenCode will log warnings about duplicates when both paths supply the same skill name. Out of scope for this plan but worth noting for the README.
- **Inventory at time of writing**: 27 skills, 11 commands, zero name collisions across plugins, zero plugins that contribute both a skill and a command.

## Approach

Generate a flat mirror directory inside the repo at `dist/opencode/` containing a `skills/` subtree and a `commands/` subtree. Each entry is a relative symlink pointing back at the canonical Claude Code plugin file. The user exports `OPENCODE_CONFIG_DIR=/path/to/repo/dist/opencode` once and never has to re-run anything: edits to the canonical files propagate live through the symlinks, and `dist/` is committed so a fresh `git pull` automatically picks up new skills and commands without touching the local environment.

A small bash script at `bin/build-opencode-mirror` regenerates the mirror. It validates name uniqueness and frontmatter conformance, then wipes and recreates `dist/opencode/`. CI runs the script and fails if `git diff --exit-code dist/` produces output, which catches both forgotten regenerations and accidental hand-edits to the mirror.

## Scope

**In scope:**

- A `bin/build-opencode-mirror` bash script that regenerates `dist/opencode/{skills,commands}/` using relative symlinks
- Idempotent execution: clean and rebuild on each run, no flags
- Validation:
  - Skill folder name matches OpenCode regex
  - Skill folder name matches the `name` field in `SKILL.md` frontmatter
  - No duplicate skill names across plugins
  - No duplicate command names across plugins
  - Frontmatter `name` and `description` present in every `SKILL.md`
- Committing `dist/opencode/` so the mirror travels with the repo and a fresh clone needs no build step
- Documentation in the root `README.md` under a new "Using with OpenCode" section
- A CI step in `.github/workflows/ci.yml` that runs the script and fails on any `dist/` diff, catching forgotten regenerations
- Pre-implementation smoke tests against a real OpenCode install to confirm SKILL.md and command loading

**Out of scope:**

- A `--copy`, `--output`, `--check`, or `--clean` flag. The script does one thing: regenerate `dist/opencode/`. CI handles drift detection via `git diff`. If a use case ever needs copies or alternate output paths, add it then.
- Gitignoring `dist/`. The mirror is a committed artifact, not a build output.
- Hooks (the `notify`, `block-rm-rf`, and `update-docs-reminder` plugins). OpenCode hooks are JS/TS modules with different signatures; nothing portable to do here.
- Claude Code `plugin.json` and `marketplace.json` (no analog in OpenCode)
- A "linker plugin" inside the marketplace
- An OpenCode-side TypeScript plugin (skills are filesystem-loaded only; OpenCode plugins cannot register virtual skills)
- Installing into `~/.config/opencode/` or `~/.claude/skills/` directly
- Per-project linking into `.opencode/` inside other repos (future enhancement; the env-var approach already covers the canonical use case)
- Versioning, marketplace registration, or release tooling for the mirror script (it is repo-internal tooling, not a plugin)

## Pre-Implementation Verification

Done. Results recorded under "Compatibility findings" above. Summary:

- Symlinked skills load cleanly through `OPENCODE_CONFIG_DIR` (verified via `opencode debug skill`).
- Symlinked commands load cleanly through `OPENCODE_CONFIG_DIR`, with the markdown body automatically populated as `template` in the resolved config (verified via `opencode debug config`). No transformation required: pure symlinks work for commands, matching the simple build-script design.
- One previously-unknown limitation surfaced: `${CLAUDE_PLUGIN_ROOT}` is not expanded by OpenCode, affecting 7 commands and 1 skill that use it to inline reference files. See Open Question 1 for handling options.

The verification used these one-off commands; preserved here for re-running if OpenCode's behavior changes:

```bash
mkdir -p /tmp/opencode-mirror-test/skills /tmp/opencode-mirror-test/commands
ln -s "$(pwd)/plugins/commit/skills/commit" /tmp/opencode-mirror-test/skills/commit
ln -s "$(pwd)/plugins/setup-ci/commands/setup-ci.md" /tmp/opencode-mirror-test/commands/setup-ci.md
OPENCODE_CONFIG_DIR=/tmp/opencode-mirror-test opencode debug skill
OPENCODE_CONFIG_DIR=/tmp/opencode-mirror-test opencode debug config
```

## Files to Create

```text
bin/
└── build-opencode-mirror

dist/
└── opencode/
    ├── skills/
    │   ├── add-community-files -> ../../../plugins/add-community-files/skills/add-community-files
    │   ├── ...                                    (27 symlinks total)
    │   └── write-zsh-scripts   -> ../../../plugins/write-zsh-scripts/skills/write-zsh-scripts
    └── commands/
        ├── add-goreleaser-homebrew.md -> ../../../plugins/add-goreleaser-homebrew/commands/add-goreleaser-homebrew.md
        ├── ...                                     (11 symlinks total)
        └── update-everything.md       -> ../../../plugins/update-everything/commands/update-everything.md
```

The `dist/opencode/` tree is committed. Symlinks are stored as git blobs of mode `120000` and survive clone, pull, and worktree operations.

## Files to Modify

- `README.md`: add "Using with OpenCode" section with the one-time `OPENCODE_CONFIG_DIR` export
- `.github/workflows/ci.yml`: add a step that runs `bin/build-opencode-mirror` and fails if `git diff --exit-code dist/` shows any change
- `bin/validate-plugins`: optionally fold in the cross-plugin name uniqueness checks, since they are useful invariants regardless of OpenCode (defer if the new script's checks suffice)

No `.gitignore` change. No `plugin.json`, no `marketplace.json`, no plugin version bumps. This is repo-level tooling.

## Implementation

### 1. `bin/build-opencode-mirror`

Bash script following the conventions in `bin/validate-plugins`: `set -euo pipefail`, sectioned headers, GitHub Actions error annotations on failure.

#### CLI

```text
Usage: bin/build-opencode-mirror

Regenerates dist/opencode/{skills,commands} from plugins/*.
No flags. The script always validates, wipes, and rebuilds.
```

#### Behavior

1. **Discover sources.** Walk `plugins/*/skills/*/SKILL.md` and `plugins/*/commands/*.md` from the repo root.
2. **Validate.**
   - Each `SKILL.md` parent dir name matches `^[a-z0-9]+(-[a-z0-9]+)*$`.
   - Each `SKILL.md` has frontmatter with both `name` and `description`. Use `awk` or `sed` to extract; the existing repo does not use a YAML parser dependency, and the frontmatter is simple enough.
   - Frontmatter `name` equals the skill's parent dir name.
   - No two skills share a name. No two commands share a name (filename minus `.md`).
   - On any failure, print `::error::<message>` and exit non-zero.
3. **Recreate the mirror from scratch.**
   - `rm -rf dist/opencode`
   - `mkdir -p dist/opencode/skills dist/opencode/commands`
   - For each skill, create a relative symlink at `dist/opencode/skills/<skill-name>` pointing to `../../../plugins/<plugin>/skills/<skill-name>`.
   - For each command, create a relative symlink at `dist/opencode/commands/<command-name>.md` pointing to `../../../plugins/<plugin>/commands/<command-name>.md`.
4. **Emit summary** to stdout:

   ```text
   Built OpenCode mirror at dist/opencode
     skills:   27
     commands: 11
   ```

#### Relative-symlink calculation

Both `dist/opencode/skills/<name>` and `dist/opencode/commands/<name>.md` are exactly three levels deep, so the relative target prefix is always `../../../`. For a skill at `plugins/<plugin>/skills/<skill>`, the symlink target is `../../../plugins/<plugin>/skills/<skill>`. No general-purpose path arithmetic needed.

#### Frontmatter parsing

The repo doesn't already depend on a YAML parser. To avoid adding `yq`, parse the limited frontmatter we care about with awk:

```bash
extract_frontmatter_field() {
  local file="$1" field="$2"
  awk -v f="$field" '
    /^---$/ { fm = !fm; next }
    fm && $1 == f":" {
      sub(/^[^:]+:[[:space:]]*/, "")
      gsub(/^["'"'"']|["'"'"']$/, "")
      print
      exit
    }
  ' "$file"
}
```

This handles single-line `name:` and `description:` values. Multi-line folded scalars (`>-`) for descriptions are common in this repo (see `plugins/commit/skills/commit/SKILL.md`); for those we just need to confirm the field is non-empty, not extract the full value. Adjust the awk to also recognize `name: >` and `description: >` and treat the field as present when followed by indented content. If awk gets too gnarly, fall back to `python3 -c "import sys, re, ..."` (acceptable per repo conventions; `python3` is available on macOS by default and on the CI runner).

### 2. README.md "Using with OpenCode" section

Add at the bottom of the README, before the License section:

````markdown
## Using with OpenCode

This repository is primarily a Claude Code plugin marketplace, but the skills and commands also work in [OpenCode](https://opencode.ai) via a committed mirror at `dist/opencode/`.

```bash
export OPENCODE_CONFIG_DIR="$(pwd)/dist/opencode"
```

That is it. The mirror travels with the repo, so a fresh clone and a `git pull` are both enough to pick up new skills and commands. Edits to canonical skill or command files propagate live through the symlinks.

When adding or removing a plugin, regenerate the mirror with `bin/build-opencode-mirror` and commit the result. CI will fail if the mirror drifts.

### Known limitations

- **Hooks are not ported.** OpenCode's hook system is incompatible with Claude Code's. Skills and commands are.
- **`${CLAUDE_PLUGIN_ROOT}` references do not expand.** Some commands and one skill use Claude Code's `@${CLAUDE_PLUGIN_ROOT}/references/...` pattern to inline reference files at runtime. OpenCode does not expand this variable, so those inclusions appear to the agent as literal path strings rather than inlined content. The inline workflow text in each affected file still loads correctly. Affected commands: `/add-goreleaser-homebrew`, `/scaffold-go-cli`, `/scaffold-go-library`, `/scaffold-new-repo`, `/scaffold-rust-cli`, `/setup-ci`, `/setup-secret-scanning`. Affected skill: `create-plugin`. For full fidelity in these cases, run them in Claude Code.
````

### 3. CI integration

Add to `.github/workflows/ci.yml` after the existing `Validate plugin structure` step:

```yaml
- name: Validate OpenCode mirror is up to date
  run: |
    bin/build-opencode-mirror
    git diff --exit-code dist/
```

This catches name collisions, regex violations, missing frontmatter, AND forgotten regenerations after adding/removing plugins. The script's own validation handles the first three; the `git diff` handles the fourth.

### 4. Optional: validate-plugins extension

If we decide cross-plugin name uniqueness is valuable to enforce regardless of the OpenCode work (it is: it would also prevent `/setup-ci` colliding with a future skill named `setup-ci`), fold the uniqueness checks into `bin/validate-plugins` as new sections 10 and 11. Defer this until after the build script lands and proves out the checks.

## Testing Strategy

### Manual smoke tests (before merging)

1. Run `bin/build-opencode-mirror`, confirm `dist/opencode/skills/` has 27 entries and `dist/opencode/commands/` has 11, all symlinks.
2. `export OPENCODE_CONFIG_DIR="$(pwd)/dist/opencode"` and start OpenCode.
3. Verify the agent can see and load at least one skill (e.g. ask "what skills do you have?") and that running a command (e.g. `/lint-and-fix`) produces the expected behavior.
4. Edit a SKILL.md, restart OpenCode, confirm the edit appears (verifies symlinks work).
5. Run `bin/build-opencode-mirror` a second time against the up-to-date mirror and confirm `git diff --exit-code dist/` exits clean.
6. Delete one entry from `dist/opencode/`, run `bin/build-opencode-mirror`, confirm the deletion is reverted (idempotent rebuild).

### Negative tests

1. Temporarily rename `plugins/commit/skills/commit` to `plugins/commit/skills/Commit` and confirm the script fails with a regex error.
2. Temporarily duplicate a skill into a second plugin and confirm the script fails with a uniqueness error.
3. Temporarily blank out a `SKILL.md`'s `description` and confirm the script fails with a missing-field error.

### CI

The new CI step in `ci.yml` runs the build script on every push and PR, exercising the validation paths.

## Documentation Updates

- `README.md`: new section as described above
- `AGENTS.md` (`CLAUDE.md` symlink): no change required; this is repo tooling, not an agent-facing convention
- `docs/plans/todo/2026-04-27-add-opencode-mirror-config.md`: this plan file moves to `docs/plans/done/` after completion

## Open Questions

1. **How to handle `${CLAUDE_PLUGIN_ROOT}` references.** Resolved: accept the limitation and document it. Affected files mirror as plain symlinks alongside the rest; the inline portion of each command and skill loads correctly, and the `@${CLAUDE_PLUGIN_ROOT}/...` template inclusions degrade gracefully (the LLM sees the literal path string rather than the inlined content). The README must explicitly call out which commands and which skill are affected so OpenCode users know what to expect. If the degradation proves disruptive in practice, revisit with a build-time path-resolution pass that materializes the affected files as transformed copies instead of symlinks. Affected commands: `add-goreleaser-homebrew`, `scaffold-go-cli`, `scaffold-go-library`, `scaffold-new-repo`, `scaffold-rust-cli`, `setup-ci`, `setup-secret-scanning`. Affected skill: `create-plugin`.

2. **Should the script also produce a project-local `.opencode/` directory in arbitrary repos?** Out of scope for this plan; the env-var workflow covers the canonical use case (the user wants these tools available everywhere they run OpenCode, not selectively per project).
3. **Should we publish a separate `cboone-opencode` package or repo at some future point?** Not now. Revisit if OpenCode users without this repo cloned start asking for it.
4. **Naming of `bin/build-opencode-mirror`.** Alternatives considered: `bin/opencode-link`, `bin/sync-opencode`, `bin/generate-opencode-config`. `build-opencode-mirror` is descriptive and matches the existing `bin/validate-*` verb-noun pattern. Confirm before writing.
