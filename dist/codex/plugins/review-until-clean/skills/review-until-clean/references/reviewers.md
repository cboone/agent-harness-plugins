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
| Shell command | `coderabbit review --agent --fresh`                                   | As a process, from the repository root |

Classify by the first word. When it names a skill or command available in this session, such as `/simplify` or `/pr-review-toolkit:review-pr`, the value is a skill or command. Anything else is a shell command, including one given by absolute path, such as `/opt/homebrew/bin/coderabbit review --agent --fresh`. A leading `/` alone does not decide it. The reviewer's own options go inside the value, and the loop passes them through untouched. One run uses one reviewer. Combining reviewers means running the loop once for each.

**Not a reviewer:** anything that needs a confirmation or a billing approval an agent cannot give. `/code-review ultra`, Claude Code's built-in cloud review, is one: its launch needs an interactive confirmation, and an agent cannot start it. Do not use it, and do not suggest it as a substitute when the requested reviewer is unavailable.

### Availability

Check before the first round, by kind:

- **Skill or command:** it appears in this session's list of available skills or commands. A name that does not resolve is a missing reviewer, not an empty review.
- **Shell command:** `command -v` succeeds on its first word after any leading `NAME=value` assignments, so `LC_ALL=C coderabbit review --agent --fresh` checks `coderabbit`. When the value is too involved to read that way, skip the check and let the run decide: an exit status of 127, the shell's "command not found", is reported as a missing reviewer rather than as a failed review.

A reviewer that is installed but not authenticated usually fails only when it runs. That is a failed round like any other: report that the reviewer is unauthenticated, rather than that it found nothing, and do not attempt to authenticate it.

Do not switch reviewers to rescue a run. The reviewer is chosen in step 2 and recorded in the ledger; changing it mid-run changes what every later round is comparable to. Report the failure and name `--reviewer` as the way to rerun with another.

## The contract

A round's review is acceptable only if both hold:

