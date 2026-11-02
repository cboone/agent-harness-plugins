# Copilot summary and sweep contracts

## Summary examples keep machine data inside details

The example templates keep each status's marker, verdict, full head and read-review
ids, with the table inside details.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

````scrut
$ awk '
> /^### 9\. Post PR Summary Comment$/ {section=1}
> section && /^```markdown$/ {code=1; body=""; next}
> code && /^```$/ {
>   code=0
>   if (body !~ /^<!-- copilot-feedback-summary -->/) next
>   count++
>   split(body, parts, "<details>")
>   if (parts[1] ~ /\| Source/ || parts[2] !~ /Status:/ || parts[2] !~ /Head SHA:/ || parts[2] !~ /Reviews read:/ || body !~ /<\/details>/) exit 1
>   print "summary " count " keeps details"
>   next
> }
> code {body=body $0 "\n"}
> END {if (count != 4) exit 1}
> ' "${REPO_ROOT}/plugins/monitor-pr/skills/resolve-copilot-feedback/SKILL.md"
summary 1 keeps details
summary 2 keeps details
summary 3 keeps details
summary 4 keeps details
````

## A successful sweep reads both inputs

```scrut
$ bash "${COPILOT_SWEEP_CASE_BIN}" "${REPO_ROOT}/plugins/monitor-pr/skills/resolve-copilot-feedback/SKILL.md" ok
sample diff
{"body":"sample PR body"}
sweep inputs read; push eligible
```

## A failed diff blocks continuation

The fixture runs the actual skill block with stubs that refuse unexpected calls.
A read failure must never reach the continuation marker.

```scrut
$ bash "${COPILOT_SWEEP_CASE_BIN}" "${REPO_ROOT}/plugins/monitor-pr/skills/resolve-copilot-feedback/SKILL.md" diff 2>&1
sample git read error
Consistency sweep failed: git diff
[1]
```

## A failed PR body read blocks continuation

```scrut
$ bash "${COPILOT_SWEEP_CASE_BIN}" "${REPO_ROOT}/plugins/monitor-pr/skills/resolve-copilot-feedback/SKILL.md" body 2>&1
sample gh read error
Consistency sweep failed: gh pr view
[1]
```

## The push gate consumes workflow failures and preserves pending siblings

These instruction source canaries assert that the surrounding prose records
read failures and prohibits treating a pending sibling as fixed. The executable
block above proves read errors stop execution.

```scrut
$ skill="${REPO_ROOT}/plugins/monitor-pr/skills/resolve-copilot-feedback/SKILL.md" && grep -F 'Either read failing is a workflow-level failure' "${skill}" > /dev/null && grep -F '**Push gate.** Push only when no workflow-level failure is recorded' "${skill}" > /dev/null && grep -F 'A sibling awaiting a design decision stays unresolved and `Pending`, and is never resolved as fixed.' "${skill}" > /dev/null && echo 'read failures gate push; pending siblings stay open'
read failures gate push; pending siblings stay open
```

## The thread command posts its reply before resolving

````scrut
$ awk '/^### 3\. Reply to and Resolve Threads$/ {section=1; next} section && /^```bash$/ {code=1; next} code && /^```$/ {exit} code {print}' "${REPO_ROOT}/plugins/monitor-pr/skills/resolve-copilot-feedback/SKILL.md"
bash resolve-copilot-threads reply-and-resolve THREAD_ID --reason REASON --body-file TMPFILE
````

## Reply succeeds before resolution

```scrut
$ bash "${COPILOT_REPLY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" ok
true
exit=0; calls=reply,resolve
```

## Reply failure prevents resolution

```scrut
$ bash "${COPILOT_REPLY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" reply 2>&1
Error: Failed to send reply: sample reply failure
exit=1; calls=reply
```

## Resolution failure preserves the successful reply

```scrut
$ bash "${COPILOT_REPLY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" resolve 2>&1
Error: Failed to resolve review thread THREAD: sample resolve failure
exit=1; calls=reply,resolve
```

## Every reason reaches the mutation on both resolution paths

The committed fixture installs its `gh` stub first on PATH. It invokes the helper
only if `command -v gh` resolves to that stub. No live thread is used.

```scrut
$ for reason in ADDRESSED WONT_FIX INVALID; do for operation in resolve reply-and-resolve; do bash "${COPILOT_REPLY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" ok "${operation}" THREAD --reason "${reason}"; done; done
true
exit=0; calls=resolve:ADDRESSED
true
exit=0; calls=reply,resolve:ADDRESSED
true
exit=0; calls=resolve:WONT_FIX
true
exit=0; calls=reply,resolve:WONT_FIX
true
exit=0; calls=resolve:INVALID
true
exit=0; calls=reply,resolve:INVALID
```

## File-based replies preserve the reason

```scrut
$ bash "${COPILOT_REPLY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" ok reply-file --reason INVALID
true
exit=0; calls=reply,resolve:INVALID
```

## Invalid reasons cannot mutate a thread

```scrut
$ for operation in resolve reply-and-resolve; do bash "${COPILOT_REPLY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" ok "${operation}" THREAD --reason Incorrect 2>&1; done
Error: Resolution reason must be ADDRESSED, WONT_FIX or INVALID
exit=1; calls=
Error: Resolution reason must be ADDRESSED, WONT_FIX or INVALID
exit=1; calls=
```

## Missing reasons cannot post a reply

```scrut
$ bash "${COPILOT_REPLY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" ok reply-and-resolve THREAD --reason 2>&1
Error: Resolution reason must be ADDRESSED, WONT_FIX or INVALID
exit=1; calls=
```

## Resolution reasons preserve reply failure handling

```scrut
$ bash "${COPILOT_REPLY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" reply reply-and-resolve THREAD --reason INVALID 2>&1
Error: Failed to send reply: sample reply failure
exit=1; calls=reply
```

## Resolution errors with a reason preserve the reply

```scrut
$ bash "${COPILOT_REPLY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" resolve reply-and-resolve THREAD --reason ADDRESSED 2>&1
Error: Failed to resolve review thread THREAD: sample resolve failure
exit=1; calls=reply,resolve:ADDRESSED
```

## Recovery can retain reason-free resolution for existing callers

```scrut
$ bash "${COPILOT_REPLY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" ok resolve THREAD
true
exit=0; calls=resolve
```

## Reply timing and prior-run recovery have one policy location

This source canary checks the policy headings and known duplicate formulations
across the skill, references and monitor docs. It detects copies and the observed
recurrence wording, not every possible paraphrase; semantic drift still requires
review. Summary data rules about pending commits remain valid outside step 4.

```scrut
$ find "${REPO_ROOT}/plugins/monitor-pr" -type f -name '*.md' -exec awk '
> FNR == 1 {step4=0}
> FILENAME ~ /\/skills\/resolve-copilot-feedback\/SKILL.md$/ && /^### / {step4=($0 == "### 4. Handle Each Category")}
> /\*\*When to reply\.\*\*/ {timing++; if (!step4) bad=1}
> /\*\*Work an earlier run already did\.\*\*/ {recovery++; if (!step4) bad=1}
> !step4 && (/whichever run made it/ || /Unpushed work from an earlier run/ || /Unpushed earlier work triggers/ || /retry only `resolve`/ || /A reply that links.*waits for/) {bad=1}
> END {if (bad || timing != 1 || recovery != 1) exit 1; print "reply policy belongs to step 4"}
> ' {} +
reply policy belongs to step 4
```
