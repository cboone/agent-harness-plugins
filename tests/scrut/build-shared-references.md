# Shared reference copies

Tests for `bin/build-shared-references`, which copies a reference that skills
in two plugins read into the plugin that does not hold its source. Each
testcase runs in a throwaway tree holding every source path, so
the script's own list of copies applies unchanged.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
$ function tree() {
>   local root
>   root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")"
>   mkdir -p "${root}/plugins/publish-report-board/skills/publish-report-board/references"
>   printf '%s\n' '# Progress Model' > "${root}/plugins/publish-report-board/skills/publish-report-board/references/progress-model.md"
>   mkdir -p "${root}/plugins/review-anti-patterns/skills/review-anti-patterns/references"
>   printf '%s\n' '# Running a Skill Through codex exec' > "${root}/plugins/review-anti-patterns/skills/review-anti-patterns/references/codex-exec.md"
>   mkdir -p "${root}/plugins/review-until-clean/scripts"
>   printf '%s\n' '# Shared review Git policy' > "${root}/plugins/review-until-clean/scripts/review-git.bash"
>   printf '%s\n' "${root}"
> }
> source_file=plugins/publish-report-board/skills/publish-report-board/references/progress-model.md
> copy_file=plugins/suggest-next-issue/skills/suggest-next-issue/references/progress-model.md
```

## Writes a missing copy, byte for byte

```scrut
$ cd "$(tree)" && "${BUILD_SHARED_REFERENCES_BIN}" && cmp "${source_file}" "${copy_file}" && echo identical
Shared references: 4 copied (4 written).
identical
```

## A second run changes nothing

```scrut
$ cd "$(tree)" && "${BUILD_SHARED_REFERENCES_BIN}" > /dev/null && "${BUILD_SHARED_REFERENCES_BIN}"
Shared references: 4 copied (0 written).
```

## Rewrites a copy edited by hand

```scrut
$ cd "$(tree)" && "${BUILD_SHARED_REFERENCES_BIN}" > /dev/null && printf '%s\n' 'edited' >> "${copy_file}" && "${BUILD_SHARED_REFERENCES_BIN}" && cmp "${source_file}" "${copy_file}" && echo identical
Shared references: 4 copied (1 written).
identical
```

## Check mode passes on current copies

```scrut
$ cd "$(tree)" && "${BUILD_SHARED_REFERENCES_BIN}" > /dev/null && "${BUILD_SHARED_REFERENCES_BIN}" --check && echo passed
passed
```

## Check mode reports a missing copy and writes nothing

```scrut
$ cd "$(tree)" && { "${BUILD_SHARED_REFERENCES_BIN}" --check; echo "exit ${?}"; } && test ! -e "${copy_file}" && echo "not written"
::error::Shared reference copy 'plugins/review-pr-with-codex/scripts/review-git.bash' is missing; run make build
::error::Shared reference copy 'plugins/suggest-next-issue/skills/suggest-next-issue/references/progress-model.md' is missing; run make build
::error::Shared reference copy 'plugins/trim-comments/skills/trim-comments/references/codex-exec.md' is missing; run make build
::error::Shared reference copy 'plugins/trim-text/skills/trim-text/references/codex-exec.md' is missing; run make build
4 shared reference error(s) found.
exit 1
not written
```

## Check mode reports a stale copy

```scrut
$ cd "$(tree)" && "${BUILD_SHARED_REFERENCES_BIN}" > /dev/null && printf '%s\n' 'edited' >> "${source_file}" && "${BUILD_SHARED_REFERENCES_BIN}" --check
::error::Shared reference copy 'plugins/suggest-next-issue/skills/suggest-next-issue/references/progress-model.md' does not match its source 'plugins/publish-report-board/skills/publish-report-board/references/progress-model.md'; edit the source, not the copy, and run make build
1 shared reference error(s) found.
[1]
```

## A missing source stops the build before any copy is written

```scrut
$ cd "$(tree)" && rm "${source_file}" && { "${BUILD_SHARED_REFERENCES_BIN}"; echo "exit ${?}"; } && test ! -e "${copy_file}" && echo "not written"
::error::Shared reference source 'plugins/publish-report-board/skills/publish-report-board/references/progress-model.md' is missing; restore it, or remove its entry from bin/build-shared-references
1 shared reference error(s) found.
exit 1
not written
```

## Usage errors

```scrut
$ cd "$(tree)" && "${BUILD_SHARED_REFERENCES_BIN}" --write 2>&1
build-shared-references: unknown argument '--write'
Usage: build-shared-references [--check]
[2]
```

```scrut
$ cd "$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && "${BUILD_SHARED_REFERENCES_BIN}" 2>&1
build-shared-references: no plugins/ directory in * (glob)
[2]
```
