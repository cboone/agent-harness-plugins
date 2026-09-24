# Translate extended SKILL.md frontmatter for the Codex and OpenCode mirrors

Issue: [#474](https://github.com/cboone/agent-harness-plugins/issues/474)

## Context

All 62 canonical `SKILL.md` files use exactly two frontmatter fields, `name` and `description`. Claude Code supports many more, and four follow-up issues propose adopting some of them: [#475](https://github.com/cboone/agent-harness-plugins/issues/475) (`disable-model-invocation`), [#476](https://github.com/cboone/agent-harness-plugins/issues/476) (`allowed-tools`), [#477](https://github.com/cboone/agent-harness-plugins/issues/477) (`paths`) and [#478](https://github.com/cboone/agent-harness-plugins/issues/478) (`context: fork`, `agent`).

None of those can land safely until the distribution paths are understood. `bin/build-codex-marketplace` copies each skill into `dist/codex/plugins/` with `cp -R`, and rule 16b of `bin/validate-plugins` fails if any generated `SKILL.md` differs from its canonical source by a single byte. `bin/build-opencode-mirror` copies nothing; it creates relative symlinks, so OpenCode reads the Claude Code frontmatter verbatim. Nothing in the repository records what either harness does with a field it does not know, and nothing rejects a misspelled field such as `disable-model-invokation`, which would be silently ignored everywhere.

The intended outcome: the behavior of each target harness is recorded, `bin/build-codex-marketplace` translates the one field that Codex expresses differently, `bin/validate-plugins` rejects unknown frontmatter fields, and the existing mirrors regenerate byte-identically because no skill uses an extended field yet.

### Correction to the issue's premise

The issue states that `bin/build-codex-marketplace` rewrites the `description` field with shorter Codex-facing text. It does not. `copy_codex_plugin_roots` runs `cp -R` and then rewrites only relative links in each `README.md`; `SKILL.md` files pass through untouched, and rule 16b exists to keep it that way. The description rewrite the issue describes was removed earlier, and the `rewriting-generator` scrut scenario exists to prove it cannot come back. This plan therefore introduces the first sanctioned transformation rather than extending an existing one.

## Findings

Measured by installing probe skills under a throwaway `CODEX_HOME` and a throwaway OpenCode project, then listing what each harness offers the model. The published documentation and the installed binaries agree with the measurement, except that Codex's documentation is silent on unrecognized fields.

| Harness           | Unknown frontmatter field                     | `disable-model-invocation: true`           |
| ----------------- | --------------------------------------------- | ------------------------------------------ |
| Claude Code       | Reported by `claude plugin validate --strict` | Native behavior                            |
| Codex CLI 0.155.1 | Ignored, no warning, skill still offered      | **Ignored, skill still offered**           |
| OpenCode 1.18.31  | Ignored, no warning, skill still offered      | Ignored, skill stays implicitly selectable |

Codex's counterpart works and is the reason the translation is load-bearing rather than cosmetic: a probe skill whose `agents/openai.yaml` sets `policy.allow_implicit_invocation: false` is withheld from the model's list, and flipping that one value to `true` makes it reappear. Copying `disable-model-invocation` through to Codex would therefore lose the author's intent silently.

Codex's bundled plugin validator is stricter than its runtime and rejects the field outright ("frontmatter field `disable-model-invocation` must be false"), which points at the same counterpart.

Corroborating precedent already in the repository: `docs/plans/done/2026-04-27-add-opencode-mirror-config.md` records that OpenCode silently dropped `disable-model-invocation` and `argument-hint` from command files and kept only `description`.

Consequence: the OpenCode mirror stays pure symlinks. Only the Codex path needs a translation step, and only for `disable-model-invocation`. OpenCode has no counterpart at all, so a skill that disables model invocation stays selectable there; OpenCode gates skills through the `skill` key of its own permission configuration instead.

## Changes

### 1. Measure both harnesses and record the result

Probe each harness offline against a scratch skill carrying the full candidate field set, then a second one with `disable-model-invocation: true`.

- Codex: isolate with `CODEX_HOME` pointed at a scratch directory so the real `~/.codex` is untouched. Install the scratch plugin through a local marketplace, then render `codex debug prompt-input` and inspect the `<skills_instructions>` block plus stderr.
- OpenCode: create a scratch project holding `.opencode/skills/<name>/SKILL.md`, then run `opencode debug skill --print-logs --log-level DEBUG` and inspect both the JSON entry and the logs.

Record the CLI versions, the commands and the outcome. Findings go in `docs/plugin-development.md`; the raw transcripts go in the pull request body, not the repository.

The translation in step 2 follows the measurement rather than the documentation, because Codex's documentation does not cover unrecognized fields and its bundled plugin validator is stricter than its runtime.

### 2. Translate `disable-model-invocation` in `bin/build-codex-marketplace`

Add a `translate_codex_skill_frontmatter` function, called per skill from `copy_codex_plugin_roots` after `cp -R`:

- A canonical `disable-model-invocation: true` is removed from the generated `SKILL.md`, and `dist/codex/plugins/<plugin>/skills/<skill>/agents/openai.yaml` is written with `policy: allow_implicit_invocation: false`.
- `disable-model-invocation: false` and an absent field are left alone. `false` is Codex's default and its validator accepts it, so there is nothing to express.
- Every other permitted field passes through unchanged, because both harnesses ignore what they do not recognize. This is the issue's "kept if Codex ignores them" branch.
- A skill that already ships `agents/openai.yaml` is an error rather than an overwrite, until a skill actually needs both. Codex's own guidance is to update such a file in place, and no skill ships one today.

Rewrite the script's header comment, which currently states that skills are copied unchanged.

### 3. Narrow rule 16b in `bin/validate-plugins`

Rule 16b currently asserts `cmp -s canonical generated`. Replace that with the narrowest assertion that still blocks an unsanctioned transformation:

- The generated `SKILL.md` must equal the canonical one after removing a `disable-model-invocation: true` line, and nothing else.
- When that line was removed, the generated `agents/openai.yaml` must exist and carry `policy.allow_implicit_invocation: false`.
- When it was not, a generated `agents/openai.yaml` must match a canonical one byte for byte, and must not appear at all when the canonical skill ships none. A manifest a skill ships itself is copied like any other file, so it is held to the same identity the `SKILL.md` is.

Express this in the validator independently rather than by calling the generator, so rule 16b stays an external check on the generator instead of a restatement of it. Update its comment: the invariant is no longer byte identity, it is that the only permitted difference is the documented translation.

### 4. Add rule 21, a frontmatter field allowlist

A new rule after rule 20, with its own loop over `plugins/*/skills/*/SKILL.md` and a `frontmatter_fields` awk helper that prints the top-level keys of the frontmatter block. Any key outside the allowlist is an error naming the file and the key.

The allowlist is the Agent Skills spec fields plus the Claude Code fields the follow-up issues adopt:

| Field                      | Source                                                                          | Codex      | OpenCode |
| -------------------------- | ------------------------------------------------------------------------------- | ---------- | -------- |
| `name`                     | Spec, required                                                                  | Read       | Read     |
| `description`              | Spec, required                                                                  | Read       | Read     |
| `license`                  | Spec                                                                            | Ignored    | Read     |
| `compatibility`            | Spec                                                                            | Ignored    | Read     |
| `metadata`                 | Spec                                                                            | Read       | Read     |
| `allowed-tools`            | Spec, Claude Code                                                               | Ignored    | Ignored  |
| `disable-model-invocation` | Claude Code, [#475](https://github.com/cboone/agent-harness-plugins/issues/475) | Translated | Ignored  |
| `paths`                    | Claude Code, [#477](https://github.com/cboone/agent-harness-plugins/issues/477) | Ignored    | Ignored  |
| `context`                  | Claude Code, [#478](https://github.com/cboone/agent-harness-plugins/issues/478) | Ignored    | Ignored  |
| `agent`                    | Claude Code, [#478](https://github.com/cboone/agent-harness-plugins/issues/478) | Ignored    | Ignored  |
| `argument-hint`            | Claude Code                                                                     | Ignored    | Ignored  |

Fields Claude Code supports but this repository does not ship, among them `model`, `effort`, `when_to_use`, `arguments`, `disallowed-tools`, `user-invocable`, `background`, `shell` and `hooks`, fail rule 21. Widening the allowlist is a deliberate change that carries a measured Codex and OpenCode outcome with it. State that in the rule's comment and in `docs/plugin-development.md`, so the rule reads as a policy rather than an oversight.

### 5. Leave `bin/build-opencode-mirror` as symlinks

No behavior change. Add a header sentence recording why symlinks remain correct: OpenCode ignores frontmatter fields it does not recognize, so a Claude Code field reaching it verbatim costs nothing. Without that note the next reader has to redo step 1's measurement.

### 6. Tests

New fixture `tests/fixtures/codex-translation-fixture`, following the `review-checklist-fixture` pattern: build a small plugin tree holding one skill with `disable-model-invocation: true` and one without, print the temporary root, and let each testcase `cd` into it and run the generator. Register `CODEX_TRANSLATION_FIXTURE_BIN` in both `Makefile` `SCRUT_ENV` and `.github/workflows/ci.yml` `scrut-env`, because a local-only registration leaves CI testing a different environment.

New `tests/scrut/build-codex-marketplace.md` covering the generator directly, which has no test of its own today:

- The translated skill's generated `SKILL.md` has no `disable-model-invocation` line, and its `agents/openai.yaml` holds the policy.
- The untranslated skill's generated `SKILL.md` is identical to its source, and it gets no `agents/openai.yaml`.
- A second run changes nothing.
- A skill that already ships `agents/openai.yaml` fails with a clear message.

New scenarios in `tests/fixtures/validate-plugin-fixture`, with matching testcases in `tests/scrut/repo-tooling.md`:

- `unknown-frontmatter-field`: inject `disable-model-invokation: true`, the typo the issue names, and expect a rule 21 error.
- `permitted-frontmatter-field`: inject `paths`, and expect validation to pass.
- `quoted-invocation-value`: inject `disable-model-invocation: "true"`, which neither the generator nor rule 16b reads, and expect a rule 21 error.
- `translated-frontmatter`: set `disable-model-invocation: true` on one skill, and expect the build and validation to pass.
- `untranslated-frontmatter`: wrap the generator so it leaves the line in place, the way `wrap_generator_with_rewrite` already does for descriptions, and expect a rule 16b error.
- `missing-openai-yaml`: wrap the generator so it strips the line without writing the policy file, and expect a rule 16b error.

### 7. Documentation

New `## Skill frontmatter` section in `docs/plugin-development.md`, placed after `## Plugin layout`:

- The allowlist table from step 4, with each field's handling in each harness.
- The measured statement of what each harness does with an unrecognized field, naming the CLI versions measured.
- The `disable-model-invocation` translation, the generated `agents/openai.yaml`, and the narrowed rule 16b invariant.
- Why the OpenCode mirror stays symlinks.

Update in place, elsewhere in the same file:

- The `## Routing descriptions and catalog summaries` paragraph stating that the generator copies `SKILL.md` into `dist/codex/` unchanged and that rule 16b fails on any difference.
- The sentence stating that no skill needs an `agents/openai.yaml` today, which the generator can now produce.

Add a line to `bin/AGENTS.md` naming the translation as the generator's one sanctioned `SKILL.md` transformation, alongside the existing delegation notes.

## Out of scope

- Adopting any extended field in a real skill. That is [#475](https://github.com/cboone/agent-harness-plugins/issues/475) through [#478](https://github.com/cboone/agent-harness-plugins/issues/478), which this work unblocks.
- Running `claude plugin validate` in CI, which is [#480](https://github.com/cboone/agent-harness-plugins/issues/480). Rule 21 is this repository's own allowlist and does not depend on it.
- Generating `agents/openai.yaml` `interface` or `dependencies` content. The existing rule against setting `interface.short_description` stands, because Codex prints it in place of the routing description.

## Files

| Path                                       | Change                                                      |
| ------------------------------------------ | ----------------------------------------------------------- |
| `bin/build-codex-marketplace`              | Translation function, call site, header comment             |
| `bin/validate-plugins`                     | Narrowed rule 16b, new rule 21, `frontmatter_fields` helper |
| `bin/build-opencode-mirror`                | Header comment only                                         |
| `bin/AGENTS.md`                            | One line on the sanctioned transformation                   |
| `docs/plugin-development.md`               | New frontmatter section, two in-place corrections           |
| `tests/fixtures/codex-translation-fixture` | New                                                         |
| `tests/fixtures/validate-plugin-fixture`   | Five scenarios                                              |
| `tests/scrut/build-codex-marketplace.md`   | New                                                         |
| `tests/scrut/repo-tooling.md`              | Five testcases                                              |
| `Makefile`, `.github/workflows/ci.yml`     | Register `CODEX_TRANSLATION_FIXTURE_BIN`                    |

No plugin sources change, so no plugin version bumps and no `.claude-plugin/marketplace.json` edit. Confirm with the `check-versions` skill before opening the pull request.

## Verification

1. `make build`, then `git status --porcelain dist/ .agents/` prints nothing. No skill uses an extended field, so every mirror regenerates byte-identically. This is the issue's last acceptance criterion.
2. `make validate` passes.
3. `make test-scrut` passes, including the new suite. Observe the final result rather than an intermediate line.
4. `make lint` passes, covering the new fixture through `bin/list-shell-scripts`, which discovers executable Bash scripts by content and needs no glob change.
5. `make test-all` passes end to end.
6. Plant the defects the new checks claim to catch, and confirm each goes red before reverting:
   - Add `disable-model-invokation: true` to a skill; rule 21 fails.
   - Add `model: opus` to a skill; rule 21 fails, because the field is outside the allowlist rather than misspelled.
   - Add `disable-model-invocation: true` to a skill, run `make build`, and confirm the generated `SKILL.md` loses the line and gains `agents/openai.yaml`; then hand-edit the generated file to restore the line and confirm rule 16b fails.
7. Re-run the step 1 probes against the translated output: install the generated `dist/codex` plugin under a scratch `CODEX_HOME` and confirm Codex reports no validation error and treats the skill as explicit-only.
