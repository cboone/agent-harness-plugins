# Review checklist generation

Tests for `bin/build-review-checklists`, which copies each style guide's
`references/review-checklist.md` into `set-up-review-config`. Every testcase
starts from the fixture tree printed by `tests/fixtures/review-checklist-fixture`:
two valid sources, `write-alpha` and `write-beta`, and one copy, `write-gone.md`,
whose source no longer exists.

## Copies each source and removes orphaned copies

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && "${BUILD_REVIEW_CHECKLISTS_BIN}" && ls plugins/set-up-review-config/skills/set-up-review-config/references/checklists
Review checklists: 2 bundled in plugins/set-up-review-config/skills/set-up-review-config/references/checklists (2 written, 1 removed).
write-alpha.md
write-beta.md
```

## Copies are byte for byte

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && "${BUILD_REVIEW_CHECKLISTS_BIN}" > /dev/null && cmp plugins/write-alpha/skills/write-alpha/references/review-checklist.md plugins/set-up-review-config/skills/set-up-review-config/references/checklists/write-alpha.md && cmp plugins/write-beta/skills/write-beta/references/review-checklist.md plugins/set-up-review-config/skills/set-up-review-config/references/checklists/write-beta.md && echo identical
identical
```

## A second run changes nothing

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && "${BUILD_REVIEW_CHECKLISTS_BIN}" > /dev/null && "${BUILD_REVIEW_CHECKLISTS_BIN}"
Review checklists: 2 bundled in plugins/set-up-review-config/skills/set-up-review-config/references/checklists (0 written, 0 removed).
```

## The output directory override leaves the committed copies alone

`bin/validate-plugins` regenerates into a temporary directory this way and
compares.

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && REVIEW_CHECKLISTS_DIR=out "${BUILD_REVIEW_CHECKLISTS_BIN}" && ls out plugins/set-up-review-config/skills/set-up-review-config/references/checklists
Review checklists: 2 bundled in out (2 written, 0 removed).
out:
write-alpha.md
write-beta.md

plugins/set-up-review-config/skills/set-up-review-config/references/checklists:
write-gone.md
```

## Files other than Markdown copies are left in place

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && touch plugins/set-up-review-config/skills/set-up-review-config/references/checklists/notes.txt && "${BUILD_REVIEW_CHECKLISTS_BIN}" > /dev/null && ls plugins/set-up-review-config/skills/set-up-review-config/references/checklists
notes.txt
write-alpha.md
write-beta.md
```

## A checklist inside set-up-review-config itself is not a source

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && cp plugins/write-alpha/skills/write-alpha/references/review-checklist.md plugins/set-up-review-config/skills/set-up-review-config/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}"
Review checklists: 2 bundled in plugins/set-up-review-config/skills/set-up-review-config/references/checklists (2 written, 1 removed).
```

## A link to an absolute URL is accepted

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '- **Link**: See [the guide](https://example.com/guide).' >> plugins/write-alpha/skills/write-alpha/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}"
Review checklists: 2 bundled in plugins/set-up-review-config/skills/set-up-review-config/references/checklists (2 written, 1 removed).
```

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '- **Link**: See [the guide][guide].' '' '[guide]: https://example.com/guide' >> plugins/write-alpha/skills/write-alpha/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}"
Review checklists: 2 bundled in plugins/set-up-review-config/skills/set-up-review-config/references/checklists (2 written, 1 removed).
```

## A failing run writes and removes nothing

Every source is checked before anything is written, so one bad source leaves
the existing copies, the orphan included, exactly as they were.

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '- plain item' >> plugins/write-beta/skills/write-beta/references/review-checklist.md && { "${BUILD_REVIEW_CHECKLISTS_BIN}" > /dev/null; echo "exit ${?}"; } && ls plugins/set-up-review-config/skills/set-up-review-config/references/checklists
exit 1
write-gone.md
```

## The heading must name a review checklist

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && src=plugins/write-alpha/skills/write-alpha/references/review-checklist.md && { echo '# Alpha Checklist'; tail -n +2 "${src}"; } > "${src}.new" && mv "${src}.new" "${src}" && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md must start with a level-1 heading ending in "Review Checklist"
1 review checklist error(s) found; no copies were written.
[1]
```

## The three sections are required, in order

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && src=plugins/write-alpha/skills/write-alpha/references/review-checklist.md && grep -v '^## Nits$' "${src}" > "${src}.new" && mv "${src}.new" "${src}" && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md must have exactly the level-2 headings "## Important", "## Nits" and "## Do not flag", in that order
1 review checklist error(s) found; no copies were written.
[1]
```

## Every item needs a bold rule name

Reviewers cite rules by name, so an unnamed item cannot be cited.

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '- plain item' >> plugins/write-alpha/skills/write-alpha/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md has a list item without a bold rule name, which reviewers cite: - plain item
1 review checklist error(s) found; no copies were written.
[1]
```

