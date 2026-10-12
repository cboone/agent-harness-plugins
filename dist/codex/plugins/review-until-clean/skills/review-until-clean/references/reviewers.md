<!-- `/simplify` is Claude Code's built-in command, named here as an example reviewer, not a plugin in this marketplace. -->
<!-- validate-plugins: ignore /simplify -->

# Reviewers

How the loop runs a reviewer it knows nothing about, how it tells a finished review from one that did not finish, and how it turns what came back into findings.

The loop has no adapter for any reviewer. Everything here applies to every reviewer alike. A rule that would only make sense for one named tool belongs in that tool's own skill, not here.

## What a reviewer is

`--reviewer` takes exactly what a person would type, in one of two kinds:

| Kind          | Examples                                                              | How it runs                            |
| ------------- | --------------------------------------------------------------------- | -------------------------------------- |
| Skill/command | `/pr-review-toolkit:review-pr`, `/review-pr-with-codex --effort high` | In this session, as a skill or command |
| Shell command | `coderabbit review --plain`                                           | As a process, from the repository root |

A value that starts with `/` is a skill or command; anything else is a shell command. The reviewer's own options go inside the value, and the loop passes them through untouched. One run uses one reviewer. Combining reviewers means running the loop once for each.

**Not a reviewer:** anything that needs a confirmation or a billing approval an agent cannot give. `/code-review ultra`, Claude Code's built-in cloud review, is one: its launch needs an interactive confirmation, and an agent cannot start it. Do not use it, and do not suggest it as a substitute when the requested reviewer is unavailable.

### Availability

Check before the first round, by kind:

- **Skill or command:** it appears in this session's list of available skills or commands. A name that does not resolve is a missing reviewer, not an empty review.
- **Shell command:** `command -v <first word>` succeeds.

A reviewer that is installed but not authenticated usually fails only when it runs. That is a failed round like any other: report that the reviewer is unauthenticated, rather than that it found nothing, and do not attempt to authenticate it.

Do not switch reviewers to rescue a run. The reviewer is chosen in step 2 and recorded in the ledger; changing it mid-run changes what every later round is comparable to. Report the failure and name `--reviewer` as the way to rerun with another.

## The contract

A round's review is acceptable only if both hold:

