# Review config reporting

The three reviewer templates and the repository's installed blocks must give
findings outside the checklists a citation form and severity. These checks
protect the prompt contract; they do not measure model compliance.

## All reviewer surfaces allow uncited findings without fabricated rules

```scrut
$ cd "${REPO_ROOT}" && for file in plugins/set-up-review-config/skills/set-up-review-config/references/{agents-md-section,code-review-skill,review-md}.md AGENTS.md .github/skills/code-review/SKILL.md REVIEW.md; do
>   grep -q 'Otherwise start it with `Uncited:`' "${file}" &&
>   grep -q 'exact rule name' "${file}" &&
>   grep -q 'never invent a rule name' "${file}" || exit 1
> done && echo 'citation forms: six surfaces'
citation forms: six surfaces
```

## Uncited findings have impact-based severity and share the Nit cap

```scrut
$ cd "${REPO_ROOT}" && for file in plugins/set-up-review-config/skills/set-up-review-config/references/{agents-md-section,code-review-skill,review-md}.md AGENTS.md .github/skills/code-review/SKILL.md REVIEW.md; do
>   grep -q 'behavior defects, data loss or leaks, and build or release failures are Important (P1)' "${file}" &&
>   grep -q 'style, naming and wording are Nit (P2 or lower)' "${file}" &&
>   grep -q 'Important findings block merging and must all be reported' "${file}" &&
>   grep -q 'uncited Nits count toward the same five-Nit cap' "${file}" || exit 1
> done && echo 'uncited severity: six surfaces'
uncited severity: six surfaces
```

## Repeats across files become one finding when the fix is shared

```scrut
$ cd "${REPO_ROOT}" && for file in plugins/set-up-review-config/skills/set-up-review-config/references/{agents-md-section,code-review-skill,review-md}.md AGENTS.md .github/skills/code-review/SKILL.md REVIEW.md; do
>   grep -q 'Combine repeats of the same defect across files into one finding listing the affected paths' "${file}" &&
>   grep -q 'unless they need different fixes' "${file}" || exit 1
> done && echo 'repeat handling: six surfaces'
repeat handling: six surfaces
```

## A Claude workflow confirms configuration only

```scrut
$ cd "${REPO_ROOT}" && skill=plugins/set-up-review-config/skills/set-up-review-config/SKILL.md &&
>   sed -n '/### 1\. Check the Repository/,/### 2\./p' "${skill}" | grep -F 'Inspect `.github/workflows/*.yml` and `.github/workflows/*.yaml`' &&
>   grep -Fq 'a filename or a general Claude task alone does not confirm review wiring' "${skill}" &&
>   grep -Fq 'A workflow confirms configuration only' "${skill}"
*Inspect `.github/workflows/*.yml` and `.github/workflows/*.yaml`* (glob)
```

## An absent workflow leaves Claude activation unconfirmed

```scrut
$ cd "${REPO_ROOT}" && skill=plugins/set-up-review-config/skills/set-up-review-config/SKILL.md &&
>   grep -Fq 'If no review workflow is found, report "Claude Code Review: not confirmable from the repository"' "${skill}" &&
>   grep -Fq 'The Claude GitHub App can provide Code Review without a workflow' "${skill}" &&
>   grep -Fq 'Preserve step 1' "${skill}" && echo 'absent workflow: not proof of inactivity'
absent workflow: not proof of inactivity
```

## Codex activation is always unverifiable from the tree

```scrut
$ cd "${REPO_ROOT}" && skill=plugins/set-up-review-config/skills/set-up-review-config/SKILL.md &&
>   grep -Fq 'Always report "Codex cloud review: unverifiable from the repository"' "${skill}" &&
>   grep -Fq 'If Codex cloud review is enabled and runs' "${skill}" &&
>   ! grep -Fq 'so from Codex expect the Important rules only' "${skill}" && echo 'Codex: external activation'
Codex: external activation
```

## Copilot review depends on activation and a request

```scrut
$ cd "${REPO_ROOT}" && skill=plugins/set-up-review-config/skills/set-up-review-config/SKILL.md &&
>   grep -Fq 'When Copilot review is enabled and requested' "${skill}" &&
>   ! grep -Fq 'so that pull request is already reviewed with the new config' "${skill}" && echo 'Copilot: conditional review'
Copilot: conditional review
```

## Copilot installation leaves activation unconfirmed

```scrut
$ cd "${REPO_ROOT}" && skill=plugins/set-up-review-config/skills/set-up-review-config/SKILL.md &&
>   grep -Fq 'Separate **Confirmed repository wiring**' "${skill}" &&
>   grep -Fq 'from **Not confirmed**' "${skill}" &&
>   grep -Fq 'Report "Copilot review: instructions installed; activation not confirmable from the repository"' "${skill}" &&
>   grep -Fq 'Installed instruction files alone do not confirm whether any reviewer is running.' "${skill}" && echo 'Copilot: installed instructions only'
Copilot: installed instructions only
```

## The README qualifies the setup pull request

```scrut
$ cd "${REPO_ROOT}" && file=plugins/set-up-review-config/README.md &&
>   grep -Fq 'The instructions are installed; Copilot review requires external activation and a review request.' "${file}" &&
>   ! grep -Fq 'so that pull request is already reviewed with the new config' "${file}" && echo 'README: installation only'
README: installation only
```

## Bootstrap reports installation separately from activation

```scrut
$ cd "${REPO_ROOT}" && file=plugins/bootstrap-project/skills/bootstrap-project/SKILL.md &&
>   grep -Fq 'Report installed instructions separately from confirmed wiring; reviewer activation is not confirmed by installation.' "${file}" &&
>   ! grep -Fq 'so that pull request is already reviewed with the new config' "${file}" && echo 'bootstrap: installation only'
bootstrap: installation only
```
