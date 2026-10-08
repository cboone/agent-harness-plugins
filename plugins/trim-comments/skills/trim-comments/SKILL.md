---
name: trim-comments
description: >-
  Trim and rewrite code comments in changed files or given paths: what the code
  does, then the minimum why. Use for "trim comments" or a comment that is too
  long or jargony; not for PR review comments or general code cleanup.
argument-hint: "[paths...] [--dry-run] [--no-commit]"
---

# Trim Comments

Rewrite the comments in scope to be as short as possible while still earning their place. The rules apply to comments in any language.

## Options

The user may provide these options inline:

- **paths**: A path, glob, or file list. Every comment in those files is in scope, changed or not. Without paths, the scope is the comments in or directly above code the current branch changed: committed changes since the base branch, plus staged, unstaged, and untracked files. When the user points at a single comment, that comment is the whole scope.
- **--dry-run**: Report proposed changes without editing or committing.
- **--no-commit**: Edit and verify, but leave the edits uncommitted. By default the skill commits its edits, and it never pushes.

## The standard

**Lead with what the code is doing. Then the minimum why. Nothing else.**

"What" means the effect or purpose a reader cannot get from the next few lines at a glance, not a paraphrase of the statements. A comment whose whole job is a constraint (see "Keep these") leads with the constraint instead.

One line is the default. Two lines when the why genuinely needs a clause. Three or more needs a reason you could defend out loud.

```typescript
// Bad: why first, action buried, trivia at the end
// multipart/form-data is the documented encoding for this endpoint, and the shape attachments would
// need. Node 22 ships a global FormData.

// Good
// FormData because multipart/form-data is the documented encoding for this endpoint.
```

## Write comments that stay true

A stale comment is worse than none: the reader trusts it, and nothing fails when it drifts. Prefer the wording that will stay true longest, and let that decide between otherwise equal rewrites.

- **Anchor the comment to the code beside it, not to code elsewhere.** Nearby code changes in the same diff as the comment, so a reviewer sees both. Code elsewhere changes without anyone rereading the comment.
- **Never cite line numbers.** Any edit above them shifts them. Name a function, type, constant, or file instead, so a rename makes the reference visibly wrong rather than quietly off by a few lines.
- **Leave out facts that change on their own schedule**: counts of callers or cases, version numbers, dates, "currently", "for now", "new", and lists of the places that use something. The exception is a fact that explains why the code looks the way it does (see "Keep these").
- **Prefer a lasting reason to a passing one.** "The API rejects more than 3 tags" outlives "the API rejected 4 tags in last week's outage".

## Cut these

| Cut                                                                                    | Example to delete                                                                                                                                                    |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Runtime, library, or language trivia                                                   | "Node 22 ships a global FormData"                                                                                                                                    |
| Cross-references to other files, unless the reader needs them (see "Keep these")       | "See the send guard in send.ts", "unlike sms.ts and push/index.ts"                                                                                                   |
| Line numbers                                                                           | "the retry loop at line 142 of client.ts"                                                                                                                            |
| Facts that drift on their own                                                          | "currently only called from the signup flow", "new in v3", "one of four handlers"                                                                                    |
| Spec and RFC citations, unless the cited rule is what stops a "fix" (see "Keep these") | "Parses the body as JSON, per RFC 8259" above a `JSON.parse` call                                                                                                    |
| Justification for why the comment's own claim matters                                  | "Two passes, because neither is sufficient alone"                                                                                                                    |
| Consequence chains                                                                     | "turns a provider 400, classified non-retryable so the message would be dropped, into a failure at the call site that tests catch"                                   |
| Restating code that sits within a few lines, not just the next one                     | "Enforcement is gated on NODE_ENV=production, which the tests below set explicitly" when a `beforeEach` three lines down plainly sets it                             |
| Arguing for a design decision the code has already made                                | "Shared with the welcome-step capture, **so anything the full submit would reject is not worth capturing early either**"                                             |
| The same subject described from two vantage points                                     | "the upsert **is stubbed here, and covered against real Postgres in its own DB test**": the reader has to track which file each clause is about                      |
| Asides about alternatives not taken                                                    | "The name matches the Python client's; basic auth passes either key type"                                                                                            |
| Lists of what something is not                                                         | "No templating, no retries, no idempotency"                                                                                                                          |
| Anything the type signature, function name, or assertion already says                  | a docstring that repeats the parameter names                                                                                                                         |
| Anything a language or framework construct already says                                | "A ref, not state: nothing renders from it and it needn't survive a refresh" above a `useRef`: "ref, not state" is the API name, and the rest is what every ref does |

