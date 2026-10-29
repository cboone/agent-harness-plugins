# Caller environment isolation

These cases supply hostile settings inside the test process, after the suite's
environment setup. Fixture histories and repository validation must still run.
Direct validator overrides remain covered by `validate-plugins-catalog.md`.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

## Every Git consumer resets at entry

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-four-fence
tests/scrut/new-four-fence.md: source bin/lib/git-environment.bash before Git consumers
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" capture-background-pid
captured-child-pid=true
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" capture-channel-split
structured-report-and-raw-detail-preserved=true
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" capture-background-failure 2>&1
deliberate fixture failure
[7]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" capture-completion-order 2>&1
completion status=7
deliberate fixture failure
[7]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-git-namespace
Makefile: fixture variables must stay outside the GIT_* namespace
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-capture
tests/fixtures/new-capture-consumer: use capture_child for retained diagnostics
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-stderr
tests/fixtures/new-capture-consumer: use capture_child for retained diagnostics
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-capture-library
bin/lib/new-capture.bash: use capture_child for retained diagnostics
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" git-maintenance
false
false
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-scrut-runner
bin/run-scrut-documents: run Scrut through bin/run-scrut
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-scrut-update
Makefile: run Scrut through bin/run-scrut
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-scrut-ci
.github/workflows/ci.yml: run Scrut through bin/run-scrut
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-scrut-ci-reusable
.github/workflows/ci.yml: run Scrut through bin/run-scrut
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-scrut-new
tests/fixtures/new-scrut-consumer: run Scrut through bin/run-scrut
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-wrapper-reset
bin/run-scrut: source bin/lib/git-environment.bash before Git consumers
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" scrut-persistence
Result: 1 document(s) with 2 testcase(s): 2 succeeded, 0 failed and 0 skipped
```

The guard scans shell scripts and Scrut commands, including callers identified
by helper names and Makefile registrations. A reset inside a child does not
satisfy its caller. These cases also check missing and late resets.

```scrut
$ "${CHECK_FIXTURE_ENVIRONMENTS_BIN}"
All Git consumers reset their fixture environment.
```

## Corpus consumers ignore an outer repository selection

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" outer-git-dir
corpus-created=true
caller-repository-unchanged=true
```

## The repository comparison detects a changed caller file

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" outer-git-dir-mutated
caller repository changed
[1]
```

## The guard detects a missing fixture reset

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-missing-reset
tests/fixtures/review-corpus-fixture: source bin/lib/git-environment.bash before Git consumers
[1]
```

## The guard discovers new nonexecutable Git consumers

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-new-consumer
tests/fixtures/new-git-consumer: source bin/lib/git-environment.bash before Git consumers
[1]
```

## The guard rejects a reset after the first consumer

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-late-reset
tests/fixtures/new-git-consumer: source bin/lib/git-environment.bash before Git consumers
[1]
```

## Indirect Git callers require their own reset

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-indirect
tests/fixtures/new-corpus-wrapper: source bin/lib/git-environment.bash before Git consumers
[1]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" guard-registered
tests/scrut/new-corpus-consumer.md: source bin/lib/git-environment.bash before Git consumers
[1]
```

## Child fixture failures retain their diagnostic and status

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" capture-readonly 2>&1
capture_child: cannot store output in captured
[2]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" capture-readonly-failure 2>&1
deliberate fixture failure
capture_child: cannot store output in captured
[7]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" failure-maintenance 2>&1
deliberate fixture failure
[7]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" capture-forward-failure 2>&1
child stdout
child stderr
[7]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" capture-replace-failure 2>&1
failure <path>
[7]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" failure-catalog 2>&1
deliberate fixture failure
[7]
```

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" failure-budget 2>&1
deliberate fixture failure
[7]
```

## Generator paths belong to the fixture

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" fixture-paths
Codex skill inventory: * (glob)
All plugin validations passed.
generator-paths-unchanged=true
```

## Explicit fixture budgets override ambient values

```scrut
$ CODEX_REFERENCE_CONTEXT_WINDOW=1 CODEX_ENABLED_SKILL_PERCENT=101 CODEX_OTHER_SKILL_RESERVE_TOKENS=999999999 "${VALIDATE_PLUGIN_FIXTURE_BIN}" valid --context-window 1000000 --enabled-percent 1 --reserve-tokens 0
Codex skill inventory: the 1 most expensive of * skills (1 percent) cost * of 20000 tokens available under the 20000-token budget for gpt-6.1-sol. Withheld from implicit invocation and not charged: *. (glob)
All plugin validations passed.
```

## Catalog history ignores commit signing settings

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" catalog-commit
changed=true target=current
release-created-for-target=true
```

## Catalog history ignores annotated tag signing settings

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" catalog-tag
changed=true target=current
release-created-for-target=true
```

## Catalog history ignores command configuration inherited through environment

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" catalog-command-config
changed=true target=current
release-created-for-target=true
```

## Corpus history ignores configured commit hooks

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" corpus-hooks
corpus-created=true
```

## Catalog setup leaves caller-selected configuration files unchanged

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" catalog-config-file
changed=true target=current
release-created-for-target=true
```

## Corpus history ignores hooks supplied by a template directory

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" corpus-template
corpus-created=true
```

## Validation gate ignores the ambient context window

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" validate-context
bin/validate-json
All JSON files are valid.
bin/check-fixture-environments
All Git consumers reset their fixture environment.
env -u CODEX_REFERENCE_CONTEXT_WINDOW -u CODEX_ENABLED_SKILL_PERCENT \
* (glob)
Codex skill inventory: * (glob)
All plugin validations passed.
```

## Validation gate ignores the ambient enabled percentage

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" validate-percent
bin/validate-json
All JSON files are valid.
bin/check-fixture-environments
All Git consumers reset their fixture environment.
env -u CODEX_REFERENCE_CONTEXT_WINDOW -u CODEX_ENABLED_SKILL_PERCENT \
* (glob)
Codex skill inventory: * (glob)
All plugin validations passed.
```

## Validation gate ignores the ambient reserve

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" validate-reserve
bin/validate-json
All JSON files are valid.
bin/check-fixture-environments
All Git consumers reset their fixture environment.
env -u CODEX_REFERENCE_CONTEXT_WINDOW -u CODEX_ENABLED_SKILL_PERCENT \
* (glob)
Codex skill inventory: * (glob)
All plugin validations passed.
```

## Validator fixtures choose their own budgets

```scrut
$ "${ENVIRONMENT_ISOLATION_BIN}" fixture-budget
Codex skill inventory: * (glob)
All plugin validations passed.
```
