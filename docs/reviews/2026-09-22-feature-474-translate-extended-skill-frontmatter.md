# Branch Review: feature/474-translate-extended-skill-frontmatter

Base: `main` (merge base: `ba8fd093`)
Commits: 2
Files changed: 12 (3 added, 9 modified, 0 deleted, 0 renamed)
Reviewed through: `e9f3be31`

## Summary

The branch answers issue #474's empirical question and acts on the answer. Codex CLI 0.155.1 and OpenCode 1.18.31 were measured directly: both ignore unrecognized `SKILL.md` frontmatter silently, and Codex also ignores `disable-model-invocation`, so a skill marked explicit-only in Claude Code is still offered to the model there. `bin/build-codex-marketplace` now translates that one field into an `agents/openai.yaml` invocation policy, rule 16b of `bin/validate-plugins` permits exactly that difference and no other, and a new rule 21 holds skill frontmatter to a named allowlist. The OpenCode mirror stays relative symlinks, with the reason recorded in the script.

## Changes by Area

### Codex generation

`bin/build-codex-marketplace` gains `disables_model_invocation` and `translate_generated_skills`, called per plugin from `copy_codex_plugin_roots` after the `cp -R`. A canonical `disable-model-invocation: true` is filtered out of the generated `SKILL.md` and restated as `policy.allow_implicit_invocation: false`. `false` and an absent field pass through, because `false` is Codex's own default. A skill that already ships its own `agents/openai.yaml` fails the build rather than having it overwritten.

Files: `bin/build-codex-marketplace`

### Validation

Rule 16b changes from `cmp -s canonical generated` to a narrower assertion: the generated file must equal the canonical one with the translated line removed, the policy manifest must exist and state the policy, and a canonical `agents/openai.yaml` must be copied byte for byte. The rule reproduces the translation itself rather than calling the generator, so it remains an external check. Rule 21 is new: it parses the opening frontmatter block, rejects any key outside an eleven-field allowlist, and requires `disable-model-invocation` to be an unquoted `true` or `false`.

Files: `bin/validate-plugins`

### OpenCode mirror

No behavior change. The header records that OpenCode reads `name` and `description` and ignores every other field, measured against 1.18.31, so symlinks stay correct as skills grow frontmatter.

Files: `bin/build-opencode-mirror`

### Tests

A new `codex-translation-fixture` builds a three-plugin tree covering `true`, absent and `false`, and an `own-manifest` scenario. `tests/scrut/build-codex-marketplace.md` is the first direct coverage of that generator, which previously ran only incidentally inside the validator fixture. Six scenarios were added to `validate-plugin-fixture`, and its single-purpose `wrap_generator_with_rewrite` was generalized into a `wrap_generator` taking the edit as an argument, with three named callers.

Files: `tests/fixtures/codex-translation-fixture`, `tests/fixtures/validate-plugin-fixture`, `tests/scrut/build-codex-marketplace.md`, `tests/scrut/repo-tooling.md`

### Documentation

A new `## Skill frontmatter` section in `docs/plugin-development.md` carries the per-harness field table, the measurement with CLI versions, the translation, and the instruction to measure a field before widening the allowlist. Two existing passages were corrected in place: the claim that rule 16b fails on any difference, and the claim that an invocation-policy override belongs in a hand-written `agents/openai.yaml`.

Files: `docs/plugin-development.md`, `bin/AGENTS.md`

### Configuration

`CODEX_TRANSLATION_FIXTURE_BIN` and `BUILD_CODEX_MARKETPLACE_BIN` registered in both `Makefile` `SCRUT_ENV` and `.github/workflows/ci.yml` `scrut-env`, as `tests/AGENTS.md` requires.

Files: `Makefile`, `.github/workflows/ci.yml`

## File Inventory

### New files (3)

- `docs/plans/done/2026-09-22-translate-extended-skill-frontmatter.md`
- `tests/fixtures/codex-translation-fixture`
- `tests/scrut/build-codex-marketplace.md`

### Modified files (9)

- `.github/workflows/ci.yml`
- `Makefile`
- `bin/AGENTS.md`
- `bin/build-codex-marketplace`
- `bin/build-opencode-mirror`
- `bin/validate-plugins`
- `docs/plugin-development.md`
- `tests/fixtures/validate-plugin-fixture`
- `tests/scrut/repo-tooling.md`

### Deleted and renamed files

None.

## Notable Changes

- **A merge-gate invariant was deliberately relaxed.** Rule 16b guaranteed byte identity between a canonical `SKILL.md` and its Codex copy. It now permits one specific edit. The rule's own comment always anticipated this ("a harness-specific transformation has to change this rule on purpose"), and the replacement reproduces the edit independently rather than trusting the generator, but this is the change reviewers should weigh hardest.
- **A new merge gate was added.** Rule 21 fails CI on any frontmatter field outside the allowlist. Every existing skill uses only `name` and `description`, so nothing fails today, but the four follow-up issues each have to widen it.
- **No plugin sources changed**, so no version bumps and no marketplace edit. Mirrors regenerate byte-identically.
- No dependency, schema or security-relevant changes.

## Plan Compliance

**Compliance verdict: good, with one verification step skipped.** All seven planned changes landed, and two scope additions beyond the plan are justified. One item in the plan's own verification section was not performed.

**Overall progress: 7/7 planned changes done (100%); 6/7 verification steps performed (86%).**

### Done