When cut material is genuinely worth recording, it goes in the commit message, the PR description, the plan doc, or the repository's review instructions (such as `.github/copilot-instructions.md` or `.github/instructions/*.instructions.md`) if its job is to stop a reviewer or Copilot re-raising it. Not inline.

## Keep these

Deleting is the default, not the goal. A comment earns its place when one of the criteria below applies. Such a comment stays even if it matches any other rule in this skill, including "Final checks"; only "Do not touch" outranks it. Trim it to the reason it is kept.

- **Someone would otherwise "fix" the code and break it.** `// split/join rather than replaceAll: tsconfig targets es2017, which predates it.`
- **The code looks wrong or arbitrary but is deliberate.** `// Deliberately one recipient per call: bulk sending is not supported here and would need its own function.`
- **A non-obvious external constraint drives it.** `// Caps tags at 3 per message, ASCII only, 128 characters max: the mail API's documented limits.`
- **Absence is the requirement.** `// Content-Type is deliberately unset: fetch derives it from the FormData body.`
- **The code cannot be understood without another file.** Name the file and a stable symbol in it, never a line number. `// Column order must match the users table in schema.sql: inserts are positional.`

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

A sentence that carries two separate behaviors, joined by "and" or "so", makes the reader hold the first clause while parsing the second. Split it. A single "so" or "because" clause that gives the reason for one behavior is fine. Trailing appositives are the worst version: a clause ending in "which is the retry" sends the reader back up the sentence to work out what "which" attaches to.

```typescript
// Bad: one sentence, two behaviors, and a trailing clause pointing back into the middle of it
// Fires on every forward exit from welcome, so a corrected phone or ZIP is resent, and on any
// later forward move while no capture has landed, which is the retry.

// Good: one behavior per sentence, the retry named where it happens
// Sends on every forward exit from welcome, so an edited phone or ZIP is captured.
// Later forward moves retry, until one capture lands.
```

Read each comment aloud. If you run out of breath, or have to restart it to parse it, split it.

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

## Plain words, no jargon

Replace terms of art with what they mean:

| Jargon                            | Write instead                                               |
| --------------------------------- | ----------------------------------------------------------- |
| case folding, folds case          | lowercases                                                  |
| needle                            | the literal, the search string, or restructure the sentence |
| load-bearing                      | required, or state the consequence plainly                  |
| sentinel                          | name the value: "`*` means unrestricted"                    |
| belt-and-braces, defense in depth | say what the second check catches                           |
| blast radius                      | what a leak can reach                                       |
| escape hatch                      | override                                                    |
| wart, smell                       | the actual problem                                          |
| discriminator                     | "tells staging from prod"                                   |

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
Bad:  the address is lowercased by this function before the lookup is performed
Good: lowercases the address before the lookup
```

## Check for misreadings

The worst comments in practice were ambiguous, not too long. Reread each as someone who has never seen the code:

| Comment                                                   | Misread as                         | Actually meant             |
| --------------------------------------------------------- | ---------------------------------- | -------------------------- |
| `Optional override, defaults to …/v3. For the EU region.` | the default is the EU region       | the override is for the EU |
| `read per call rather than at module load`                | this costs a network read per call | where the declaration sits |

If a comment can be parsed two ways, rewrite or delete it, even if it is already short.

**The tell.** Reread the comment and ask what it is _about_. If the answer is a decision the author made (why this is shared, why it is stubbed, why this file covers only part of it), it is narrating the author's thinking, not the code, unless it meets a "Keep these" criterion. Say what the line does instead, and let the decision live in the commit message or PR.

## Do not touch

Two entries apply to whole files, generated files and prose documents, and step 1 takes those out of scope. The rest name comments inside in-scope files: step 3 keeps them, or flags a ticketless `TODO`.

- Generated files: codegen output, build output, vendored dependencies, lockfiles, and anything the repository marks as generated
- Lint and type-checker suppressions (`eslint-disable`, `ts-expect-error`, `@ts-ignore`, `noqa`, `nolint`) and their justifications
- Directive and pragma comments that a compiler, build tool, coverage tool, or formatter reads, such as `//go:build`, `//go:generate`, shebangs, encoding declarations, `/// <reference>`, `// @ts-check`, `# type: ignore`, `# pragma: no cover`, `/* istanbul ignore next */`, and `// prettier-ignore`
- Docstrings that contain doctests
- `TODO` and `FIXME` comments. Leave one with a ticket reference alone. Flag one without a ticket in the report instead of deleting it.
- License and copyright headers
- Public API doc comments that an IDE surfaces to consumers, unless they are redundant with the signature
- Prose documents: `.md` files, including Copilot instruction files. Those have different length rules.
- Comments outside the scope. Do not sweep the whole repository.

