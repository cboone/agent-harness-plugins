# Profile: code comments

Applies to comments and docstrings in source files, tests, scripts, stylesheets and markup. Prose documents, including Markdown instructions, are outside this profile. Apply the shared standard from the owning skill; the rules here adapt it to code.

## What leads

**Lead with what the code is doing. Then the minimum why. Nothing else.** Explain the effect or purpose a reader cannot get from nearby code, rather than paraphrasing statements. A constraint leads when it is the comment's whole job.

One line is the default. Two lines when the reason needs a clause. Three or more needs a reason. Prefer the equally clear wording that will stay true longest, anchored to nearby code.

```typescript
// Bad: why first, action buried, trivia at the end
// multipart/form-data is the documented encoding for this endpoint, and the shape attachments would
// need. Node 22 ships a global FormData.

// Good
// FormData because multipart/form-data is the documented encoding for this endpoint.
```

## Comment-specific cuts and keeps

Cut unnecessary file cross-references and spec/RFC citations, restatements of nearby code, signatures, assertions and language/framework constructs. Keep a reference when another file is required to understand the code; name a file and stable symbol, never a line number. Keep a citation when its rule stops an incorrect change. Cut counts, versions and dates unless they explain why the code looks this way.

The shared keep criteria cover comments that prevent an incorrect change, explain deliberate behavior or a non-obvious external constraint, or state required absence. For example: `Content-Type is deliberately unset: fetch derives it from the FormData body.` Protected comments below outrank these criteria; otherwise retain only the reason that earns a comment its place.

## Test scaffolding

Comments above mocks, fixtures, and other test setup (`vi.mock`, `jest.mock`, `unittest.mock.patch`, fixture factories) are the most frequent offenders, because the author is mid-decision and narrates the decision instead of the line. State **what is faked and what that buys this file**, in one sentence. Nothing else.

```typescript
// Bad: two vantage points, and a second sentence restating a beforeEach further down
// Token checks talk to the auth SDK; stub it so the enforcement branch runs without a real
// auth service. Enforcement is gated on NODE_ENV=production, which the tests below set explicitly.

// Good
// Stub the auth SDK so the token-check tests run without a real auth service.
```

Do not explain what a _different_ file covers. "…and covered against real Postgres in its own DB test" is a cross-reference wearing a coverage-report costume: it tells the reader to go find something rather than telling them what is in front of them.

## One behavior per sentence

Apply the shared one-point rule to behaviors. A reason for one behavior can stay in the same sentence. For example:

```typescript
// Bad: two behaviors and an ambiguous trailing clause
// Fires on every forward exit from welcome, so a corrected phone or ZIP is resent, and on any
// later forward move while no capture has landed, which is the retry.

// Good
// Sends on every forward exit from welcome, so an edited phone or ZIP is captured.
// Later forward moves retry, until one capture lands.
```

## Stylesheets

CSS documents itself more than most code: a declaration names both the property and the value. A comment above `display: grid` saying that things stack in a grid earns nothing. Comment a rule only when a value looks arbitrary and would break something if changed.

```css
/* Bad: the two `grid-area: 1 / 1` declarations below already say this */
/* The label and the reserved width stack in one grid cell. */

/* Bad: names what `width` does, not why this value */
/* Reserves all three dots up front so the label never shifts as they cycle. */

/* Good: above `width: 1.4em`, which is otherwise an unexplained number */
/* Full three-dot width, so the label doesn't shift. */
```

One line, and let the declaration below carry the rest. "Reserves all three dots up front" is `width: 1.4em` plus a sentence; "Full three-dot width" is the part the code cannot say.

## Comment vocabulary and values

In addition to the shared plain-language rules, write "lowercases" for "case folding", "literal" or "search string" for "needle", name the value for "sentinel", and write what distinguishes environments for "discriminator". Identifiers and API names are exempt.

Name the output: "`*` returns `null`, meaning unrestricted. Unset or empty returns `[]`, which allows nothing." Check whether "For the EU region" modifies an override or its default, and whether "read per call" sounds like a network read when it means declaration placement. Rewrite or flag an ambiguous comment.

## Protected comments