## References that break outside this repository are rejected

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '- **Reference**: Read ./references/guide.md first.' >> plugins/write-alpha/skills/write-alpha/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md names a ./references/ path, which does not exist in the repositories the checklist is installed into
1 review checklist error(s) found; no copies were written.
[1]
```

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '- **Root**: Load ${CLAUDE_PLUGIN_ROOT}/guide.md.' >> plugins/write-alpha/skills/write-alpha/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md names the plugin-root placeholder, which is not substituted where the checklist is installed
1 review checklist error(s) found; no copies were written.
[1]
```

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '<!-- validate-plugins: ignore /example -->' >> plugins/write-alpha/skills/write-alpha/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md has a validate-plugins directive, which would be copied into other repositories
1 review checklist error(s) found; no copies were written.
[1]
```

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '- **Link**: See [the guide](../SKILL.md).' >> plugins/write-alpha/skills/write-alpha/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md has a relative link, which breaks where the checklist is installed: ](../SKILL.md)
1 review checklist error(s) found; no copies were written.
[1]
```

A reference definition breaks the same way an inline link does.

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '- **Link**: See [the guide][guide].' '' '[guide]: ../SKILL.md' >> plugins/write-alpha/skills/write-alpha/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md has a relative link, which breaks where the checklist is installed: [guide]: ../SKILL.md
1 review checklist error(s) found; no copies were written.
[1]
```

## Constructs that Markdown formatters rewrite are rejected

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '~~~text' 'example' '~~~' >> plugins/write-alpha/skills/write-alpha/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md has a code fence; installed checklists avoid constructs that Markdown formatters rewrite
1 review checklist error(s) found; no copies were written.
[1]
```

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '| Rule | Severity |' >> plugins/write-alpha/skills/write-alpha/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md has a table; installed checklists avoid constructs that Markdown formatters rewrite
1 review checklist error(s) found; no copies were written.
[1]
```

GFM table rows need no leading pipe, so the delimiter row identifies a table
written without them.

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && printf '%s\n' '' 'Rule | Severity' '--- | ---' >> plugins/write-alpha/skills/write-alpha/references/review-checklist.md && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md has a table; installed checklists avoid constructs that Markdown formatters rewrite
1 review checklist error(s) found; no copies were written.
[1]
```

## Checklists are capped in size

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && src=plugins/write-alpha/skills/write-alpha/references/review-checklist.md && head -c 5000 /dev/zero | tr '\0' 'x' >> "${src}" && echo >> "${src}" && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-alpha/skills/write-alpha/references/review-checklist.md is * bytes; review checklists are capped at 5000 (glob)
1 review checklist error(s) found; no copies were written.
[1]
```

## A checklist belongs to the skill named after its plugin

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && mkdir -p plugins/write-gamma/skills/other/references && cp plugins/write-alpha/skills/write-alpha/references/review-checklist.md plugins/write-gamma/skills/other/references/ && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
::error::plugins/write-gamma/skills/other/references/review-checklist.md sits in skill other of plugin write-gamma; a review checklist belongs to the skill named after its plugin
1 review checklist error(s) found; no copies were written.
[1]
```

## Unusable environments stop before writing

```scrut
$ cd "$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
build-review-checklists: no plugins/ directory in * (glob)
[2]
```

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && REVIEW_CHECKLISTS_DIR=/ "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
build-review-checklists: refusing to write review checklists to '/'
[2]
```

An override must name a new or empty directory, because orphan removal would
otherwise delete Markdown files the generator never wrote.

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && mkdir notes && touch notes/keep.md && { REVIEW_CHECKLISTS_DIR=notes "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1; echo "exit ${?}"; } && ls notes
build-review-checklists: REVIEW_CHECKLISTS_DIR must name a new or empty directory, since copies without a source are removed from it; 'notes' is not empty
exit 2
keep.md
```

```scrut
$ cd "$("${REVIEW_CHECKLIST_FIXTURE_BIN}")" && rm -r plugins/set-up-review-config && "${BUILD_REVIEW_CHECKLISTS_BIN}" 2>&1
build-review-checklists: plugins/set-up-review-config does not exist to receive the checklists
[2]
```

## This repository's copies match their sources

The count guards against a scan that finds nothing and passes vacuously.

```scrut
$ cd "${REPO_ROOT}" && count=0 && for src in plugins/*/skills/*/references/review-checklist.md; do guide="${src#plugins/}"; guide="${guide%%/*}"; cmp -s "${src}" "plugins/set-up-review-config/skills/set-up-review-config/references/checklists/${guide}.md" || echo "stale: ${guide}"; count=$((count + 1)); done && if ((count >= 7)); then echo "at least seven sources: yes"; else echo "at least seven sources: no"; fi
at least seven sources: yes
```