## Workflow

### 1. Resolve scope

If the user pointed at a single comment, it is the whole scope: expand its file like a user-given path below, then apply the filter at the end of this step. If the file survives, go to step 3 with that one comment as the only item to classify, reading the rest of the file only for context; otherwise report that it was skipped and why, and stop. If the user gave paths, which are relative to the current working directory like any command-line argument, expand every one of them, whether a file, a directory, or a glob, with `git ls-files -z --cached --others --exclude-standard --full-name -- ':(glob)<path>'`. Quoting keeps the shell from expanding a glob first, `:(glob)` makes `**` match any depth as in a shell, and ignored files and paths outside the repository stay out, including the contents of a named directory. Then filter the paths as described at the end of this step, and go to step 2.

Every path list in this step comes from a `-z` command: split it on NUL bytes only, never on newlines, so a filename containing a newline or quote arrives intact and unescaped. Never paste a path into command text. Keep the current path in a shell variable and pass it, with any pathspec prefix, as one double-quoted argument to every command, Git or not, including `realpath` and `test`. Every path is root-relative and these checks run from the repository root, so write it as `"./$path"` for commands other than Git; a filename beginning with `-` is then never read as an option. This applies to user-given paths here and to the changed filenames in step 2, since either can contain spaces, quotes, or shell metacharacters.

Otherwise, choose the remote: `origin` when `git remote` lists it; otherwise the current branch's upstream remote (`git config --get branch.<branch>.remote`, ignoring `.`, which means the upstream is a local branch), or the only remote when there is one. With several remotes and no upstream, treat the base as not found. Keep the chosen name in `$remote`, and the base name found next in `$base`, and quote `$branch`, `$remote`, and `$base` wherever they appear in a command, since branch and remote names are repository data and can contain shell metacharacters.

