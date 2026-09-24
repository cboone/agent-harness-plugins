<!-- validate-plugins: ignore /code-review -->

# Reviewer backends

How to run each backend read-only, what it can and cannot see, and how to turn its output into findings.

`/code-review` below is Claude Code's own built-in command, not a plugin in this marketplace.

## The contract every backend meets

A backend is acceptable only if all four hold. A backend that cannot meet them is not usable here, however good its reviews are.

1. It runs without write access to the working tree.
1. It covers the whole scope, or states exactly what it missed.
1. Its findings end up in the schema `review-scope --schema` prints, either because the backend emitted them that way or because you transcribed its reply into it.
1. **A completed review is distinguishable from a run that did not finish**, by **every** signal the backend offers: its exit status where it runs as a process, schema validity where it is schema-constrained, and a non-empty reply in all cases. A backend section may leave out a signal only by naming it as unavailable and saying what stands in for it.

The third and fourth are separate on purpose. A backend that cannot be schema-constrained is still usable, as long as something other than the transcription tells you the review actually happened. A backend where the only evidence is a transcription you wrote yourself is not.

The fourth says "every" rather than "any" because the signals fail independently. A Codex run that exits zero having written nothing satisfies an exit-status check on its own, and that is exactly the case this loop must not read as clean.

## Codex

### Availability

```bash
command -v codex && codex --version
```

Authentication failures surface when the review runs, not before. Treat a non-zero exit with an authentication message as "backend unavailable" rather than as a failed round, and say which command reported it.

### Use `codex exec`, not `codex exec review`

This is the surprising part, so it is first. `codex exec review` is Codex's own review mode and looks like the obvious choice. It cannot meet the contract above, for three reasons measured against `codex-cli 0.155.1`:

- **`--output-schema` is accepted and ignored.** A review run with a schema still returns prose as its final message. Its output cannot be validated, so a clean result from it cannot be distinguished from a crash.
- **The scope flags are mutually exclusive with each other.** `--base`, `--uncommitted` and `--commit` cannot be combined, so no single review covers committed and uncommitted work at once:

  ```text
  error: the argument '--base <BRANCH>' cannot be used with '--uncommitted'
  ```

- **The scope flags are mutually exclusive with a custom prompt.** So the output contract cannot be supplied in instructions either:

  ```text
  error: the argument '--base <BRANCH>' cannot be used with '[PROMPT]'
  ```

Any two of those would have workarounds. All three together mean the subcommand can give a good review that this loop has no way to check. Do not switch back to it as a simplification.

Plain `codex exec` has none of those limits: the prompt sets the scope, `--output-schema` is honored, and `--sandbox read-only` makes the read-only invariant structural rather than a matter of trust.

### The invocation

```bash
review-scope --schema > "<schema-file>"

codex exec \
  --sandbox read-only \
  --ephemeral \
  --output-schema "<schema-file>" \
  -o "<out-file>" \
  "<review prompt>" < /dev/null
```

`< /dev/null` is required, not tidiness. `codex exec` appends stdin to the prompt whenever stdin is not a terminal, so a run launched from an agent harness, whose stdin is an open pipe that never reaches end of file, prints `Reading additional input from stdin...` and blocks until something kills it. Measured against `codex-cli 0.155.1`: it hung until a 12-second timeout and **never created the `-o` file**. That is the worst shape a failure can take here, because the round produces no output at all.

`--sandbox read-only` denies writes at the sandbox level. `--ephemeral` keeps the run from persisting a session. `-m` selects a model; effort comes from the Codex configuration.

The prompt names the whole scope in one pass, which is how this backend satisfies the first invariant without a second invocation:

```text
Review this repository's local changes for defects.

The scope is all of the following, and you must read all of it:
  - committed changes:  git diff <base> <head>
  - staged changes:     git diff --cached
  - unstaged changes:   git diff
  - untracked files:    <the untracked paths from review-scope>

Read the surrounding code, not only the diff. Report a finding only when you
can point to the case that goes wrong.

Set "reviewed" to exactly: <snapshot>
```

Two things about building that prompt:

- **Pass the untracked paths explicitly, and say they are not in any diff.** A reviewer told to look at "the diff" will not find a file that is not in one, and untracked files are usually the newest and least reviewed code in the scope.
- **Omit a bucket `review-scope` reported empty.** On a branch with no commits ahead of its base, the committed line renders as `git diff <sha> <sha>`, which returns nothing. Listing a command that produces nothing invites the reviewer to conclude the scope is smaller than it is. Leave the line out instead.

### Reading the output

`-o` writes the final message to the named file, and with the schema in force that message is the findings object. Check it in this order, and treat any failure as a failed round:

1. **`codex` exited zero.** A non-zero exit is a failed round whatever the file holds.
1. **The `-o` file exists.** A run that failed or was killed never creates it, so a missing file is a failed round, never an empty findings list.
1. **The file is non-empty.** `jq . <file>` exits **0** on an empty file and prints nothing, so jq's exit status is not the emptiness check. Use the file's size, or `jq -e`, which exits 4 on empty input.
1. **It validates against the schema**, and `reviewed` equals the snapshot from step 1.

Never read a missing file, or an empty one, as "no findings".

`--json` additionally streams events on stdout, where the same message arrives as the `item.completed` event whose `item.type` is `agent_message`. Everything else in the stream is the reviewer's own tool use and is not a finding. The stream is useful for watching a long review; it is not a second source of findings.

A run whose output does not parse is a failed round. Do not repair it by hand, and do not fall back to reading its prose as findings. The Claude backend below transcribes prose because it has no schema; here the schema was asked for and did not come back, which means the run did not do what it was told, and its content is unknown.

