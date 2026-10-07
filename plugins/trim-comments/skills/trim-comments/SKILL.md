---
name: trim-comments
description: >-
  Trim and rewrite code comments so each leads with what the code does, then
  the minimum why. Use for "trim comments", "clean up comments", or a comment
  that is too long or jargony.
argument-hint: "[paths...] [--dry-run]"
---

# Trim Comments

Rewrite comments in changed code to be as short as possible while still earning their place. The rules apply to comments in any language.

## Options

The user may provide these options inline:

- **paths**: A path, glob, or file list to limit the scope. Default scope is the current branch's changed files: committed changes since the base branch, plus staged, unstaged, and untracked files.
- **--dry-run**: Report proposed changes without editing.

## The standard

**Lead with what the code is doing. Then the minimum why. Nothing else.**

One line is the default. Two lines when the why genuinely needs a clause. Three or more needs a reason you could defend out loud.

```typescript
// Bad: why first, action buried, trivia at the end
// multipart/form-data is the documented encoding for this endpoint, and the shape attachments would
// need. Node 22 ships a global FormData.

// Good
// FormData because multipart/form-data is the documented encoding for this endpoint.
```

## Cut these

| Cut | Example to delete |
| --- | --- |
| Runtime, library, or language trivia | "Node 22 ships a global FormData" |
| Cross-references to other files | "See the send guard in send.ts", "unlike sms.ts and push/index.ts" |
| Spec and RFC citations | "local-parts are case-sensitive per RFC 5321" |
| Justification for why the comment's own claim matters | "Two passes, because neither is sufficient alone" |
| Consequence chains | "turns a provider 400, classified non-retryable so the message would be dropped, into a failure at the call site that tests catch" |
| Restating code that sits within a few lines, not just the next one | "Enforcement is gated on NODE_ENV=production, which the tests below set explicitly" when a `beforeEach` three lines down plainly sets it |
| Arguing for a design decision the code has already made | "Shared with the welcome-step capture, **so anything the full submit would reject is not worth capturing early either**" |
| The same subject described from two vantage points | "the upsert **is stubbed here, and covered against real Postgres in its own DB test**": the reader has to track which file each clause is about |
| Asides about alternatives not taken | "The name matches the Python client's; basic auth passes either key type" |
| Lists of what something is not | "No templating, no retries, no idempotency" |
| Anything the type signature, function name, or assertion already says | a docstring that repeats the parameter names |
| Anything a language or framework construct already says | "A ref, not state: nothing renders from it and it needn't survive a refresh" above a `useRef`: "ref, not state" is the API name, and the rest is what every ref does |

When cut material is genuinely worth recording, it goes in the commit message, the PR description, the plan doc, or the repository's review instructions (such as `.github/*.instructions.md`) if its job is to stop a reviewer or Copilot re-raising it. Not inline.

## Keep these

Deleting is the default, not the goal. A comment earns its place when:

- **Someone would otherwise "fix" the code and break it.** `// split/join rather than replaceAll: tsconfig targets es2017, which predates it.`
- **The code looks wrong or arbitrary but is deliberate.** `// Deliberately one recipient per call: bulk sending is not supported here and would need its own function.`
- **A non-obvious external constraint drives it.** `// The mail API documents at most 3 tags per message, ASCII only, 128 characters max.`
- **Absence is the requirement.** `// Content-Type is deliberately unset: fetch derives it from the FormData body.`

## Test scaffolding

Comments above mocks, fixtures, and other test setup (`vi.mock`, `jest.mock`, `unittest.mock.patch`, fixture factories) are the most frequent offenders, because the author is mid-decision and narrates the decision instead of the line. State **what is faked and what that buys this file**, in one clause. Nothing else.

```typescript
// Bad: two vantage points, and a second sentence restating a beforeEach further down
// Token checks talk to the auth SDK; stub it so the enforcement branch runs without a real
// auth service. Enforcement is gated on NODE_ENV=production, which the tests below set explicitly.

// Good
// Stub the auth SDK so the token-check tests run without a real auth service.
```

Do not explain what a _different_ file covers. "…and covered against real Postgres in its own DB test" is a cross-reference wearing a coverage-report costume: it tells the reader to go find something rather than telling them what is in front of them.