Then find the base branch name. Try these in order and use the first that prints a name:

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
git symbolic-ref --quiet --short "refs/remotes/$remote/HEAD"
```

The second prints `<remote>/<base>`; strip the `<remote>/` prefix. Treat empty output, a failed command, or a result of `HEAD` as not found.

Then find the merge base:

```bash
git merge-base "$remote/$base" HEAD
```

If `<remote>/<base>` does not exist, try the local `<base>` branch. A local branch can be behind its remote, which moves the merge base back and pulls other people's commits into scope, so say in the report when the local branch was used. If neither works, treat it as not found and see "Error Handling".

Collect the changed files. Both commands print paths from the repository root, from any working directory; `--no-relative` keeps a `diff.relative` setting from limiting the first to the current directory:

```bash
git --no-pager diff --no-ext-diff --no-textconv -z --name-only --no-relative --diff-filter=d <merge-base>
git ls-files -z --others --exclude-standard --full-name :/
```

The first command covers committed, staged, and unstaged changes since the merge base, without deleted files; the second adds untracked files.

Filter every path list, including the file of a single named comment, before reading any file. Every path is root-relative, so run these checks from the repository root (`git rev-parse --show-toplevel`), not the current directory:

- Drop generated files and prose documents, the file-level entries under "Do not touch". Its other entries are individual comments, which step 3 handles, so a file that contains one stays in scope.
- Drop secret-bearing paths, such as real environment files, private keys, and credential stores, and any path that may hold credentials but cannot be classified without reading it. Never read, search, edit, or print them; report only that secret-bearing files were skipped.
- Drop symlinks and anything reached through one, without following them, since a link can point outside the repository or to a file this filter would otherwise drop. Keep a path only when the output of `realpath "./$path"` equals the output of `realpath "$(git rev-parse --show-toplevel)"` followed by `/$path`; any symlink in any component, including a parent directory that points elsewhere inside the repository, makes them differ.
- Drop anything that is not a regular file (`test -f "./$path"` fails), such as a directory or a changed submodule, which Git lists as a single path. Never descend into a submodule.
- Drop binary files, such as images, archives, and databases: anything where `grep -Iq . "./$path"` fails, which also drops empty files, since they hold no comments.

Report the remaining file list before editing, listing untracked files separately, since they count as entirely changed and may not belong to this branch's work.

### 2. Collect comments

Read each file in scope, resolving its path from the repository root (`git rev-parse --show-toplevel`); step 1 makes every path root-relative. With paths, collect every comment in the file. With the default scope, collect comments inside a changed hunk or directly above one, using `git --no-pager diff --no-ext-diff --no-textconv -U0 <merge-base> -- ":(top,literal)<file>"` to find the changed lines without surrounding context (`top` keeps the root-relative path from step 1 correct in any working directory, and `literal` keeps a `*`, `?`, or `[` in a filename from matching other files); an untracked file counts as entirely changed.

### 3. Classify each comment

Apply the sections above and give each collected comment one action; for a single named comment, that is the only comment classified. A comment listed under "Do not touch" is always keep, with two exceptions: a ticketless `TODO` or `FIXME` is flag, and a public API doc comment that is redundant with the signature is classified like any other comment:

- **keep**: leave it unchanged
- **rewrite**: replace it with a shorter or clearer version
- **delete**: remove it
- **flag**: leave it unchanged and call it out in the report, for a `TODO` without a ticket or a comment whose meaning is unclear from the code

### 4. Edit

Skip this step with `--dry-run`.

Unless `--no-commit` was given, first record which in-scope files are clean, so step 6 never commits the user's own changes. A file is clean only when both checks pass:

- `git status --porcelain=v1 -z --untracked-files=all -- ":(top,literal)$path"` exits 0 and prints nothing: the file is tracked and matches `HEAD` in both the index and the working tree.
- `git ls-files -v -- ":(top,literal)$path"` prints the tag `H`. `git status` hides local edits to a file marked `assume-unchanged` (a lowercase tag) or `skip-worktree` (`S`), so either could carry the user's changes into the commit.

Any other result means the file is not clean, including an untracked file, staged or unstaged changes, or a check that fails or prints an error.

Make each change a separate, minimal edit, so each one maps to one row of the report. Touch only comments: no code, whitespace, or formatting changes beyond what removing a comment line requires. Never delete a docstring; trim it instead. A docstring is runtime-visible (as `__doc__` in Python), and when it is the only statement in a function or class body, deleting it is a syntax error.

### 5. Verify

Skip this step with `--dry-run`. Most comments cannot change behavior, but directives, doctests, and formatting can. Check the files this skill edited, not the rest of the branch:

- the project's linter and formatter, in check mode, on the edited files where the tool allows it. Never run a formatter that has no check mode, since it would rewrite the user's own changes too; record it as not run.
- the type checker, if the project has one
- the tests that cover the edited files, or the full test command when they cannot be selected, which confirms nothing structural broke

If a check fails because of an edit made here, fix that edit by hand rather than letting a formatter rewrite the file, which would also reformat the user's own changes. A failure is pre-existing only when it plainly does not involve these edits, such as an error in a file or test this skill did not touch; report it without fixing it. Treat every other failure as caused here.

Record each check's outcome for step 7: passed, failed, or not run with the reason, such as no type checker in the project or no test command found. Never report a check that did not run as passed.

### 6. Commit

Skip this step with `--dry-run` or `--no-commit`, when no comment was edited, or when a step 5 check still fails because of an edit made here, even in a file that will not be committed, since the commit would record a failing tree. Never push.

Commit only the edited files that step 4 recorded as clean; a single named comment follows the same rule. A file that already held uncommitted work stays uncommitted, because committing the whole file would mix the trims with the user's changes; step 7 lists it. When no edited file was clean, commit nothing.

Run every command in this step from the repository root (`git rev-parse --show-toplevel`), since `"./$path"` is root-relative. Skip the commit when it would not land on a working branch:

- `git symbolic-ref --quiet --short HEAD` fails: HEAD is detached, and a commit would belong to no branch.
- The current branch is the base branch. Step 1 found `$base` for the default scope; with paths or a single named comment, find it the same way, choosing the remote and trying the same two commands.
- The base cannot be found, since the current branch might be the default one.

Next, confirm that each committable file holds only this run's edits: `git --no-pager diff --no-ext-diff --no-textconv --no-relative HEAD -- ":(top,literal)$path"` must show only the comment changes in the step 7 table. A step 5 check that wrote files, a formatter that ignored check mode, or a user edit during the run can add other changes; leave such a file uncommitted and list it in the report. Then record each committable file's content hash, `git hash-object -- "./$path"`, and a snapshot of the whole working tree, `git status --porcelain=v1 -z --untracked-files=all :/`.

Run `git commit` with the message, then `--` and each committable file as a `":(top,literal)$path"` pathspec. Naming the paths commits only those files from the working tree, leaves anything the user staged in the index, and stages nothing if the commit fails. Write one message naming what was trimmed, following the repository's commit convention (for example, `refactor:` or `style:` where it uses Conventional Commits), with any cut material worth keeping in its body. Leave out issue references: a closing keyword such as `fixes #N` would close an issue that a comment trim did not resolve. Sign the commit when the user's or the repository's instructions require signed commits. Never amend, and never pass `--no-verify`, `--no-gpg-sign`, or any other flag that bypasses hooks or signing.

If the commit fails because of an edit made here, or a hook rejects the message written here, fix the edit or the message and retry once. Before retrying, report any working-tree change the failed attempt left behind (compare a fresh status snapshot with the recorded one), rerun the step 5 checks on any file the fix touched, confirm again that each committable file holds only this run's comment edits, and record the hashes and snapshot again. A second failure, or any other failure (a hook failing for another reason, a signing failure, a lock file, or a merge or rebase in progress), ends this step without a commit: leave the edits uncommitted and report the exact error.

After a commit, check what a hook changed, for example by running a formatter in write mode. A committed file whose recorded hash differs from `git rev-parse "HEAD:$path"` holds content this skill did not write. A new or changed entry in a fresh status snapshot, compared with the recorded one, is a file a hook left modified. Never amend or revert either kind of change; report the files.

### 7. Report

Report a table: `file:line` (in the edited file), action (`rewrite`, `delete`, or `flag`), before, after. Leave out comments kept unchanged. The report is read once, so line numbers are fine here. Keep before and after to one line each, truncating with `…`. With `--dry-run`, the table lists proposed changes.

Then report:

- each step 5 check: passed, failed, or not run, with the reason
- the commit and its branch, shown with `git log -1 --format='%h %s'` so the subject reflects any hook rewrite; or no commit, with the skip condition or the exact error from step 6
- any change a hook made beyond these edits, in the commit or left in the working tree
- edited files left uncommitted because they already held the user's work or picked up changes beyond these edits
- cut material worth moving into the PR description, or into a commit message when no commit was made

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

The consequence-chain rewrite keeps its reason because it meets a "Keep these" criterion: without it, someone would make timeouts non-retryable.

## Final checks

Before finishing, confirm:

- No comment restates its own next line, or code within a few lines of it
- Every comment kept under "Keep these" is trimmed to the reason it is kept
- No file, spec, or version reference unless it meets a "Keep these" criterion
- No line numbers, and no counts, dates, or "currently" that will drift, unless the fact explains why the code looks the way it does
- Where two rewrites say the same thing, the one that will stay true longer won
- No jargon-table term used as prose; identifiers and API names are exempt
- Every remaining comment leads with what the code does, or with the constraint that forces it
- No comment can be read two ways
- No comment argues for a design decision the code has already made, unless it meets a "Keep these" criterion
- No comment changes subject mid-sentence, from this file to another one
- Every mock or fixture comment says what is faked and what that buys _this_ file, and stops
- No sentence carries two separate behaviors, and no clause trails off into "which is…" pointing back up the sentence
- No comment explains what a language or framework construct does
- No CSS comment restates the declaration under it, or names what the property does rather than why this value

## Error Handling

- **No changed files**: Report that the scope is empty and stop. Suggest passing paths.
- **No base branch or merge base found for the default scope**: Ask the user for the base branch or for paths, rather than guessing. Use a structured question tool when the session offers one; otherwise ask in plain text and wait for the reply.
- **A given path does not exist, matches no files, or is outside the repository**: Report it and continue with the paths that do. A path that matches nothing is never skipped silently, since a root-relative path given from a subdirectory looks valid but matches nothing.
- **A comment's meaning is unclear from the code**: Keep it and flag it in the report, rather than rewriting it into something possibly wrong.
- **Linter, formatter, or tests fail for reasons unrelated to the edits**: Report the failure and leave it unfixed.