### Severity

The schema makes the reviewer emit `important` or `nit` directly. If a finding arrives carrying Codex's own priority labels instead, map it:

| Codex                    | Mapped to |
| ------------------------ | --------- |
| P0, P1                   | Important |
| P2 and below, unlabelled | Nit       |

## Claude

Claude Code's `/code-review` reviews a diff locally. Run it **without** `--fix` and without `--comment`: the loop owns every edit, and posting to a pull request is not this skill's business.

This backend behaves differently from Codex in two ways that matter, and both need handling rather than hoping. It does not emit structured output, and its scope is not the scope `review-scope` reports.

### Under Claude Code

Run the review in the session, at the effort `--effort` selected, with the target chosen under Coverage below.

In-session there is no subprocess, so there is no exit status and no output file: the only artifact is the reply, and you are also the one transcribing it. That is the configuration the contract above warns about, so it needs a standing-in signal. **Record the reply verbatim in the round's ledger section before extracting a single finding.** A round with no recorded raw reply is `failed`, whatever you believe you saw. Capturing it first is what makes "the reviewer said nothing" and "the reviewer found nothing" different states rather than the same empty list.

**Record it inside a fenced code block**, never as loose prose. The ledger is handed to `address-review`, which reads unchecked list items and headings as actionable work, so a reply pasted raw can put the reviewer's own sentences into the fixer's queue. That would make reviewer output into instructions, which is the one thing the loop's conventions forbid. A fence keeps it data:

````markdown
Reviewer reply, verbatim:

```text
<the reply, exactly as it came back>
```
````

### Under another harness

```bash
claude -p '/code-review <effort> <target>' --disallowed-tools Edit Write NotebookEdit Bash
```

A `-p` run waits for the review and includes the findings in its response.

`Bash` belongs on that list with the others. Denying `Edit`, `Write` and `NotebookEdit` alone leaves a shell, and a shell writes files perfectly well through a redirection, `git apply`, `sed -i`, or `tee`. The reviewer could then change the tree without the host agent seeing an edit, which breaks the read-only invariant and moves the snapshot underneath the round. Codex gets the same property from `--sandbox read-only`; this is the equivalent, and it is structural rather than a matter of trust.

### Output, and how emptiness is judged

`/code-review` has no schema flag. It reports findings as prose in its reply, or through a findings list in hosts that request one. **You** turn that reply into the findings schema; the reviewer does not, and it does not echo the snapshot either.

That moves where the emptiness test has to happen. For Codex, an unparseable or empty result is caught by the schema. Here, transcribing a reply into an empty findings list is exactly what a genuinely clean review also produces, so the test has to be on the raw reply instead:

- A non-zero exit, or no reply at all, is a **failed round**.
- An empty reply, or one that is only an error, is a **failed round**.
- A reply that reports no findings is a clean round.

Never transcribe an empty or missing reply into `"findings": []`. That is the one move that turns a crashed reviewer into a clean result, and it is the failure the whole skill is built to prevent.

Because the reviewer does not echo the snapshot, `reviewed` is filled in by you. It is not a cross-check for this backend. That is not a hole: the snapshot binding is enforced by step 8 recomputing it, not by the reviewer repeating it back.

### Coverage

`/code-review`'s default scope is the branch's commits **ahead of its upstream**, plus uncommitted changes. That differs from `review-scope`'s scope in two ways, and the first one bites on exactly the branches this skill is for.

- **Upstream, not merge base.** On a branch that has been pushed, the upstream is usually at `HEAD`, so "commits ahead of upstream" is empty and a default run reviews **none of the committed work**. A defect living only in an earlier commit is then outside the review while the run still looks complete. Compare `git rev-parse @{upstream}` with the base from `review-scope`: when they differ, a no-target run cannot claim the committed bucket. Pass `<base>...HEAD` as the target to review that range instead.
- **Untracked files.** Whether the default scope includes them is not documented. Treat them as excluded until a run shows otherwise, which is what step 3's question is for. `git add -N` records an intent to add and puts the file in the diff without staging its content; `git reset -- <paths>` undoes it. The snapshot is content-addressed and does not move either way.

Whether passing a ref-range target keeps the uncommitted changes in scope or replaces them is **not established**. Until it is, do not assume one run covers both. When the upstream differs from the base and there is uncommitted work, either run the committed range and the working tree as two rounds, or report the round as partial scope naming which bucket was left out. Reporting partial scope is always allowed; claiming full scope you did not verify is not.

`/code-review` does not read `REVIEW.md`. It follows `CLAUDE.md` like any session, so repository review rules reach it only through those files.

### Severity

| Claude            | Mapped to |
| ----------------- | --------- |
| Important         | Important |
| Nit, Pre-existing | Nit       |

Pre-existing findings map to Nit rather than being dropped. They are real, and they are not what this branch is answerable for, so they are recorded and left below the default threshold.

### Not a backend

`/code-review ultra` runs a deeper review in the cloud. It is billed, its launch needs an interactive confirmation, and an agent cannot start it. Do not use it as a backend, and do not suggest it as a substitute when another backend is unavailable.

## Choosing between them

The default is the model family the host is not, because a reviewer built on the same model as the author misses what it missed, and the findings worth the round trip are the ones the author's own model would not have reached. `--reviewer` overrides this when the point is a second opinion from the same family, or when only one backend is installed.

## Adding a backend

A new backend needs an availability check, a read-only invocation, its coverage against the four buckets stated plainly, an output path that meets the contract above, and a severity mapping into Important and Nit. Verify each against the tool rather than its documentation, and record what was observed. A backend documented from its README and never run is how a loop comes to trust output nobody has seen.