## One behavior per sentence

A sentence that carries two behaviors, joined by "and" or "so", makes the reader hold the first clause while parsing the second. Split it. Trailing appositives are the worst version: a clause ending in "which is the retry" sends the reader back up the sentence to work out what "which" attaches to.

```typescript
// Bad: one sentence, two behaviors, and a trailing clause pointing back into the middle of it
// Fires on every forward exit from welcome, so a corrected phone or ZIP is resent, and on any
// later forward move while no capture has landed, which is the retry.

// Good: one behavior per sentence, the retry named where it happens
// Re-sends on every forward exit from welcome, so an edited phone or ZIP is captured.
// Later forward moves retry, until one capture lands.
```

Read each comment aloud. If you run out of breath, or have to restart it to parse it, split it.

## Stylesheets

CSS documents itself more than most code: a declaration names both the property and the value. A comment above `display: grid` saying that things stack in a grid earns nothing. Comment a rule only when a value looks arbitrary and would break something if changed.

```css
/* Bad: the two `grid-area: 1 / 1` declarations below already say this */
/* The label and the reserved width stack in one grid cell. */

/* Good: 1.4em is otherwise an unexplained number */
/* The 1.4em padding matches the Ellipsis box. */
```

One line, and let the declaration below carry the rest. The same applies to a comment naming what a property does rather than why this value: "Reserves all three dots up front so the label never shifts as they cycle" is `width: 1.4em` plus a sentence; "Full three-dot width, so the label doesn't shift" is the part the code cannot say.

## Plain words, no jargon

Replace terms of art with what they mean:

| Jargon | Write instead |
| --- | --- |
| case folding, folds case | lowercases |
| needle | the literal, the search string, or restructure the sentence |
| load-bearing | required, or state the consequence plainly |
| sentinel | name the value: "`*` means unrestricted" |
| belt-and-braces, defense in depth | say what the second check catches |
| blast radius | what a leak can reach |
| escape hatch | override |
| wart, smell | the actual problem |
| discriminator | "tells staging from prod" |

## Name real values

Describe behavior in terms of the values the code actually produces, not abstractions.

```typescript
// Bad
// `*` means unrestricted; unset or empty means allow nothing.

// Good
// `*` returns `null`, meaning unrestricted. Unset or empty returns `[]`, which allows nothing.
```

## Prefer plain active voice

```text
Bad:  making a duplicate email the worst case rather than a lost message
Good: we'd rather send a duplicate email than lose a message
```

## Check for misreadings

The worst comments in practice were not too long, they were ambiguous. Reread each as someone who has never seen the code:

| Comment | Misread as | Actually meant |
| --- | --- | --- |
| `Optional override, defaults to …/v3. For the EU region.` | the default is the EU region | the override is for the EU |
| `read per call rather than at module load` | this costs a network read per call | where the declaration sits |
| `…stubbed to drive branching, and covered against real Postgres in its own DB test` | which file is each clause about? | the subject moved mid-sentence |

If a comment can be parsed two ways, rewrite it even if it is already short.

**The tell.** Reread the comment and ask what it is _about_. If the answer is a decision the author made (why this is shared, why it is stubbed, why this file covers only part of it), it is narrating the author's thinking, not the code. Say what the line does instead, and let the decision live in the commit message or PR.

## Do not touch

- Generated files: codegen output, build output, vendored dependencies, lockfiles, and anything the repository marks as generated
- Lint and type-checker suppressions (`eslint-disable`, `ts-expect-error`, `@ts-ignore`, `noqa`, `nolint`) and their justifications
- `TODO` / `FIXME` carrying a ticket reference
- License and copyright headers
- Public API doc comments that an IDE surfaces to consumers, unless they are redundant with the signature
- Prose documents: `.md` files, including `.github/*.instructions.md`. Those have different length rules.
- Comments outside the scope. Do not sweep the whole repository.

## Workflow

### 1. Resolve scope

