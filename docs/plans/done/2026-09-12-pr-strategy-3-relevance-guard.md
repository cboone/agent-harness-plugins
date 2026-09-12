# Guard `pr` strategy 3 against a single weak search hit

Addresses [issue #381](https://github.com/cboone/agent-harness-plugins/issues/381).

## Context

The `pr` skill detects the issues a branch addresses with three strategies. Strategies 1 and 2 read issue numbers out of the branch name and the commit messages, so they are safe by construction: the number was written down by a person. Strategy 3 guesses, searching GitHub for the branch slug as keywords, and it is the only one that can be wrong.

Today strategy 3 applies its relevance test to only half its own results:

```markdown
- If **exactly one** issue is returned, include it.
- If **multiple** issues are returned, compare each issue title against the branch slug. Include an issue only if its title, when slugified ..., is a near-exact match with the branch slug. If no single issue clearly matches, include none.
```

The single-result case has no relevance check at all, which is backwards. A one-hit search is precisely where a weak keyword match is most likely to be the only thing returned, and `gh issue list --search` ranks by keyword overlap with no notion of whether the hit is about the same work.

The failure this produced: opening #379 from branch `feature/add-monitor-copilot-skill`, strategies 1 and 2 found nothing, and strategy 3 returned exactly one issue, #367 "New skill: triage-ci-failure". The two share only the generic word `skill`. The rule as written says to include it, which would have written `Closes #367` into the PR body and closed an unrelated open issue on merge. The slug comparison the multiple-result branch already applies rejects it cleanly: `add-monitor-copilot-skill` against `new-skill-triage-ci-failure` is nowhere near a match.

The intended outcome is that a search hit is treated as a candidate rather than a match, whatever the result count, and that "near-exact match" is stated concretely enough for an agent to apply it consistently rather than leniently.

## Changes

### 1. Rewrite the strategy 3 evaluation rules

`plugins/pr/skills/pr/SKILL.md`, step 2, "Strategy 3 -- GitHub issue search by branch slug" (currently lines 128 through 132).

Replace the three count-based bullets with a single relevance test applied to every result. The replacement:

- States that a search hit is a candidate and not a match, and that a single hit is evidence of scarcity rather than relevance. This is the actual fix.
- Makes the comparison operational: slugify the title, then require the **distinctive** words to line up, meaning the words naming the specific subject of the work. Generic tracker vocabulary (`add`, `new`, `fix`, `update`, `skill`, `ci`, `test`) does not count toward a match, because that is exactly what the false positive matched on.
- Keeps the worked example from the issue, so the rule has a concrete negative case attached to it.
- Defaults to including none when the comparison is ambiguous, and says why the asymmetry justifies that default: a missing reference costs a cross-reference that can be added by hand, a wrong one closes someone else's issue quietly at merge in a PR body that reads plausibly.
- Keeps the existing zero-result behavior unchanged.

No other section of the skill changes. Step 4 (commit message references) and step 7 (the `## Closes` section) consume the deduplicated list from step 2 and need no adjustment; narrowing what strategy 3 contributes is enough.

### 2. Version bump and catalog state

- `plugins/pr/.claude-plugin/plugin.json`: `1.8.0` to `1.8.1`. Patch, per the repo's rule that bug fixes and prompt adjustments are patches.
- `.claude-plugin/marketplace.json`: the `pr` entry version must match, and `metadata.version` is recomputed with `bin/compute-catalog-state` (expected `catalog-M65-m92-p156-n52`, to be confirmed by running the script rather than by hand).

### 3. Regenerate the mirrors

Run `make build` (`bin/build-codex-marketplace` and `bin/build-opencode-mirror`) and commit the results. Nothing under `dist/` or `.agents/` is edited by hand; CI fails if either generated tree drifts from source.

## Out of scope

`address-issue` and `address-issue-in-worktree` carry a superficially similar rule ("if the search returns exactly one result, proceed automatically"). That is a different risk profile and is deliberately left alone: the user supplied the search text in the same breath, the outcome is visible immediately, and nothing is closed. Only strategy 3 writes a closing keyword into a PR body on a guess.

`plugins/pr/README.md` needs no change. Its description already says issues are detected "from branch names and commit messages" and does not advertise the search fallback.

## Verification

1. `bin/check-cross-references plugins/pr/skills/pr/SKILL.md` for a fast check while editing.
1. `make validate` (`bin/validate-json` plus the 19 rules in `bin/validate-plugins`), which covers manifest and marketplace version agreement, the catalog state tag, and generated-tree freshness.
1. `make lint` for markdownlint, Prettier, and the shell linters.
1. `make test-scrut` for the snapshot suites.
1. `make test-all` as the single gate before opening the PR.
1. The `check-versions` skill before creating the PR, since another branch may have already moved a version.

Behavioral check against the reported case, done by reading the rewritten section rather than by executing it: branch slug `add-monitor-copilot-skill` against slugified title `new-skill-triage-ci-failure` must fall out as "include none" under the new wording, with the shared word `skill` explicitly named as non-qualifying.

## Commits

1. `fix: apply the strategy 3 relevance test to every result (#381)` for the skill body.
1. `chore: bump pr to 1.8.1 and rebuild mirrors (#381)` for the version, catalog state, and generated trees.
