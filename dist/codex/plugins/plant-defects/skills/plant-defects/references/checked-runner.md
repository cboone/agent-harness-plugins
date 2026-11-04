# Checked plant runner

Use the bundled runner for every plant claim. Commit the check and plant inputs
before running. Do not write a separate harness, success ledger section or status
line. The runner executes trusted local scripts in private copies; this is input
isolation, not a sandbox. Scripts must use relative paths to the copied subject,
never write to the live checkout, and never call live services.

## Manifest

Place a JSON manifest at the root of the input tree. List every source file,
fixture, setup/check script, patch and configuration it reads in `inputs`, using
normalized relative file paths. Include supporting files explicitly; directory
and glob entries are unsupported. All external file reads use one nonblocking regular-file reader, including the
manifest, result JSON and existing record destinations. Manifest parsing and its
fingerprint use the same bytes. The runner verifies inputs are regular files before reading; FIFOs and other unsupported kinds fail with
null fingerprints and a preserved cause. Require real paths within the manifest directory: symlinked inputs and symlinked
relative path components are refused with null fingerprints. Create any links
needed by a check in its setup script, using declared regular target files.
Dependencies and command-line tools must already be available. Secrets stay in
environment variables and must not be printed by scripts: captured output becomes
part of the result file.

```json
{
  "inputs": ["src/subject.py", "tests/check.sh", "tests/setup.sh", "plants/example.patch", "plants/ignored-control.patch"],
  "setup": "tests/setup.sh",
  "check": "tests/check.sh",
  "timeout": 60,
  "green": {"exit_code": 0, "contains": ["Ran 1 test", "\nOK\n"], "excludes": ["skipped", "SKIP", "ERROR:"]},
  "variants": [
    {
      "name": "required-boundary",
      "patch": "plants/example.patch",
      "red": {
        "exit_code": 1,
        "contains": ["FAIL: test_required_boundary", "Ran 1 test", "FAILED (failures=1)"],
        "excludes": ["ERROR:", "skipped", "SyntaxError", "ImportError"]
      }
    }
  ],
  "controls": [
    {"name": "ignored-fixture", "patch": "plants/ignored-control.patch"}
  ]
}
```

Assertion variants go in `variants` and must reach their declared red assertion.
Negative controls that must stay green go in the separate `controls` list; each
has a unique name and patch and must satisfy the manifest's `green` expectation
after applying it. A control that goes red, skips, fails setup or never runs
fails publication. Its outcome is `control-green`, never a red plant. Either list
may be omitted; at least one declaration is required. Names are unique across both
lists. The runner executes assertion variants first, then green controls.

`setup` is optional. It must return zero, including compilation and other
prerequisites that must succeed before the check can assert the named property.
The runner invokes each script with `bash -euo pipefail` from the private input
root. Setup runs before baseline, red and restored checks. Give the check a
literal progress marker and a specific assertion marker, with exact exit codes
and exclusions for framework errors or skips. A nonzero exit alone cannot prove
that the intended assertion ran. Match an exact green success marker, including
its line boundary, and explicitly exclude the framework's skip and error output
in both green and red expectations. For unittest, `OK (skipped=1)` is not green
evidence: require `\nOK\n` and exclude `skipped`, `SKIP` and `ERROR:`. Move compilation and dependency setup out of
the assertion command. Shell constructs that deliberately mask failure remain
the script author's responsibility.

Input fingerprints include SHA-256 content digests and permission modes. Private
and restored copies preserve those modes so supporting executables run.
Mode changes after a run invalidate publication just as content changes do.

Patches use Git's `a/` and `b/` paths relative to this root. Patch commands use a
separate private Git context with inherited Git overrides and configuration
removed; ancestor checkouts cannot silently skip private paths, even when
`TMPDIR` is inside a repository. The runner validates
and applies each patch from its own private path. Keep patches focused on the
subject or judge being tested. Each variant starts with pristine input copies,
checks baseline green, applies its patch, checks red, reconstructs its private
input tree and checks restored green. Python subprocesses receive a fresh
`PYTHONPYCACHEPREFIX` and `PYTHONDONTWRITEBYTECODE=1` for every step. Do not override
them or reuse long-lived Python workers.