If the user gave paths, use them. Otherwise, find the base branch and the merge base:

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
git rev-parse --abbrev-ref origin/HEAD | sed 's@^origin/@@'
git merge-base origin/<base> HEAD
```

Use the first command that succeeds for the base name. Then collect the changed files:

```bash
git diff --name-only <merge-base>
git ls-files --others --exclude-standard
```

The first command covers committed, staged, and unstaged changes since the merge base; the second adds untracked files. Drop deleted files and anything under "Do not touch". Report the file list before editing.

### 2. Collect comments

Read each file in scope and collect every comment in or adjacent to changed code.

### 3. Classify each comment

Keep as-is, rewrite, or delete. Apply the sections above.

### 4. Edit

Skip this step with `--dry-run`. Make each change a separate, minimal edit, so each one is reviewable on its own. Touch only comments: no code, whitespace, or formatting changes beyond what removing a comment line requires.

### 5. Verify

Skip this step with `--dry-run`. Comments cannot change behavior, but formatting and lint can trip:

- the project's linter and formatter, scoped to the changed files
- the type checker, if the project has one
- the project's test command, which confirms nothing structural broke

Fix failures the edits caused. Report pre-existing failures without fixing them.

### 6. Report

Report a table: file and symbol or nearest heading, action, before, after. Keep before and after to one line each, truncating with `…`. With `--dry-run`, the table lists proposed changes.

Leave the edits uncommitted for the user to review. Suggest a `refactor:` or `style:` commit naming what was trimmed, made with the `commit` skill when it is installed, and list any cut material worth moving into that commit message or the PR description.

## Worked examples

One per failure class, all from review feedback. `…` marks a truncated original.

| Failure | Before | After |
| --- | --- | --- |
| Config narration | `…read per call rather than at module load so the secret binding only…` | deleted |
| Language construct | `A ref, not state: nothing renders from it…` above `useRef(false)` | deleted |
| CSS restating the declaration | `The label and the reserved width stack in one grid cell.` above `display: grid` | deleted |
| CSS naming the property, not the value | `Reserves all three dots up front so the label never shifts as they cycle.` | `Full three-dot width, so the label doesn't shift.` |
| Argues a decision | `Shared with the welcome-step capture, so anything the full submit would reject…` | `Shared with the welcome-step capture.` |
| Consequence chain | `Timeouts and network failures are both ambiguous… deliberately unlike sms.ts… the worst case is one duplicate email…` | `Ambiguous: the request may have reached the mail API. Retryable anyway, since a retry re-sends identical content and we'd rather send a duplicate email than lose a message.` |
| Two vantage points | `Token checks talk to the auth SDK; stub it… Enforcement is gated on NODE_ENV=production, which the tests below set…` | `Stub the auth SDK so the token-check tests run without a real auth service.` |
| Coverage cross-reference | `…the upsert is stubbed…, and covered against real Postgres in its own DB test.` | `Stub the DB write so these tests exercise only the handler's branches.` |
| Run-on with a trailing "which" | `Fires on every forward exit from welcome, so a corrected phone or ZIP is resent, and on any later forward move…, which is the retry.` | `Re-sends on every forward exit from welcome, so an edited phone or ZIP is captured. Later forward moves retry, until one capture lands.` |

## Final checks

Before finishing, confirm:

- No comment restates its own next line, or code within a few lines of it
- No file, spec, or version reference that is not preventing a regression
- No word from the jargon table
- Every remaining comment starts with what, not why
- No comment can be read two ways
- No comment argues for a design decision the code has already made
- No comment changes subject mid-sentence, from this file to another one
- Every mock or fixture comment says what is faked and what that buys _this_ file, and stops
- No sentence carries two behaviors, and no clause trails off into "which is…" pointing back up the sentence
- No comment explains what a language or framework construct does
- No CSS comment restates the declaration under it, or names what the property does rather than why this value

## Error Handling

- **No changed files**: Report that the scope is empty and stop. Suggest passing paths.
- **No base branch found**: Ask the user for the base branch or for paths, rather than guessing.
- **A given path does not exist**: Report it and continue with the paths that do.
- **A comment's meaning is unclear from the code**: Keep it and flag it in the report, rather than rewriting it into something possibly wrong.
- **Linter, formatter, or tests fail for reasons unrelated to the edits**: Report the failure and leave it unfixed.
