# Ordered Assertions

An absence has to be told apart from an instrument that was not running, and the order of the assertions is what tells them apart.

## The order

Always these three, in this order:

1. **The instrument was running.** In the strongest form, something built to fail did fail. Where the subject cannot be weakened into failing, the fallback is a marker proving the instrument produced output at all. Without one or the other, everything below passes vacuously.
1. **The subject ran to completion, its output parses, and its progress counter moved.** A clean result now describes work that actually happened.
1. **The absence.** No race, no leak, no match, nothing left behind.

Everything the subject proves is an absence, and a search for absence succeeds for the wrong reason when the instrument was never running. An unlinked runtime, an uninstrumented access, a thread the sanitizer never saw, a job that built the wrong module: each makes every arm silent, and only step 1 tells that apart from a correct subject.

The two forms of step 1 are not equally strong, and the gap between them is where the plant table earns its place. A failing arm proves the instrument can see **the one defect the arm plants**, on the inputs that arm supplies. A proof-of-output marker proves only that the instrument ran. Neither proves visibility for a class, which is the same caution the blindness matrix raises about variants of one defect, and it is why a campaign plants several spellings rather than one. The two worked examples below are one form each, and the second says explicitly what it therefore cannot establish on its own.

## Worked example: a two-arm sanitizer judge

A script that runs both arms of a race harness under a thread sanitizer and judges them in order. It is parameterized, so one script serves every harness in the project:

```text
race-check <path/to/harness> <clean-arm> <weakened-arm> <progress-field>

  race-check zig-out/bin/fosforo-ring-race ring weakened validated
  race-check zig-out/bin/fosforo-gate-race gate gate-weakened contended
```

The progress field is an argument precisely because the evidence that two threads met differs per harness: one counts windows its reader validated, the other counts rounds in which the closer actually spun.

The two functions are called in a fixed order, and the control is judged before the subject's result is read at all:

```bash
check_control "${binary}" "${weakened_arm}" "${capture}"
check_subject "${binary}" "${clean_arm}" "${progress_field}" "${capture}"
```

`check_control` gates on two things, and its diagnostics are the useful part:

```text
the <arm> arm did not finish (exit N), so there is nothing to compare against
Thread Sanitizer reported nothing against an arm built to race, so it is not detecting anything here
every check below would pass vacuously; this run's clean result means nothing
```

**The exit status in that first message is context, not the test.** It has to be, because a flagged control arm exits non-zero by design, so reading the status as the completion signal would reject every correct run. Completion is judged by a marker line the harness prints when it finishes, and the status is interpolated into the message only to save the reader a second lookup. Any judge over an instrument that signals through its exit code needs the same separation: decide on the output, report the status alongside it.

`check_subject` gates on three, in order: the arm completed, the progress counter moved, then the absence.

```text
the <arm> arm reported <field>=<absent>, so the two threads never met
a clean sanitizer result over that is vacuous
```

Two details worth copying:

- **The exit status of each arm is recorded and not obeyed.** A flagged arm exits non-zero by design and a clean one exits zero for a reason the script has not checked yet. Read the status and the output as separate facts.
- **The sanitizer's own settings are set explicitly** rather than relied on, because the assertions depend on them: errors do not halt the run, so the weakened arm completes and prints its own result line.

### The control that paid for itself before the check ever passed

Asking a build system for thread-sanitizer instrumentation produced a binary that linked the sanitizer runtime and emitted none of its instrumentation, because the compiler's default backend for that target silently omits the pass. Nothing warns. The binary is the right size, it builds, links, runs, exits zero, and reports no races whatever runs inside it.

Without a control arm, the clean arm would have come back clean and the job would have gone green while measuring nothing at all. This is the single strongest argument for the two-arm structure, and it arrived before the check had ever passed once.

The general rule: **anything that acquires a sanitizer needs the same kind of control**, and the way to establish it is to disassemble or otherwise inspect both builds rather than to infer from the flags you passed.

## Worked example: an external report

A leak checker exits non-zero whenever it finds anything at all, and it always finds something, because the platform's own frameworks leak a few hundred allocations per run and none of them belong to the project. So the exit code is not the signal, and neither is a clean grep on its own. Four assertions, in order:

1. **The harness itself passed.** A leak report over a run that fell over partway through describes a process that never reached the teardown being measured.
1. **The checker produced a report and it parses.** A grep that finds nothing in output that was never generated reads exactly like a pass.
1. **No leaked object belongs to this project**, by class-name prefix.
1. **The total leaked bytes are inside the bound.**

The class filter comes before the byte bound deliberately, because it can say **what** leaked. "These objects belong to this project, here they are" is a strictly better first thing to read than "some number of bytes went missing", so the bound is the catch-all for what the filter cannot name.