1. **Measure both harnesses and record the result.** Probes installed under a throwaway `CODEX_HOME` and a throwaway OpenCode project; results in `docs/plugin-development.md` with CLI versions.
1. **Translate `disable-model-invocation`.** Implemented as planned, including the `false`-passes-through and own-manifest-fails cases.
1. **Narrow rule 16b.** Implemented, and reproduced independently of the generator as the plan required.
1. **Rule 21 allowlist.** Implemented with the eleven fields the plan named, plus the unquoted-value requirement.
1. **Leave the OpenCode mirror as symlinks.** Header comment added.
1. **Tests.** Both new files and all six scenarios landed, registered in `Makefile` and `ci.yml`.
1. **Documentation.** New section plus the two in-place corrections, and the `bin/AGENTS.md` line.

### Deviations

- **Function naming.** The plan named `translate_codex_skill_frontmatter`; the code has `translate_generated_skills` plus a `disables_model_invocation` predicate. Reasonable, the split is clearer than the single name.
- **Scope addition: canonical manifest identity.** The plan said only that no generated `agents/openai.yaml` may appear that the canonical skill does not ship. The implementation also holds a canonical manifest to byte identity. Reasonable: it closes the same class of hole rule 16b exists for, now that `agents/` is within the rule's remit.
- **Scope addition: two extra scenarios.** `quoted-invocation-value` in the validator fixture and `own-manifest` in the generator fixture. Reasonable, both cover real failure modes.

### Fidelity concerns

- **Plan verification step 7 was not performed.** The plan says to install the _generated_ `dist/codex` plugin under a scratch `CODEX_HOME` and confirm Codex reports no validation error and treats the skill as explicit-only. What was actually done is narrower: a hand-written probe skill whose `agents/openai.yaml` contained only the two policy lines, without the three comment lines the generator emits. The exact bytes this pipeline produces were never fed to Codex. The risk is low, since YAML comments are unremarkable, but this is precisely the end-to-end confirmation the step existed for, and it is cheap to run.
- **The plan was edited to match the implementation.** The findings table, the rule 16b description and the scenario list were revised after the code was written, before the plan was committed. That keeps the committed record accurate, but it means the plan is not an independent yardstick for this review, and a reader cannot tell from the diff which decisions were made before the work and which after.

## Code Quality Assessment

**Overall quality: close to ready, with one defect to fix first.** The design is sound, the comments carry their reasoning and their evidence, and every new check was confirmed to fail when its defect was planted. One check is scoped wrongly and will produce a false failure on a plausible future skill.

### Strengths

- **The measurement drove the design rather than decorating it.** Codex's bundled plugin validator rejects `disable-model-invocation` outright, which would have suggested a different fix. The running CLI ignores it. The implementation follows the runtime behavior and the documentation says so, with versions.
- **Rule 16b stays an external check.** Reproducing the translation in the validator rather than calling the generator preserves what the rule is for. Delegating to a shared helper would have made it a restatement of the generator and would have passed no matter what the generator did.
- **Every new check was verified by planting its defect**: the misspelling, an off-allowlist `model`, a quoted boolean, a generator that keeps the line, one that drops the manifest, and one that rewrites a canonical manifest.
- **A long-standing coverage gap closed.** `bin/build-codex-marketplace` had no test of its own; it now has seven cases.
- **Comments match the repository's register**, explaining why and naming the measured versions rather than restating the code.

### Issues to address

1. **Important: rule 21's value check is not scoped to the frontmatter block.** `bin/validate-plugins` runs `grep -q '^disable-model-invocation:' "${skill_md}"` over the whole file, while every other frontmatter check in the repository, including rule 21's own `frontmatter_fields`, stops at the closing `---`. A `SKILL.md` that documents the field in a fenced example at column zero fails validation for no reason. Confirmed by appending a fenced `disable-model-invocation: "true"` counter-example to a skill body, which produced `must write disable-model-invocation as an unquoted true or false`. This is not hypothetical: issue #475 adds this field to skills, and a skill that teaches skill authoring is exactly where such an example would appear. Fix by reading the value through a frontmatter-scoped helper and comparing in bash, which also removes the two greps per skill.

### Suggestions

1. **Subprocess count in rule 21.** Across 62 skills the rule spawns roughly 310 processes: one `awk` per skill, one `grep` per field for the allowlist membership test, and two more per skill for the value check. The scrut suite already hit a timeout on an unrelated testcase under parallel load during this work. Holding the allowlist in an array and testing membership in a bash loop, then folding the value check into the existing `awk` pass, removes about two thirds of them. Not blocking.
1. **"Ignored" in the field table is inferred, not measured.** The measurement establishes that each field is accepted with no warning and the skill is still offered to the model. That a field has no behavioral effect in Codex rests on the absence of any handling in the binary. The surrounding prose is precise about what was observed; the table's one-word cell is looser. A footnote, or wording such as "accepted, no effect observed", would keep the table as honest as the paragraph under it.
1. **Commit message inaccuracy in `e9f3be31`.** The body says the fixture scenarios cover "the three allowlist rejections"; there are two rejections and one acceptance. Not worth a follow-up commit, and amending is against project practice. Noted so the record is not mistaken for a count.

### Completeness

No TODO, FIXME, HACK or XXX markers, no stubs, no commented-out code. New behavior has tests, and the documentation was updated in the same commit as the code that cites it. `make test-all` reports 519 of 519 testcases passing, and `make build` leaves `dist/` and `.agents/` unchanged.
