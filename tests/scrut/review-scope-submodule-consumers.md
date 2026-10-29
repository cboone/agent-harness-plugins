# Recursive submodule scope consumers

The single shared membership contract assertion runs for every fixture. It reads the actual stored digest blob and compares its path set with scope output, prompt input, validation, changes acceptance, gate and symlink discovery. Every success case runs collection through prompt rendering, aspect validation,
change reporting and the gate using the same captured file paths. Fixtures use
local repositories and isolated configuration; no reviewer is launched.

## Untracked embedded checkouts expand to reviewable files

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" embedded
true
true
```

## Uninitialized nested gitlinks remain pointer-only entries

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" embedded-uninitialized
true
true
```

## Committed gitlink content has precise editable membership

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" committed-consumption
true
true
```

## A staged gitlink differing from the checkout has precise membership

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" staged-consumption
true
true
```

## Nested committed gitlink content has precise membership

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" nested-consumption
true
```

## Recursive untracked symlinks receive link-only annotations

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" symlink
{"path":"module/new-link","kind":"symlink","target":"../../outside"}
```

## Missing initialized-child objects preserve Git diagnostics

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" unavailable 2>&1
fatal: * (glob)
review-scope: could not read current gitlink object: module
[1]
```

## Every consumer rejects directory and uninventoried untracked entries

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" contract-rejection
12 contract rejections verified
```

## Gitlink replacements review symlink text and ordinary file content

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" replacement
true
true
true
true
```

## Option-like checkout paths work initialized and uninitialized

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" option-path
true
true
true
```

## A replaced parent directory cannot redirect a captured gitlink into a target

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" ancestor-replacement
true
true
```

## Option-like checkout paths and untracked symlinks share the rooted contract

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" symlink-option
{"path":"-vendor/new-link","kind":"symlink","target":"../../outside"}
```

## Child path-record write errors cannot return partial success

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" record-write-failure
printf: sample path-record write failure
codex-aspects: could not record changed path module/nested/file in * (glob)
```

## Initialization path-record errors remain fatal before later successful children

```scrut
$ "${REVIEW_SUBMODULE_FIXTURE_BIN}" transition-write-failure
printf: sample path-record write failure
codex-aspects: could not record initialization path module/nested in * (glob)
```
