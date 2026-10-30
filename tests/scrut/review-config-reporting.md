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
