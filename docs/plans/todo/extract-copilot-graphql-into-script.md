# Extract Copilot skill GraphQL operations into standalone bash script

## Context

When the `resolve-copilot-pr-feedback` skill runs, SKILL.md instructs Claude to construct raw `gh api graphql -f query='...'` commands with inline-substituted values. This is fragile: shell escaping warnings appear four times in SKILL.md, manual pagination requires Claude to loop with cursor values, and each distinct `gh api graphql` invocation triggers a separate permission prompt. Extracting all GraphQL + JSON processing into a dedicated bash script gives it a fixed, permissionable path -- one approval for the script covers all operations, eliminates shell escaping issues, and handles pagination automatically.

## Plan

### 1. Create `plugins/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads`

New executable bash script (755) following the `plugins/notify/scripts/notify` pattern.

**Subcommands:**

- **`fetch <owner> <repo> <pr_number>`** -- Fetches all unresolved Copilot-authored review threads. Uses `gh api graphql --paginate --slurp` which automatically manages cursor-based pagination (the query must declare `$endCursor: String` and use `after: $endCursor` plus `pageInfo { hasNextPage endCursor }` so `gh` can auto-inject cursor values across pages). Pipes the slurped JSON array through `jq` to filter for unresolved + Copilot-authored threads, and outputs a clean JSON array:
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

- **`resolve <thread_id>`** -- Resolves a thread via `resolveReviewThread` GraphQL mutation. Uses `-f` string variable binding (no shell escaping issues). Outputs `true` on success.

- **`reply <thread_id> [--body-file <path>]`** -- Replies to a thread via `addPullRequestReviewThreadReply`. Reads body from `--body-file` or stdin (for multiline-safe input without shell escaping issues). Outputs the comment ID.

- **`reply-and-resolve <thread_id> [--body-file <path>]`** -- Combines reply + resolve, with reply body read from `--body-file` or stdin.

Key design choices:
- Uses `-F`/`-f` for GraphQL variables instead of string interpolation (eliminates the `$variable` shell escaping bugs the current SKILL.md warns about in four places)
- Pagination is fully automatic: `gh --paginate` handles cursor injection when the query declares `$endCursor: String` and includes the required `pageInfo` shape -- the script does NOT manually loop or pass cursors
- `jq` filters for `isResolved == false` and explicit Copilot identities/signatures; the script documents which author logins it matches (`github-copilot[bot]`, `github-actions[bot]`) and which body signatures it checks, so future maintainers understand the heuristics
- Computes the `location` field as the first non-null of `line`, `originalLine`, `startLine`, `originalStartLine`; fallback is `path:(no-line)`
- Checks for required dependencies (`gh`, `jq`) at startup; prints actionable error to stderr and exits 1 if missing
- Verifies GitHub auth (`gh auth status`) and exits 1 with guidance if not authenticated

### 2. Update SKILL.md

Replace raw GraphQL code blocks with script invocations. Keep all LLM-judgment sections unchanged.

**Add near the top -- script location section:**
Instruct Claude to locate and store the script path at the start. `CLAUDE_PLUGIN_ROOT` is expanded by the hooks system but is not available as a shell environment variable during skill execution. Instead, tell Claude to find the script by searching for `**/resolve-copilot-pr-feedback/scripts/resolve-copilot-threads` (e.g., via glob or `find`) and store the result in a `SCRIPT` variable for the rest of the session.

**Replace section 1 (Fetch ALL Unresolved Copilot Threads):**
Remove the two large GraphQL query blocks and manual pagination instructions. Replace with a single `"${SCRIPT}" fetch OWNER REPO PR_NUMBER` call + output format documentation.

**Replace the Thread Resolution Mutation in Critical Requirements + section 3:**
Remove both GraphQL mutation blocks. Replace with `"${SCRIPT}" resolve THREAD_ID`.

**Replace the reply mutation in section 4 (Handle Each Category):**
Remove the `addPullRequestReviewThreadReply` GraphQL block. Replace with `"${SCRIPT}" reply` and `"${SCRIPT}" reply-and-resolve`, showing stdin/`--body-file` usage for multiline-safe reply bodies.

**Remove all four `$variable` shell escaping warnings** (lines 46, 133, 222, 247)**:**
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
3. Verify dependency checks: run with `gh` or `jq` absent from `PATH` and confirm non-zero exit with actionable stderr message; run without GitHub auth and confirm similar behavior
4. Dry-run `fetch` against a real PR with Copilot comments to verify JSON output shape and pagination coverage
5. Dry-run `resolve`, `reply`, and `reply-and-resolve` against a real PR to verify mutations work end-to-end (use a test PR or already-resolved threads to avoid side effects)
6. Verify the SKILL.md reads coherently with script references replacing raw GraphQL and preserving behavior notes (including `path:(no-line)` fallback)