- Lint and type-checker suppressions (`eslint-disable`, `ts-expect-error`, `@ts-ignore`, `noqa`, `nolint`) and their justifications
- Directive and pragma comments that a compiler, build tool, coverage tool, or formatter reads, such as `//go:build`, `//go:generate`, shebangs, encoding declarations, `/// <reference>`, `// @ts-check`, `# type: ignore`, `# pragma: no cover`, `/* istanbul ignore next */`, and `// prettier-ignore`
- Docstrings that contain doctests
- `TODO` and `FIXME` comments. Leave one with a ticket reference alone. Flag one without a ticket in the report instead of deleting it.
- License and copyright headers
- Public API doc comments that an IDE surfaces to consumers, unless they are redundant with the signature
- Comments outside the scope. Do not sweep the whole repository.

## Collect and edit comments

Resolve and filter paths with the owning skill before reading files. With explicit paths collect every comment; with a single named comment classify only that comment. In branch scope, use `git --no-pager diff --no-ext-diff --no-textconv --no-relative -U0 <merge-base> -- ":(top,literal)<file>"` to collect comments within changed hunks or directly above changed code. An untracked file is entirely changed. Do not widen branch scope when passing resolved filenames to Codex.

Identify comments using the language's syntax: line and block comments, Python docstrings, shell comments outside quoted strings and heredoc data, CSS comments, and markup comments. A string containing comment markers is code, not a comment. In mixed markup or component files, restrict edits to actual comment regions; embedded code and visible prose stay unchanged. When syntax is uncertain, flag rather than edit.

Touch only comments: no code, whitespace or formatting changes beyond what removing a comment line requires. Never delete a docstring; trim it instead. It is runtime-visible, and removing the only statement in a Python function or class would break syntax. A redundant public API doc comment may be trimmed like other comments, subject to this docstring rule. Leave unclear meaning unchanged and flag it.

## Verify unchanged code

Record each source file before editing, including pre-existing local changes. Compare the final diff against that snapshot, not only HEAD: every changed span must be an eligible comment or the line removal needed to delete one. Verify that code, string literals, directives, protected comments and non-comment whitespace are unchanged. Use a language-aware parser or token comparison where available, accounting for permitted docstring text changes; a pattern that simply strips comment markers is insufficient. If the comparison cannot establish comment-only edits, leave the file uncommitted and report verification as unresolved.

Run the project's linter and formatter in check mode on the edited files, the type checker if present, and tests covering the files, or the full test command when tests cannot be selected. Never let a formatter rewrite unrelated content. Fix failures caused by these edits by hand; report unrelated failures without fixing them. Record passed, failed and not-run checks separately. An unresolved unchanged-code check or failure caused by the edits blocks the entire trim commit, including prose files in a mixed run.

## Worked examples

One per failure class, all from review feedback. `…` marks a truncated original.

| Failure                                | Before                                                                                                                                 | After                                                                                                                                                     |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Misreading                             | `…read per call rather than at module load so the secret binding only…`                                                                | deleted                                                                                                                                                   |
| Language construct                     | `A ref, not state: nothing renders from it…` above `useRef(false)`                                                                     | deleted                                                                                                                                                   |
| CSS restating the declaration          | `The label and the reserved width stack in one grid cell.` above two `grid-area: 1 / 1` declarations                                   | deleted                                                                                                                                                   |
| CSS naming the property, not the value | `Reserves all three dots up front so the label never shifts as they cycle.`                                                            | `Full three-dot width, so the label doesn't shift.`                                                                                                       |
| Argues a decision                      | `Shared with the welcome-step capture, so anything the full submit would reject…`                                                      | `Shared with the welcome-step capture.`                                                                                                                   |
| Consequence chain                      | `Timeouts and network failures are both ambiguous… deliberately unlike sms.ts… the worst case is one duplicate email…`                 | `Ambiguous: the request may have reached the mail API. Retryable anyway: a retry re-sends identical content, and a duplicate email beats a lost message.` |
| Two vantage points                     | `Token checks talk to the auth SDK; stub it… Enforcement is gated on NODE_ENV=production, which the tests below set…`                  | `Stub the auth SDK so the token-check tests run without a real auth service.`                                                                             |
| Coverage cross-reference               | `…the upsert is stubbed…, and covered against real Postgres in its own DB test.`                                                       | `Stub the DB write so these tests exercise only the handler's branches.`                                                                                  |
| Run-on with a trailing "which"         | `Fires on every forward exit from welcome, so a corrected phone or ZIP is resent, and on any later forward move…, which is the retry.` | `Sends on every forward exit from welcome, so an edited phone or ZIP is captured. Later forward moves retry, until one capture lands.`                    |

The consequence-chain rewrite keeps its reason to prevent someone from making timeouts non-retryable.
