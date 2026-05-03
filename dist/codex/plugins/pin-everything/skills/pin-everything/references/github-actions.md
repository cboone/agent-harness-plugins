# SHA-Pinning GitHub Actions

How to SHA-pin every `uses:` ref in a repository's workflows and composite actions.

## Why SHA-Pin

Tag refs (`@v6`, `@v6.0.2`) are mutable. An attacker (or a careless maintainer) who controls the upstream repo can repoint any tag to a different commit. The published `tj-actions/changed-files` compromise in March 2025 was a notable example: a popular action's tags were rewritten to inject token-exfiltration code, and every consumer pinned by tag was instantly affected. SHA pins are immutable — Git's content-addressable storage guarantees the commit hash refers to one specific tree forever — so the consumer takes the upgrade only when they explicitly bump the SHA.

## Resolving a Tag to a Commit SHA

Two endpoints work; one is simpler.

### Preferred: `gh api repos/<r>/commits/<tag>`

This endpoint dereferences both lightweight and annotated tags transparently and returns the commit object directly:

```bash
gh api repos/actions/checkout/commits/v6.0.2 --jq '.sha'
# → de0fac2e4500dabe0009e67214ff5f5447ce83dd
```

Use this as the default path. It's one API call and handles either tag type.

### Fallback: `gh api repos/<r>/git/ref/tags/<tag>`

The lower-level Git refs endpoint returns the raw ref object. For lightweight tags the object type is `commit` and `.object.sha` is the answer. For annotated tags the object type is `tag` and `.object.sha` is the SHA of the tag object itself; you have to dereference one more level:

```bash
ref=$(gh api repos/actions/checkout/git/ref/tags/v6.0.2)
type=$(jq -r '.object.type' <<< "$ref")
sha=$(jq -r '.object.sha' <<< "$ref")

if [[ "$type" == "tag" ]]; then
  sha=$(gh api "repos/actions/checkout/git/tags/$sha" --jq '.object.sha')
fi
echo "$sha"
```

Use this only if `commits/<tag>` is unavailable for some reason.

## Channel-Style Refs

Some actions expose a moving channel ref instead of (or alongside) a release tag. Examples:

- `dtolnay/rust-toolchain@stable` — pin the action repo, not the toolchain
- `dtolnay/rust-toolchain@1.76.0` — also valid; pins both
- `actions/setup-node@main` — generally not what you want; pin to a release tag if available

For channel refs, pin the action repo to the SHA of the named branch's HEAD:

```bash
sha=$(gh api repos/dtolnay/rust-toolchain/commits/stable --jq '.sha')
echo "uses: dtolnay/rust-toolchain@${sha} # stable"
```

The toolchain channel itself (which Rust version `stable` resolves to) is a separate concern, handled by `rust-toolchain.toml` in the consuming repo.

## Reusable Workflow Refs

Reusable workflow refs look like:

```yaml
uses: cboone/gh-actions/.github/workflows/lint-go.yml@v3.0.0
```

These are subject to the same tag-mutability risk as actions. SHA-pin them with the same approach:

```bash
gh api repos/cboone/gh-actions/commits/v3.0.0 --jq '.sha'
# → 1234567890abcdef1234567890abcdef12345678
```

Then:

```yaml
uses: cboone/gh-actions/.github/workflows/lint-go.yml@1234567890abcdef1234567890abcdef12345678 # v3.0.0
```

Tag immutability is a property of how Git refs work, not a property of repo ownership. Pin org-owned refs the same way you pin third-party ones.

## First-Party Local Refs

Composite actions referenced from inside the same repo:

```yaml
uses: ./.github/actions/local-action
```

Leave these unpinned. They resolve to the current commit by definition — there is no separate version to pin.

## Comment Format

Always append `# vX.Y.Z` (or `# stable`, or `# branch-name`) after the SHA:

```yaml
uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2
```

This serves two purposes:

1. **Dependabot reads it.** Dependabot's PR diffs use the comment to render `v6.0.2 → v6.0.3` rather than `de0fac2... → 1234abcd...`. Without the comment the diff is unreadable.
2. **Humans read it.** A reviewer can tell at a glance which version they're getting without resolving the SHA back to a tag.

If a release tag is unavailable (channel ref, branch ref), use the channel or branch name in the comment.

## Held Major Versions

Sometimes you want to hold an action at a specific major because the next major has a breaking change you have not migrated yet. The pin is the same — SHA + comment — but the comment captures the intent:

```yaml
uses: owner/action@<sha> # v2.3.4, held at v2 pending v3 migration; see ISSUE-NUMBER
```

When the upstream cuts a new patch release within the held major, Dependabot will still propose the bump. Accept it; the major boundary stays put because the comment matches the held major's tag pattern.

The bundled `version-audit-template` (step 10 of `SKILL.md`) reads pinned `# vX.Y.Z` comments and compares each one against upstream releases **within the same major series**, not against the absolute upstream latest. That is what makes the held-major comment work as an intentional pin: the audit flags a v2 -> v2.x.y patch but never an unwanted v2 -> v3 "drift" row.

## Bumping a Held Major

Before bumping, read the upstream major's release notes for breaking changes:

```bash
gh release list --repo golangci/golangci-lint-action --limit 5
gh release view --repo golangci/golangci-lint-action v9.0.0
```

Then update both the SHA and the comment in one commit so the diff is reviewable.

## Caveat: SHAs in Skill Templates Rot

Reference docs (this one included) embed SHAs that go stale as upstream cuts new releases. When this skill emits a workflow into a user's repo, refresh each `uses:` ref against current upstream first. The "Refresh own SHAs at scaffold time" section of `SKILL.md` covers the lookup pattern.