1. **A finished review is distinguishable from one that did not finish**, by every signal its kind offers. See [Completion signals](#completion-signals).
1. **Its findings end up in the schema `review-scope --schema` prints**, because the reviewer emitted them that way or because you transcribed its reply into it.

They are separate on purpose. Transcription is allowed. Letting the transcription decide whether the review happened is not: a crashed reviewer and a clean reviewer both transcribe to `"findings": []`, so only the raw reply and the process status can tell them apart.

### Completion signals

| Kind          | A finished review                                                                                                   | A failed round                                                                                                  |
| ------------- | ------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Shell command | Exit status 0 **and** non-empty stdout                                                                              | A non-zero exit, a timeout, empty stdout even with stderr, output that is only an error, output that is cut off |
| Skill/command | A report that says the review completed, whether with findings or with none, recorded verbatim before transcription | No report, a report that is only an error, a report that ends partway, a report that says it could not run      |

Every signal, not any one. A process that exits 0 having printed nothing passes an exit-status check on its own, and that is exactly the case this loop must not read as clean. The output that counts is stdout: many CLIs write progress lines to stderr, so a run that exits 0 with only stderr has reported nothing.

A reviewer that emits structured output, such as JSON, adds a signal: the output must parse. Output that was supposed to be structured and does not parse is a failed round. Do not repair it by hand, and do not fall back to reading it as prose; the reviewer did not do what it does, and its content is unknown.

A reviewer that echoes what it reviewed adds another: the echoed value must match the round. Most reviewers do not, and that is not a hole. The snapshot binding is enforced by step 8 recomputing it, not by the reviewer repeating it.

## Running a reviewer

### Skill or command

Invoke it in this session exactly as given, with nothing added to its arguments. Run it over the repository as it is; do not narrow its scope, and do not tell it which findings to look for.

A skill or command runs with this session's own tools, so nothing structural stops it writing. That is allowed: see [Report rounds and edit rounds](#report-rounds-and-edit-rounds). What is not allowed is a reviewer pushing, posting to a pull request, or rewriting history. Do not run a reviewer with an option that does any of those. If its report shows it did, or a check in [Pushes, fetches and rewritten history](#pushes-fetches-and-rewritten-history) catches it, stop the run as `failed`. Those checks apply to both kinds of reviewer, and they catch the common cases only.

### Shell command

Run it from the repository root, in **one** tool call, as a script file under `bash -e -o pipefail`, with stdin closed and both output streams captured to files **outside the working tree**:

```bash
tmp="$(mktemp -d)"
printf 'reviewer_tmp=%s\n' "${tmp}"
cat > "${tmp}/reviewer.sh" << 'REVIEWER_VALUE'
<the --reviewer value, exactly as given>
REVIEWER_VALUE
if bash -e -o pipefail "${tmp}/reviewer.sh" < /dev/null > "${tmp}/stdout" 2> "${tmp}/stderr"; then
  reviewer_status=0
else
  reviewer_status=$?
fi
printf 'reviewer_status=%s\n' "${reviewer_status}"
```

Each part is there for a reason:

- **The value written to a script file through a quoted heredoc.** The value usually contains quotes of its own, such as `jq -s '…'`, so it cannot go inside single quotes: its first `'` would end the string, and the rest would run in the caller's shell, outside every redirect. A heredoc whose delimiter is quoted writes every character literally. It is not inside `$( )`, because macOS's bash 3.2 still parses a heredoc there as shell text, so an apostrophe in a comment or an unbalanced `)` would break it. Pick a delimiter that does not appear as a line of its own in the value.
- **One script, with `pipefail`.** The value may be a pipeline, such as `tool --json | jq -s '…'`. Written out bare, the redirects attach only to its last command: the first one keeps the harness's stdin, its stderr escapes the capture, and the status is the last command's. A reviewer that exits non-zero having printed a finding then comes back as status 0 with `jq`'s empty result, which is a failed review recorded as a clean one. Running the whole value as one script puts every command under the redirects, and `pipefail` makes a failure in any stage the script's status.
- **`-e`.** `pipefail` covers one pipeline at a time, so in `tool | cat; echo done` a later command that succeeds would still set the status to 0. `-e` ends the script at the first command that fails, so that failure is the script's status. It has exceptions, such as a command tested by `if` or joined by `&&` or `||`, so a reviewer value should be the reviewer command itself, optionally piped into its output processing, and not a script that wraps it in further logic.
- **A reviewer that exits 1 to report findings.** Many CLIs, linters among them, exit 0 when clean, 1 when they found something, and higher on error, and the loop reads every non-zero exit as a failed round. Declare the findings code inside the value, as in `ruff check . || test $? -eq 1`: the `||` keeps `-e` from ending the script on the 1, and `test` passes only that code, so a real error still fails the round.
- **The `if` around it.** It records the status even when the caller runs under `set -e`, which would otherwise end the caller before the diagnostics were captured.
- **`reviewer_status`, not `status`.** The surrounding lines run in the caller's shell, which is often zsh, and zsh reserves `status` as a read-only alias for `$?`. Assigning it fails with `read-only variable: status` whatever the reviewer returned, so the exit status is lost.
- **The directory first, the status last.** An agent's shell does not keep variables from one tool call to the next, and the run itself prints nothing, since both streams go to files. The first line names the directory before the reviewer starts, so its output can still be found if the call is cut off; the last line gives the status. Read both from the output, and record the status before anything else runs; never run the reviewer again to recover them, since that is a silent retry and repeats an editing reviewer's edits.
- **A timeout to match the reviewer.** A full review can take many minutes, longer than an agent shell tool's default timeout, which is two minutes in Claude Code. Give the call the longest timeout the tool allows, or run it in the background and wait for it to finish. A call cut off by the tool's timeout is a failed round: record what the directory holds and stop, rather than running the reviewer again.
- **`< /dev/null`.** Many CLIs read stdin when it is not a terminal. An agent harness's stdin is a pipe that never reaches end of file, so without the redirect such a CLI waits forever and the round produces nothing at all.
- **Files outside the working tree.** The snapshot covers every non-ignored path in the tree, so an output file written into the repository is itself a change. It would move the snapshot, turn every round into an edit round, and hand the next round the reviewer's own output as new code. `./ledger.md` gives the same rule for the ledger.
- **The exit status, kept.** It is one of the two completion signals, so record it, from the printed line, before anything else runs.

Remove the temporary directory when the round ends, including when it fails, and only after both streams are in the ledger in full, or saved beside it as [Recording the raw reply](#recording-the-raw-reply) allows.

## Pushes, fetches and rewritten history

**The loop relies on the reviewer not pushing, fetching or rewriting history, and cannot fully detect it.** A reviewer runs with this session's own tools or as an arbitrary command, so it can reach anything the session can. Choosing a reviewer is trusting it not to do those things. Two checks catch the common cases, and a clean report never claims more than they show:

- **Remote refs.** Record every remote-tracking ref and tag before the reviewer runs, and compare them as it returns:

  ```bash
  git for-each-ref --format='%(refname) %(objectname)' refs/remotes refs/tags
  ```

  A plain `git push` or `git fetch` updates a remote-tracking ref, including from a branch with no upstream yet under `push.autoSetupRemote`. It misses a push of a tag that already existed locally, a push to a URL or to a remote with no fetch refspec, and any write through an API, such as `gh`.

- **Ancestry.** When `HEAD` moved, check `git merge-base --is-ancestor <step 1 head> <new head>`. A new commit passes it. An amend, a reset or a rebase fails it, and is a rewrite, not an edit round.

A moved ref or a failed ancestry check ends the run as `failed`, naming the refs or commits involved. The ref check cannot tell who moved a ref: an editor's background fetch or another session moves it just the same, so say that the cause is unknown rather than that the reviewer fetched. Posting to a pull request leaves no local trace at all, so for that the reviewer's report is the only evidence.

## Report rounds and edit rounds

A reviewer either **reports** findings or **edits** the code itself, as `/simplify` and fix modes do. The loop does not ask which; it observes it.

Compare the snapshot from step 1 with `review-scope`'s snapshot taken **immediately after the reviewer returns**, before transcribing anything:

- **Unchanged:** a report round. The reviewer's findings go through steps 6 to 9 as usual.
- **Moved:** an edit round. Whatever moved it happened while the reviewer ran, so it is that round's result. Record the paths that changed. Any findings the reviewer also reported are recorded but never queued for the fixer, since they name lines in code its edits replaced. An edit round is never clean, whatever it reported, because the code it reviewed is no longer the code on disk; the next round reviews the new snapshot.

The snapshot binds `HEAD`, the resolved merge base, and the working tree's content as Git would store it. A reviewer that commits moves it even when no file content changed; record such a round's `HEAD` or base change in place of the changed paths, which can then be empty. A `HEAD` that moved to a commit not descended from the old one is a rewrite, not an edit round, per the ancestry check above. Within the tree, it sees lasting changes to stored content and nothing else. An unchanged snapshot does not prove the reviewer wrote nothing: staging or unstaging a path that is already tracked, a write to an ignored untracked file, an edit reverted before the reviewer returned, and an edit Git normalizes away, such as a line-ending change under text normalization, all leave it where it was. Such a round is recorded as a report round. The index does count in one case: it decides which paths are tracked, so force-adding an ignored file with `git add -f`, or removing a tracked ignored file from the index, moves the snapshot without changing any file's bytes, and that round is an edit round. None of them changes the content the snapshot binds a clean result to, which is why the mode is decided from it; say what the snapshot covers rather than that nothing was written.

A change made by something other than the reviewer during its run, such as a formatter on save or another session, is indistinguishable from the reviewer's own edit. It is recorded the same way, which costs at most one more round and never a wrong clean result.

The changed paths come from the content trees the two scope reads report: `git diff-tree -r -z --name-only <tree before> <tree after>` lists exactly the paths whose stored content changed, added or deleted. Do not derive them from the file lists. Those lists sort paths into buckets, and staging, unstaging or `git add -N` moves a path between them, or off them, without changing a byte, so a path that only left a list is not an edit. Record a `HEAD` or base change separately, as above. List the paths in the ledger; do not summarize them as "the reviewer made changes".

Under `--report-only`, an edit round is reported with its changed paths, and nothing is reverted. Reverting would be the loop editing code under `--report-only`, and a guess about which edits were the reviewer's.

## Coverage

The reviewer decides what it reads. The loop cannot make it read all four buckets, so it prepares the scope before the round and verifies coverage after it.

### Before the round: untracked files

Many reviewers read only `git diff`, and an untracked file is in no diff, though untracked files are usually the newest and least reviewed code in the scope. When the scope has untracked files, ask once per run whether to make them visible with `git add -N`, which records an intent to add without staging content. Use the structured-question capability where the harness has one, and a numbered list with a wait for the reply where it does not. Restore the index with `git reset -- <paths>` when the round ends, touching only those paths, including when the round fails. When no one can answer, as in a non-interactive run, do not touch the index: record the untracked bucket as not covered and go on.

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
- **Never hand a reviewer a symlink as a file to open**, and never resolve the target and pass that path either; the resolved path is the same content by another name. A reply that quotes a symlink's target contents is redacted before any of it is saved, in the raw reply and in every finding alike; see [Recording the raw reply](#recording-the-raw-reply).
- **A symlink is in the scope, and its target is not.** A round whose untracked bucket holds symlinks is still full coverage. The snapshot agrees: git records a symlink as its target string.

The rule does not depend on where the target points. A target inside the repository is already in the scope on its own merits, so following the link would only show the reviewer the same bytes twice.

## Recording the raw reply

**Record the reviewer's reply verbatim in the round's ledger section before extracting a single finding.** For a shell command, that is its exit status, its stdout and its stderr, each in full and each in its own fence, since the decisive error is often the last line a CLI prints; for a skill or command, the report it produced. A round with no recorded raw reply is `failed`, whatever you believe you saw.

**One exception to verbatim: redact a symlink target's contents first.** If the reply, or either output stream, quotes the contents of a file an untracked symlink points to, replace that text with `[redacted: contents of the target of <symlink path>]` before anything is written, to the ledger or beside it, and say in the round's section that a redaction was made. The rule above keeps those contents out of the review; a verbatim record would put them back into the ledger and every commit made from it. Redact only that text, and record the rest exactly as it came back. Capturing it first is what keeps "the reviewer said nothing" and "the reviewer found nothing" different states.

**Record it inside a fenced code block**, never as loose prose. The ledger is handed to `address-review`, which reads unchecked list items and headings as actionable work, so a reply pasted raw can put the reviewer's own sentences into the fixer's queue.

**Size the fence to the reply.** A review of code routinely contains code blocks, so a fixed three-backtick fence can be closed early by the reply's own. Count the longest run of consecutive backticks anywhere in the reply and open with at least one more than that, never fewer than three. CommonMark closes a fence only on a run at least as long as the one that opened it, so a fence longer than anything inside it cannot be closed from within. For a reply whose longest run is a three-backtick code block, the ledger's fence takes four:

`````markdown
Reviewer reply, verbatim:

````text
F1 src/session.ts:142: token refresh races with logout.

```ts
await refresh(token);
```
````
`````

A very long reply or stderr may be stored in full beside the ledger, outside the working tree, with its file name and its first and last lines in the ledger instead. The same fence rule applies to the excerpt. Such a file travels with the ledger: step 11 moves it too, and the ledger names it by a path relative to itself.

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
