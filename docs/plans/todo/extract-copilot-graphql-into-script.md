# Extract Copilot skill GraphQL operations into standalone bash script

## Context

When the `resolve-copilot-pr-feedback` skill runs, Claude Code reaches for `python3 -c '...'` to parse JSON responses from `gh api graphql` (filtering threads, extracting fields, handling pagination). This triggers a broad `python3` permission prompt. Extracting all GraphQL + JSON processing into a dedicated bash script gives it a fixed, permissionable path -- one approval for the script covers all operations, without granting blanket `python3` access.

## Plan

### 1. Create `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`

New executable bash script (755) following the `plugins/notify/scripts/notify` pattern.

**Subcommands:**

- **`fetch <owner> <repo> <pr_number>`** -- Fetches all unresolved Copilot-authored review threads. Uses `gh api graphql --paginate --slurp` with a cursor-aware query (`$endCursor`, `after: $endCursor`, `pageInfo { hasNextPage endCursor }`), pipes through `jq` to filter for unresolved + Copilot-authored threads, and outputs a clean JSON array:
  ```json
  [
    {
      "id": "PRRT_kwDONZ...",
      "path": "src/foo.ts",
      "location": "src/foo.ts:42",
      "isOutdated": false,
      "comments": [{"author": "copilot", "body": "[nitpick] Consider..."}]
    }
  ]
  ```

- **`resolve <thread_id>`** -- Resolves a thread via `resolveReviewThread` GraphQL mutation. Uses proper `-F` variable binding (no shell escaping issues). Outputs `true` on success.

- **`reply <thread_id> [--body-file <path>]`** -- Replies to a thread via `addPullRequestReviewThreadReply`. Reads body from `--body-file` or stdin (for multiline-safe input without shell escaping issues). Outputs the comment ID.

- **`reply-and-resolve <thread_id> [--body-file <path>]`** -- Combines reply + resolve, with reply body read from `--body-file` or stdin.

Key design choices:
- Uses `-F`/`-f` for GraphQL variables instead of string interpolation (eliminates the `$variable` shell escaping bugs the current SKILL.md warns about)
- Uses `--paginate --slurp` with an explicit cursor-aware query shape (`$endCursor`, `after: $endCursor`, `pageInfo { hasNextPage endCursor }`)
- `jq` filters for `isResolved == false` and explicit Copilot identities/signatures (`github-copilot[bot]`, `github-actions[bot]`, and Copilot body signatures)
- Computes the `location` field as the first non-null of `line`, `originalLine`, `startLine`, `originalStartLine`; fallback is `path:(no-line)`

### 2. Update SKILL.md

Replace raw GraphQL code blocks with script invocations. Keep all LLM-judgment sections unchanged.

**Add near the top -- script location section:**
Instruct Claude to locate and store the script path at the start. Use `${CLAUDE_PLUGIN_ROOT}/scripts/resolve-copilot-threads` with a glob fallback.

**Replace section 1 (Fetch ALL Unresolved Copilot Threads):**
Remove the two large GraphQL query blocks and manual pagination instructions. Replace with a single `"${SCRIPT}" fetch OWNER REPO PR_NUMBER` call + output format documentation.

**Replace the Thread Resolution Mutation in Critical Requirements + section 3:**
Remove both GraphQL mutation blocks. Replace with `"${SCRIPT}" resolve THREAD_ID`.

**Replace the reply mutation in section 4 (Handle Each Category):**
Remove the `addPullRequestReviewThreadReply` GraphQL block. Replace with `"${SCRIPT}" reply` and `"${SCRIPT}" reply-and-resolve`, showing stdin/`--body-file` usage for multiline-safe reply bodies.

**Remove all three `$variable` shell escaping warnings:**
No longer needed since the script uses proper `-F` variable binding.

**Update section 5 (Verify Completion):**
Replace "re-query PR with pagination" with `"${SCRIPT}" fetch OWNER REPO PR_NUMBER` expecting `[]`.

**Sections that stay unchanged:**
- Frontmatter
- PR Comments Prohibition
- Copilot instructions update requirements + file strategy + format guidance
- Comment categorization table
- Category handling logic (Nitpick/Outdated/Incorrect/Valid/Deferred decisions)
- Reply templates
- Success criteria + summary table format

### 3. Bump versions

- `plugins/resolve-copilot-pr-feedback/.claude-plugin/plugin.json`: `1.0.0` -> `1.1.0`
- `.claude-plugin/marketplace.json`: plugin version `1.0.0` -> `1.1.0`, marketplace `1.0.4` -> `1.0.5`

### 4. Update project structure docs

- `CLAUDE.md`: Add `scripts/` directory + `resolve-copilot-threads` to the tree under `resolve-copilot-pr-feedback/`

## Files to modify

| File | Action |
|------|--------|
| `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads` | Create (new) |
| `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md` | Edit |
| `plugins/resolve-copilot-pr-feedback/.claude-plugin/plugin.json` | Edit (version bump) |
| `.claude-plugin/marketplace.json` | Edit (version bumps) |
| `CLAUDE.md` | Edit (directory tree) |

## Verification

1. `bash -n` and `shellcheck` on the new script
2. Run `./scripts/resolve-copilot-threads --help` to verify usage output
3. Verify dependency and auth handling (`gh`, `jq`, GitHub auth); confirm expected non-zero exits with actionable errors when unavailable
4. Dry-run `fetch` against a real PR with Copilot comments to verify JSON output and pagination coverage
5. Verify the SKILL.md reads coherently with script references replacing raw GraphQL and preserving behavior notes (including `path:(no-line)` fallback)