1. **A finished review is distinguishable from one that did not finish**, by every signal its kind offers. See [Completion signals](#completion-signals).
1. **Its findings end up in the schema `review-scope --schema` prints**, because the reviewer emitted them that way or because you transcribed its reply into it.

They are separate on purpose. Transcription is allowed. Letting the transcription decide whether the review happened is not: a crashed reviewer and a clean reviewer both transcribe to `"findings": []`, so only the raw reply and the process status can tell them apart.

### Completion signals

| Kind          | A finished review                                                                                                   | A failed round                                                                                             |
| ------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Shell command | Exit status 0 **and** non-empty output                                                                              | A non-zero exit, a timeout, no output, output that is only an error, output that is cut off                |
| Skill/command | A report that says the review completed, whether with findings or with none, recorded verbatim before transcription | No report, a report that is only an error, a report that ends partway, a report that says it could not run |

Every signal, not any one. A process that exits 0 having printed nothing passes an exit-status check on its own, and that is exactly the case this loop must not read as clean.

A reviewer that emits structured output, such as JSON, adds a signal: the output must parse. Output that was supposed to be structured and does not parse is a failed round. Do not repair it by hand, and do not fall back to reading it as prose; the reviewer did not do what it does, and its content is unknown.

A reviewer that echoes what it reviewed adds another: the echoed value must match the round. Most reviewers do not, and that is not a hole. The snapshot binding is enforced by step 8 recomputing it, not by the reviewer repeating it.

## Running a reviewer

### Skill or command

Invoke it in this session exactly as given, with nothing added to its arguments. Run it over the repository as it is; do not narrow its scope, and do not tell it which findings to look for.

A skill or command runs with this session's own tools, so nothing structural stops it writing. That is allowed: see [Report rounds and edit rounds](#report-rounds-and-edit-rounds). What is not allowed is a reviewer pushing, posting to a pull request, or rewriting history. Do not run a reviewer with an option that does any of those, and if its report shows it did, stop the run as `failed` and say what it did.

### Shell command

Run it from the repository root, with stdin closed and both output streams captured to files **outside the working tree**:

```bash
tmp="$(mktemp -d)"
<reviewer command> < /dev/null > "${tmp}/stdout" 2> "${tmp}/stderr"
status=$?
```

Each part is there for a reason:

- **`< /dev/null`.** Many CLIs read stdin when it is not a terminal. An agent harness's stdin is a pipe that never reaches end of file, so without the redirect such a CLI waits forever and the round produces nothing at all.
- **Files outside the working tree.** The snapshot covers every non-ignored path in the tree, so an output file written into the repository is itself a change. It would move the snapshot, turn every round into an edit round, and hand the next round the reviewer's own output as new code. `./ledger.md` gives the same rule for the ledger.
- **The exit status, kept.** It is one of the two completion signals, so record it before anything else runs.

Remove the temporary directory when the round ends, including when it fails, after its content is in the ledger.

## Report rounds and edit rounds

A reviewer either **reports** findings or **edits** the code itself, as `/simplify` and fix modes do. The loop does not ask which; it observes it.

Compare the snapshot from step 1 with `review-scope`'s snapshot taken **immediately after the reviewer returns**, before transcribing anything:

- **Unchanged:** a report round. The reviewer's findings go through steps 6 to 9 as usual.
- **Moved:** an edit round. Whatever moved it happened while the reviewer ran, so it is that round's result. Record the paths that changed, and any findings the reviewer also reported. An edit round is never clean, whatever it reported, because the code it reviewed is no longer the code on disk; the next round reviews the new snapshot.

A change made by something other than the reviewer during its run, such as a formatter on save or another session, is indistinguishable from the reviewer's own edit. It is recorded the same way, which costs at most one more round and never a wrong clean result.

The changed paths come from comparing the two scope reads: every path in either read's file lists whose content differs, plus any path that appears in only one of them. List them in the ledger; do not summarize them as "the reviewer made changes".

Under `--report-only`, an edit round is reported with its changed paths, and nothing is reverted. Reverting would be the loop editing code under `--report-only`, and a guess about which edits were the reviewer's.

## Coverage

The reviewer decides what it reads. The loop cannot make it read all four buckets, so it prepares the scope before the round and verifies coverage after it.

### Before the round: untracked files

Many reviewers read only `git diff`, and an untracked file is in no diff, though untracked files are usually the newest and least reviewed code in the scope. When the scope has untracked files, ask once per run whether to make them visible with `git add -N`, which records an intent to add without staging content. Use the structured-question capability where the harness has one, and a numbered list with a wait for the reply where it does not. Restore the index with `git reset -- <paths>` when the round ends, touching only those paths, including when the round fails.

The snapshot is content-addressed and does not move either way. Declining is a valid choice; the untracked bucket is then recorded as not covered, unless the reviewer's report shows it read those files anyway.

### After the round: what the reviewer says it read

Compare what the reviewer reports it reviewed against the four buckets from step 1, and record the round's coverage as one of:

| Coverage     | When                                                                                                |
| ------------ | --------------------------------------------------------------------------------------------------- |
| `full`       | The report names its range or files, and they include every non-empty bucket                        |
| `partial`    | The report shows a bucket was left out, such as a range that starts after the base. Name the bucket |
| `unverified` | The report does not say what it read                                                                |

Judge from what the reviewer reported, not from what it is documented to do. A reviewer's default range is often the branch's upstream rather than its merge base, and on a pushed branch that leaves every committed change out while the run still looks complete.

A clean round with `partial` coverage reports `clean, partial scope`, and one with `unverified` coverage reports `clean, coverage unverified`. Neither is ever plain `clean`.

Do not split a round to reach full coverage. Running the reviewer once over one bucket, fixing, and then running it over another means no round ever saw the whole scope, and the eventual clean result is not what it claims. Reporting partial or unverified coverage is always allowed.

## An untracked symlink is not an untracked file

`git ls-files --others --exclude-standard` lists an untracked symlink exactly like an untracked regular file. A reviewer told to read that path reads the target instead of the link, and the target is chosen by whoever created the link. A link to `~/.ssh/id_ed25519` or to another checkout puts that content into the reviewer's context, from where it reaches the findings, the ledger, and any commit made from them.

So find the untracked symlinks before the round:

```bash
while IFS= read -r -d '' path; do
  if [[ -L "${path}" ]]; then
    printf 'symlink %s -> %s\n' "${path}" "$(readlink "${path}")"
  fi
done < <(git ls-files -z --others --exclude-standard)
```

Then:

- **A symlink is in scope only as its link text.** A wrong or dangling target is reviewable, and that is all there is to review in a link. `git add -N` satisfies this on its own: git diffs a symlink as its target string, so the link text reaches the review and the target's contents do not.
- **Never hand a reviewer a symlink as a file to open**, and never resolve the target and pass that path either; the resolved path is the same content by another name. A finding whose evidence quotes a symlink's target contents is recorded with that evidence withheld.
- **A symlink is in the scope, and its target is not.** A round whose untracked bucket holds symlinks is still full coverage. The snapshot agrees: git records a symlink as its target string.

The rule does not depend on where the target points. A target inside the repository is already in the scope on its own merits, so following the link would only show the reviewer the same bytes twice.

## Recording the raw reply

**Record the reviewer's reply verbatim in the round's ledger section before extracting a single finding.** For a shell command, that is its stdout, with its exit status and the first lines of stderr; for a skill or command, the report it produced. A round with no recorded raw reply is `failed`, whatever you believe you saw. Capturing it first is what keeps "the reviewer said nothing" and "the reviewer found nothing" different states.

**Record it inside a fenced code block**, never as loose prose. The ledger is handed to `address-review`, which reads unchecked list items and headings as actionable work, so a reply pasted raw can put the reviewer's own sentences into the fixer's queue.

**Size the fence to the reply.** A review of code routinely contains code blocks, so a fixed three-backtick fence can be closed early by the reply's own. Count the longest run of consecutive backticks anywhere in the reply and open with at least one more than that, never fewer than three. CommonMark closes a fence only on a run at least as long as the one that opened it, so a fence longer than anything inside it cannot be closed from within. With the reply's own fence at three and the ledger's at four:

````markdown
Reviewer reply, verbatim:

```text
<the reply, exactly as it came back>
```
````

A very long reply may be stored in full beside the ledger, outside the working tree, with its path and its first and last lines in the ledger instead. The same fence rule applies to the excerpt.

## Transcribing findings

Turn each finding in the reply into one entry of the `review-scope --schema` shape: `file`, `line`, `severity`, `title`, `detail`, `evidence`. Transcribe what the reviewer said; do not add findings it did not raise, and do not drop ones you disagree with. Disagreement is a decline, recorded with a reason under step 7.

A finding with no location, such as a remark about the design as a whole, is recorded in the round with a `file` of the most relevant path in scope when the reply names one, and otherwise as a note in the round's section rather than an unchecked item.

### Severity

The repository's own two levels are Important and Nit. Map the reviewer's labels into them, whatever words it uses:

| Reviewer label                                                               | Mapped to |
| ---------------------------------------------------------------------------- | --------- |
| Critical, blocker, high, major, important, error, P0, P1, "must fix"         | Important |
| Medium, minor, low, nit, suggestion, style, info, P2 and below, pre-existing | Nit       |
| No label                                                                     | Important |

**An unlabelled finding is Important.** A reviewer that does not grade its findings is still saying each one is a defect, and mapping them to Nit would let a reviewer with no severities never block a clean result at the default threshold.

A label that fits neither row is mapped by meaning, and the original label is kept in the finding's `detail` so the mapping can be checked. Do not introduce a third level.

Pre-existing findings map to Nit rather than being dropped. They are real, and they are not what this branch is answerable for.
