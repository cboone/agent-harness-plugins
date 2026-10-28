# Testcase environment persistence

```scrut
$ source "${REPO_ROOT}/bin/lib/git-environment.bash" \
>   && if [[ -z "${GIT_DIR+x}${CODEX_REFERENCE_CONTEXT_WINDOW+x}${CODEX_ENABLED_SKILL_PERCENT+x}${CODEX_OTHER_SKILL_RESERVE_TOKENS+x}" ]]; then echo 'case 1 clean'; else echo 'case 1 inherited'; fi
case 1 clean
```

```scrut
$ if [[ -z "${GIT_DIR+x}${CODEX_REFERENCE_CONTEXT_WINDOW+x}${CODEX_ENABLED_SKILL_PERCENT+x}${CODEX_OTHER_SKILL_RESERVE_TOKENS+x}" ]]; then echo 'case 2 clean'; else echo 'case 2 inherited'; fi
case 2 clean
```