**Notice how this example departs from the three-step order, because the difference is the useful part.** There is no deliberately failing arm here. You cannot weaken a leak checker into reporting a leak that is not there, so the positive control of the two-arm kind is unavailable, and assertion 2 stands in for it: a report that exists and parses proves the instrument ran and produced output, which is the most this script can establish from inside itself. Note that the assertion is parseability rather than a nonzero total. A clean report legitimately carries zero, so requiring nonzero would fail a correct run on a platform that happens not to leak anything of its own.

That is weaker than a control arm, and it is weaker in a specific way worth naming: it proves the instrument ran, not that the instrument can see the defect you care about. Only a planted leak proves the second, and it has to be run **outside** the script, by hand, as a row in the plant table. So the two halves divide like this:

| Establishes                            | Where it lives                                     |
| -------------------------------------- | -------------------------------------------------- |
| The instrument ran and produced output | Assertion 2, on every run, forever                 |
| The instrument can see this defect     | A planted leak, run by hand, recorded in the table |

The general rule, then, is not "always start with a failing arm". It is **start with whatever proves the instrument was running, and use the strongest form available to you**: a deliberately failing arm where the subject can be weakened, a proof-of-output marker where it cannot. Where you settle for the weaker form, the plant table is what carries the claim the script cannot.

Two implementation details that are really assertions:

- **Extract the summary figure with a stream editor rather than a grep.** Under `errexit`, a grep that matches nothing takes the script down where the number is read rather than where it is judged, which reads as a crash instead of a diagnosis. And `grep ... || true` hands back an empty string, which the shell reads as zero in an arithmetic context, and zero passes.
- **Anchor the pattern so two matches fail as well as none.** One line per match, one trailing newline stripped, no multiline flag: a two-line result fails the test the same way an empty one does. Three failure modes, one assertion, and no way to satisfy it vacuously.

## Distinct exit codes for "nothing was measured"

Give "the instrument did not run" its own exit code, separate from "the thing is broken".

```text
0  - the harness passed and leaked nothing this project owns
64 - invalid arguments
65 - something leaked
66 - the harness binary does not exist or is not executable
69 - the harness failed or the report did not parse, so nothing was measured
```

The last two are separate for a reason that arrives with CI. Under `continue-on-error`, nobody opens the log of a step that cannot block a merge, so the exit code is the whole message. Returning one code for both conclusions puts back together the two things the assertion order exists to keep apart.

## A control that models the defect is not the subject exhibiting it

Plant in the real code as well as in the replica.

A negative control arm is usually a copy of the access pattern with one thing relaxed, which is convenient and is not the subject. So run the plant against the real primitive too. On the project this comes from, doing that found a genuine gap in the harness itself: the reader consulted a helper before every read, and that helper was itself an acquiring load, so per-iteration it ordered the writer's stores against the copies that followed. It detected a weakened publishing store and would have reported a weakened acquiring load as clean. Half the protocol was uncovered by a line that read as an optimization.

## The instrument's own cost can make the control unfaithful

The subtlest finding in the whole program, and one nobody predicted.

A control arm failed with its progress counter at zero: the closer had not spun in a single one of its 256 rounds, against 195 for the clean arm on the same commit. The reason is that how long a thread takes to leave a gate is itself a function of the ordering under test. A sanitizer instruments a releasing store as a full publish of the accessing thread's vector clock and a relaxed store as very much less, so the weakened arm's holder reached the exit and was gone before the closer arrived. The control had quietly stopped modelling the only situation either arm exists to model.

The repair is to hold the assertion rather than to relax it, because the assertion was right. The general form: **a control that models a defect can be made unfaithful by the instrument's own cost, and the counter that proves the two parties met is the only thing that would say so.**

## Plant the checker itself

The judging script is code, and its assertions are claims. Verify them the same way.

The meta-plant for a two-arm judge is to remove the race from the weakened arm and confirm the script fails **at assertion one** rather than passing. For the report reader, truncate the report and confirm it exits with the "nothing was measured" code rather than the "something leaked" one.

## Portable shapes

- **Any external instrument**: assert a parseable report exists before searching it for absence. Prefer a marker line the tool always prints when it ran.
- **Any absence claim in a unit suite**: add one assertion in the opposite direction, so a degenerate implementation fails. See `./references/vacuous-passes.md`.
- **Any two-arm judge**: parameterize the harness path, both arm names, and the progress field, so one script serves every harness and the order of assertions is written once.
- **Any counter-based overlap check**: assert it from outside the process as well as inside it. A harness that reports its own overlap is reporting on itself.