## Run and generate records

Resolve `checked-plant` from this skill's installed plugin, using
`${CLAUDE_PLUGIN_ROOT}/scripts/checked-plant` in Claude. In Codex, use the helper
shipped beside the selected skill's plugin, or the generated skill's relative
helper path. Resolve `../../scripts/checked-plant` from the real directory
containing the selected `SKILL.md`. Do not choose another installation by a
version-blind glob.

The runner requires Python 3.13 or newer for POSIX `waitid` and `WNOWAIT`
on macOS. Its inline metadata lets `uv run --script` select a compatible
interpreter even in a repository whose `.python-version` pins 3.11 or 3.12.
Unsupported runtimes still fail closed before spawning commands.

Run through `uv run --script`, with a new output directory for every attempt:

```bash
uv run --script /absolute/plugin/scripts/checked-plant run plants.json plant-run
uv run --script /absolute/plugin/scripts/checked-plant render plant-run/results.json \
  --ledger ledger.md --status plant-status.md
```

Check each command's exit status. Rendering refuses incomplete, failed, unrun or
stale evidence before touching either record. Failed runs exit 1 and retain the
cause in `results.json`; later variants remain `unrun`, which also fails the run.
The runner preserves the initial failure when restoration fails too. It never
reuses an output directory. Missing inputs produce failed evidence, with null
fingerprints for unreadable files. A missing or malformed manifest cannot supply
variant names, so the top-level reason reports that failure.

A selector drains nonblocking step transports into runner-owned regular files
until EOF or an explicit deadline. Each file receives at most 1 MiB; overflow
sets `output_truncated`, stops the owned process group and fails the step. On
timeout or overflow, transports close without waiting for escaped descendants.
Parent waits and final file reads are bounded, so neither inherited descriptors
nor continuous output can prevent failure publication. Results record timeout, termination and
reaping state as well as the exit code. Timed-out, unreaped or truncated steps
never count as assertion evidence. A timeout stops the step's process group;
checks must clean up descendants that deliberately create separate sessions.
Normally exiting steps also stop their remaining process group with bounded TERM
then KILL before restoration. The leader stays unreaped until group verification
finishes; results retain any remaining live PIDs or cleanup error and refuse
publication. The runtime must provide POSIX `waitid` and `WNOWAIT`; unsupported
runtimes fail before spawning. Ledger and status
destinations must differ and cannot alias inputs or evidence, including hard links and names that the filesystem treats as the same file.
The renderer opens both outputs without truncation, checks their filesystem
identities, and writes through those checked handles. Refusal removes only new reservations.

The JSON result includes schema version, absolute manifest path, completion
and success flags, SHA-256 fingerprints of the manifest, runner and all declared
inputs, and one row per declared assertion variant or green control. Rows contain outcome, cause,
restoration flags, exact setup/check exits, stdout and stderr. The renderer checks the
manifest's ordered variant list, all setup/check evidence and current fingerprints,
independently of the aggregate success flag. It replaces only the marked ledger
section and writes the status text from those same rows. Preserve the JSON with
the ledger; use its generated status verbatim when reporting plant outcomes.
JSON is local evidence, not a signature against intentional edits.

## Restart check

Commit a regression that supplies a deliberately inapplicable patch. Assert its
row is `setup-error`, later rows are `unrun`, the run fails, and rendering refuses
without changing ledger or status. Then run real assertion plants and verify red,
restoration and green. Also verify a declared green control stays green. Verify a control that goes
red blocks publication. Both are required; a refused broken run alone proves no
positive plant. The plugin's committed Scrut fixture exercises these paths and
plants faults in the runner's own assertion and publication guards.
