# Default branch fallbacks

## Skill fallback commands preserve a missing ref's failure

Execute the fallback line from each canonical source in a repository with an
origin but no remote HEAD. Pipeline status is deliberately not protected by
pipefail, as a skill consumer may run it that way.

```scrut
$ work="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" \
>   && git -C "${work}" init -q --template= \
>   && git -C "${work}" remote add origin https://example.invalid/repo.git \
>   && cd "${work}" \
>   && for path in .claude/skills/check-versions/SKILL.md \
>        plugins/review-branch/skills/review-branch/SKILL.md \
>        plugins/use-git/skills/use-git/references/common-operations.md \
>        plugins/sync-with-main/skills/merge/SKILL.md \
>        plugins/sync-with-main/skills/rebase/SKILL.md \
>        plugins/workmux/skills/create-worktree/SKILL.md \
>        plugins/workmux/skills/start-issue/SKILL.md; do \
>     command_text="$(awk '/^git .*origin\/HEAD|^git remote show origin/ { print; count++ } END { if (count != 1) exit 1 }' "${REPO_ROOT}/${path}")" || exit 1; \
>     code=0; output="$(bash +o pipefail -c "${command_text}" 2>/dev/null)" || code=$?; \
>     if [[ "${code}" == 0 || -n "${output}" ]]; then printf 'invalid fallback: %s\n' "${path}"; exit 1; fi; \
>   done && echo 'all seven fallbacks report not found'
all seven fallbacks report not found
```

## A nonstandard default survives the same fallback commands

```scrut
$ cd "${work}" \
>   && git -c commit.gpgsign=false -c user.email=t@t -c user.name=t commit -qm init --allow-empty \
>   && git update-ref refs/remotes/origin/integration HEAD \
>   && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/integration \
>   && for path in .claude/skills/check-versions/SKILL.md \
>        plugins/review-branch/skills/review-branch/SKILL.md \
>        plugins/use-git/skills/use-git/references/common-operations.md \
>        plugins/sync-with-main/skills/merge/SKILL.md \
>        plugins/sync-with-main/skills/rebase/SKILL.md \
>        plugins/workmux/skills/create-worktree/SKILL.md \
>        plugins/workmux/skills/start-issue/SKILL.md; do \
>     command_text="$(awk '/^git .*origin\/HEAD|^git remote show origin/ { print; count++ } END { if (count != 1) exit 1 }' "${REPO_ROOT}/${path}")" || exit 1; \
>     output="$(bash +o pipefail -c "${command_text}")" || exit 1; \
>     [[ "${output#origin/}" == integration ]] || exit 1; \
>   done && echo 'all seven fallbacks find integration'
all seven fallbacks find integration
```
