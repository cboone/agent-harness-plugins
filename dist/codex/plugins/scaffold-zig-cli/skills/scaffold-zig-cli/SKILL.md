---
name: scaffold-zig-cli
description: >-
  Scaffold a complete Zig CLI project with build.zig, build.zig.zon,
  cross-compiled releases, GitHub Actions CI/CD, and Makefile.
---

# Scaffold Zig CLI

Generate the full boilerplate for a new Zig CLI project.

## Workflow

### 1. Gather Project Information

If the user provided a project name in their request, use it as the project name and skip asking for it. Still ask for the remaining parameters unless already provided in the user's initial request.

Ask the user for these parameters:

- **Project name** -- kebab-case, used as the binary name and directory name (e.g., `my-tool`)
- **Short description** -- one sentence, used in the README

**Validate the project name before using it anywhere.** It becomes a directory name and a binary name, and step 3 passes it to `mkdir` and `cd`, so it must match `[a-z0-9]+(-[a-z0-9]+)*`: lowercase alphanumeric segments joined by single hyphens, nothing else. Reject anything else and ask again rather than repairing it.

That pattern is doing real work, not tidiness. A name beginning with a hyphen, `-tool` for instance, reads as options to `mkdir -p` and `cd` instead of as a path. A name containing `/` scaffolds into a different directory than the one reported. `.` and `..` escape the target entirely. A name with whitespace or a shell metacharacter splits into several arguments. Quote the name wherever it reaches a command as well, so the pattern is the guarantee rather than the only defence.

Reject one more set the pattern lets through: the Windows reserved device names, which are `con`, `prn`, `aux`, `nul`, and `com0` through `com9` and `lpt0` through `lpt9`. Windows reserves these whatever the extension, so `con` cannot be a directory and `con.exe` cannot be written or extracted. The release workflow cross-compiles a Windows target and packages `PROJECT-NAME.exe` into a zip, so a project named `con` produces an archive nobody on Windows can unpack. Match them case-insensitively against the whole name; a name that merely contains one, like `con-tool`, is fine.

Derive the **package name** from the project name rather than asking: replace every hyphen with an underscore (`my-tool` becomes `my_tool`). Wherever templates reference `PACKAGE-NAME`, use this form; wherever they reference `PROJECT-NAME`, use the kebab-case form. The binary keeps the hyphens.

Then **validate the derived name**, because replacing hyphens is necessary and not sufficient. `build.zig.zon`'s `.name` must be a bare Zig identifier that is not a reserved word, which means it matches `[A-Za-z_][A-Za-z0-9_]*` and is none of Zig's keywords (`test`, `error`, `fn`, `async`, `export`, `struct`, and the rest). Two of these three project names derive to something Zig rejects:

| Project name | Derived    | Result                                            |
| ------------ | ---------- | ------------------------------------------------- |
| `my-tool`    | `my_tool`  | accepted                                          |
| `test`       | `test`     | `error: expected expression, found '.'` (keyword) |
| `123-tool`   | `123_tool` | `error: expected expression, found '.'` (digit)   |

If the derived name fails either rule, stop and ask the user for a package name that passes, keeping their chosen project name for the binary and the directory. Do not silently rewrite it: the package name is half of the package's permanent identity, so the user should choose it.

**The name they supply replaces the derived one from here on.** Validate it the same way. Quoting is the likely thing to try and it does not work: `.@"my-tool"` and `.@"test"` are both refused with `error: name must be a valid bare zig identifier`, so a replacement has to be a bare non-keyword identifier like any other. Use it for **every** `PACKAGE-NAME` substitution: steps 6, 7 and 8, and step 10, which keys `typos.toml`'s identifier entry on it. Those steps say "the underscored package name" as shorthand for whichever name survived this step, not for a value re-derived from the project name. Re-deriving it would write the rejected name back into `build.zig.zon` and fail the same way at step 21, and would leave the typo allowlist keyed to a name that appears nowhere in the project.

If the user already provided some or all of these in their initial request, do not re-ask. Derive what you can from context.

### 2. Detect User Identity

Detect the user's GitHub username and full name for use in templates:

```bash
# GitHub username (for repository URLs, Homebrew tap)
gh api user -q .login
```

```bash
# Full name (for LICENSE copyright)
git config user.name
```

**Every `git config` read in this step resolves against the current directory**, and this step runs before step 3 has chosen the target. Invoked from inside some other repository, these read that repository's local config, which may not be what the scaffolded project will commit with. `gh api user` is account-level and unaffected.

So treat the values here as provisional: good enough to fill `COPYRIGHT-HOLDER`, not good enough to conclude anything about whether step 23 can commit. Step 4 re-reads them in the target, which is the only place the answer is authoritative.

Use the GitHub username wherever templates reference `GITHUB-USERNAME` and the full name wherever they reference `COPYRIGHT-HOLDER`.

The two failures are not handled alike. If `gh api user` fails or returns nothing, ask the user for the value: it is account-level, so nothing later in the workflow will answer it any better. If `git config user.name` returns nothing, **do not ask yet**. Note it and move on, for the reason below: step 4 reads the target's own config, and an empty answer here is as likely to mean the skill was invoked from the wrong place as it is to mean the value is unset.

`git config user.name` is read here as template input, which is not the same as git being configured to commit. Step 23 makes a GPG-signed commit, and that needs `user.email` and a signing key as well:

```bash
git config user.email
git config gpg.format
git config user.signingkey
```

A value supplied by the user for `COPYRIGHT-HOLDER` does not configure anything, and step 23 needs git's own committer identity rather than a name someone typed. **Do not stop here on an unset value.** These reads are provisional, and stopping on them rejects a perfectly good target: invoked from a directory with no global identity, they come back empty even when the target repository has a local `user.name` and `user.email` of its own. Note what is missing and carry on; step 4 decides.

The same applies to signing. Read the pair together rather than accepting either alone, because `gpg.format` selects the backend and not a key, so `gpg.format=ssh` with no `user.signingkey` looks configured and still fails at `git commit -S`. The two cases differ:

- **`gpg.format` is `ssh`**: `user.signingkey` is required. Unset means signing will fail.
- **`gpg.format` is unset or `openpgp`**: `user.signingkey` is optional, because GnuPG can select a key from the committer identity. Unset is not conclusive either way.

Carry both observations into step 4 and judge them there, once the target's own config is the one being read.

### 3. Verify the Target Directory

The project is scaffolded in a directory named after the project. Establish that directory and **change into it** before anything else in this step:

- If the current directory is already named after the project, it **is** the target and no move is needed, whether or not it is empty. Its contents are the preflight's business, not this branch's.
- Otherwise, create it and enter it:

```bash
mkdir -p "PROJECT-NAME"
cd "PROJECT-NAME"
```

Emptiness is deliberately not part of the first test. The recommended order runs `scaffold-new-repo` first, which leaves a populated directory named after the project, and requiring emptiness there sends that case down the second branch to create `PROJECT-NAME/PROJECT-NAME` inside it. That nests the project one level too deep and steps straight past the preflight whose whole purpose is to notice the boilerplate already sitting there. A directory with the project's name is the project's directory.

Every path from here on is relative to the target, in this step and in every later one: the preflight below, `git init`, `zig build`, and each generated file. Entering the directory is therefore not optional. Creating it and staying put scaffolds the whole project into the parent, and the preflight would report on the wrong directory while doing it.

If a later step reports the wrong directory, check this one first.

Before generating anything, check what is already there. Two separate checks, because they catch different things.

**Files this run would overwrite.** Later steps write all of these, and most are not Zig-specific, so a check limited to `build.zig` and `src/` misses the ones most likely to already exist:

```bash
ls -d build.zig build.zig.zon src README.md LICENSE CHANGELOG.md Makefile \
  typos.toml .gitignore .editorconfig .github/workflows/ci.yml \
  .github/workflows/release.yml .claude/settings.json \
  .github/copilot-instructions.md \
  docs/plans/todo/.gitkeep docs/plans/done/.gitkeep tests/.gitkeep 2> /dev/null
```

Anything listed will be replaced, except the `.gitkeep` files, which step 20 creates with `touch` and therefore leaves intact if they already exist. Step 23 stages them either way, so an existing one with content in it would go into the scaffold commit; report it rather than staging it blind. Four paths are merged rather than overwritten: `.gitignore`, `.editorconfig` and `.claude/settings.json` per steps 12, 13 and 19, and `.github/copilot-instructions.md` per step 22. Name those separately when reporting, since an existing one is appended to rather than lost. For the rest, show the user what would be lost and ask before continuing. A directory holding someone's `README.md` and `Makefile` is the case this exists for, and it does not have to be a git repository to lose work.

Note that this check stands on its own: a clean `git status` later says nothing about it, because committed files are exactly the ones `git status` stays quiet about.

The second check, for uncommitted work, waits for step 4. It only makes sense once the repository step 23 will commit into is known, and that is what step 4 establishes.

### 4. Initialize Git

Skip `git init` only when the **target itself** is the root of a repository. Ask git where the root is and compare it to the target:

```bash
git rev-parse --show-toplevel 2> /dev/null
```

Skip `git init` only if that prints the target directory. No output means there is no repository here, and a different path means the target sits inside someone else's.

**When it prints the target, check for uncommitted work before going further:**

```bash
git status --porcelain
```

Any output means this repository carries work that is not the scaffold's. Report it and ask whether to continue, since step 23's commit is signed and should hold only generated files.

Run this check in that case alone. In the other two the target is about to become its own repository, and `git status` would be reporting on something else: from a directory nested inside the caller's repository it describes that repository, whose uncommitted work has nothing to do with the scaffold and would block it for no reason.

Being merely _inside_ a repository is not the same thing and must not skip it. Step 3 may have created the target as a subdirectory of wherever the skill was invoked, and if that was a repository, the new directory is inside it while having none of its own. Skipping `git init` there leaves the scaffold with no repository, and step 23's `git add` and signed `git commit` then land in the caller's repository instead. Initialize a nested target like any other:

```bash
git init
```

**If `git init` failed**, do exactly two things and then leave this step.

1. If step 2 left `COPYRIGHT-HOLDER` unfilled because `git config user.name` was empty, **ask for it now**. This one is not optional and is not covered by the skip below: step 2 deferred the question to the re-read further down, the re-read is about to be skipped, and nothing later asks it. Step 16 would write a LICENSE with the placeholder still in it.
1. Skip everything else in this step, including those reads, which need a repository and would fail too.

Then carry on to the generation steps, and skip step 23 per the Error Handling entry.

Otherwise re-read the committer identity, from inside the target, because only here does its own local config apply. Do this **every time**, including when `git init` was skipped: an existing target repository has its own config, and that is the one step 23 commits with. Step 2's values came from wherever the skill was invoked, and step 3 has since changed into the target:

```bash
git config user.name
git config user.email
git config gpg.format
git config user.signingkey
```

Judge them by step 2's rules, and let these answers win where they differ.

If `user.name` here differs from the value step 2 put in `COPYRIGHT-HOLDER`, **stop and ask which belongs in the LICENSE**, naming both. Do not pick one and carry on. The committer and the copyright holder are genuinely allowed to differ, so neither is the safe default: taking the step 2 value attributes the project to whoever the caller happened to be, and taking this one overrides a name the user may have chosen deliberately. Attribution in a LICENSE is not a detail to infer, and this is the last moment before step 16 writes it.

Whichever they choose goes in the LICENSE. The committer identity for step 23 stays as read here regardless.

If step 2 came back with no `user.name` and left `COPYRIGHT-HOLDER` unfilled, fill it from `user.name` here. Ask the user only if it is still empty at this point, which is the first moment the question is worth asking.

**This is where an unset identity stops the run**, not step 2. If `user.name` or `user.email` is unset here, stop before generating anything: step 23 cannot commit without them, these values are the ones it will use, and stopping now costs nothing. A value that looked missing in step 2 and is present here was never missing; the earlier read was just looking in the wrong place.

Apply step 2's signing rules here too, against these values.

### 5. Detect the Zig Toolchain

The templates target Zig 0.16 and later. Read the installed version:

```bash
zig version
```

Use the version **exactly as printed** wherever templates reference `ZIG-VERSION`. Do not strip anything.

A development toolchain prints something like `0.17.0-dev.164+bc7955306`. Write that whole string. `mlugg/setup-zig` installs precisely the value in `minimum_zig_version`, so truncating it to `0.17.0` pins CI to a release that does not exist yet and the workflow fails on its first run. Setting a dev-channel pin to the full `0.X.Y-dev.NNNN+abcdef` snapshot is what `pin-everything`'s language-runtime guidance prescribes.

When the version carries a `-dev` component, say so in the summary: the development channel changes daily and old snapshots leave the download index, so the pin will need attention sooner than a release pin would. That is the user's call to make, not a reason to rewrite their toolchain version.

If the installed version is older than `0.16.0`, stop and tell the user: 0.16 removed `std.io` and `std.fs.File` and changed `main`'s signature, so these templates do not compile on 0.15.

If `zig version` fails, Zig is not installed or not on the PATH. Ask the user to install it before continuing.

### 6. Generate build.zig.zon

Read `./references/build-zig-zon.md` for the template and create `build.zig.zon` from it.

- Replace `PACKAGE-NAME` with the underscored package name
- Replace `ZIG-VERSION` with the detected Zig version, exactly as printed

Leave the `.fingerprint` field out entirely. Step 21 fills it in from the compiler's own output. Never copy a fingerprint from another project: it is half of a package's globally unique identity, and reusing one claims another package's identity.

### 7. Generate build.zig

Read `./references/build-zig.md` for the template and create `build.zig` from it.

- Replace `PROJECT-NAME` with the project name (kebab-case, this is the binary name)
- Replace `PACKAGE-NAME` with the underscored package name (this is the module name)

### 8. Generate src/root.zig

Read `./references/root-zig.md` for the template and create `src/root.zig` from it.

- Replace `PROJECT-NAME` with the project name
- Replace `PACKAGE-NAME` with the underscored package name

### 9. Generate src/main.zig

Read `./references/main-zig.md` for the template and create `src/main.zig` from it.

- Replace `PROJECT-NAME` with the project name

There is no `PACKAGE-NAME` in this template. `build.zig` registers the library module under the fixed import name `lib`, so nothing in `src/main.zig` depends on what the package is called.

### 10. Generate typos.toml

Read `./references/typos.md` for the template and create `typos.toml` from it.

- Replace `PACKAGE-NAME` with the underscored package name

### 11. Generate Makefile

Read `./references/makefile.md` for the template and create `Makefile` from it.

- Replace `PROJECT-NAME` with the project name

### 12. Generate .gitignore

Read `./references/gitignore.md` for the template and create `.gitignore` from it.

No replacements needed.

If a `.gitignore` already exists, merge the template entries into it rather than overwriting.

### 13. Generate .editorconfig

Read `./references/editorconfig.md` for the template and create `.editorconfig` from it.

No replacements needed.

If an `.editorconfig` already exists, merge the Zig sections into it rather than overwriting.

### 14. Generate CI Workflow

Read `./references/ci-workflow.md` for the template and create `.github/workflows/ci.yml` from it.

No replacements needed (the workflow is project-name-independent).

### 15. Generate Release Workflow

Read `./references/release-workflow.md` for the template and create `.github/workflows/release.yml` from it.

- Replace `PROJECT-NAME` with the project name

### 16. Generate LICENSE

Read `./references/license.md` for the LICENSE template and create `LICENSE` from it.

- Replace `YEAR` with the current year (run `date +%Y` to get it)
- Replace `COPYRIGHT-HOLDER` with the detected full name. It is settled by step 4 on every path, including the one where `git init` failed, so it should never still be a placeholder here. If it is, ask before writing the file rather than emitting the placeholder

Generate `LICENSE` before running any build. `build.zig.zon` lists it in `.paths`, and that list determines the package hash a downstream consumer computes.

### 17. Generate README.md

Read `./references/readme.md` for the README template and create `README.md` from it.

- Replace `PROJECT-NAME` with the project name (kebab-case)
- Replace `PROJECT-DESCRIPTION` with the short description
- Replace `GITHUB-USERNAME` with the detected GitHub username
- Replace `ZIG-VERSION` with the detected Zig version, exactly as printed

### 18. Generate CHANGELOG.md

Create `CHANGELOG.md` with the initial changelog template:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
```

No replacements needed. The `release` skill will populate version sections and comparison links on the first release.

### 19. Seed .claude/settings.json

Add the Zig commands this project runs constantly to the tracked allowlist, so building and formatting do not prompt on every invocation.

If `.claude/settings.json` exists (the scaffold-new-repo skill creates it with an empty allowlist when running in the bootstrap flow), merge these three entries into `permissions.allow`, preserving any entries already there:

```json
["Bash(zig build*)", "Bash(zig fmt*)", "Bash(zig version)"]
```

If the file does not exist, create it:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(zig build*)", "Bash(zig fmt*)", "Bash(zig version)"],
    "deny": []
  }
}
```

`Bash(zig build*)` has no space before the asterisk on purpose, so it covers bare `zig build` as well as `zig build test` and `zig build -Dtarget=...`. These belong in the tracked `settings.json` rather than the untracked `settings.local.json`: every contributor runs the same commands, so there is nothing machine-specific about them.

### 20. Create Directory Stubs

Create stub directories for the standard project layout:

```bash
# plans directory
mkdir -p docs/plans/todo docs/plans/done
touch docs/plans/todo/.gitkeep docs/plans/done/.gitkeep

# tests directory
mkdir -p tests
touch tests/.gitkeep
```

### 21. Verify the Build and Fill In the Fingerprint

`build.zig.zon` has no `.fingerprint` yet, so the first build is expected to fail with the value to use. Run:

```bash
zig build
```

The first invocation reports the missing field and prints the value in the same message:

```text
build.zig.zon:1:2: error: missing top-level 'fingerprint' field; suggested value: 0xd7ba43a4d5bc8918
```

Take the **last** `0x` value on that line and write it into `build.zig.zon` as the `.fingerprint` field, immediately after `.version`, keeping the trailing comment. Indent it four spaces like every other field, shown here in place:

```zig
.{
    .name = .PACKAGE-NAME,
    .version = "0.1.0",
    .fingerprint = 0xd7ba43a4d5bc8918, // Changing this has security and trust implications.
    .minimum_zig_version = "ZIG-VERSION",
```

The indentation is load-bearing. `zig fmt --check` rejects the field at column zero, so writing it flush left makes the `zig build fmt-check` below fail on the manifest this step just edited.

Two diagnostics can appear here and the skill must accept either. An absent field produces `missing top-level 'fingerprint' field; suggested value: 0x...`; a field that is present but wrong produces `invalid fingerprint: 0x...; if this is a new or forked package, use this value: 0x...`. Both put the value to use last on the line. Do not compute a fingerprint, and do not reuse one from another project: the compiler is the only correct source.

Then confirm the project builds, tests and formats cleanly:

```bash
zig build
zig build test
zig build fmt-check
```

All three must succeed before continuing. The comment on the fingerprint line is deliberate: it makes any later change to the field visible in code review.

### 22. Update Copilot Instructions

Do this **before** the initial commit, so the edit lands in it. Running it afterwards leaves a freshly scaffolded repository dirty on its very first `git status`.

If `.github/copilot-instructions.md` exists (created by the scaffold-new-repo skill when running in the bootstrap flow, or already present in an existing repo), append the following entries to the PR review section. Before appending each entry, check whether the bold key text already exists in the file; skip entries that are already present.

To locate the PR review section: look for an existing heading whose text includes "PR Review" or "Code Review" (e.g., `## PR Review`, `## Code Review`, `## PR Review Checklist (CRITICAL)`). If no matching heading exists, append a new `## PR Review` section at the end of the file and place the entries there.

- **The fingerprint is compiler-generated**: `.fingerprint` in `build.zig.zon` was emitted by Zig for this package and is half of its globally unique identity, paired with `.name`. Do not suggest copying one from another project, editing it by hand, or changing it while the package name stays the same. Regenerating it is correct in exactly one case: the package identity itself changes, as when the project is forked or `.name` is changed. Then delete the field and let `zig build` emit a new value, and use the value the compiler reports rather than any other.
- **`minimum_zig_version` is the only Zig version pin**: CI resolves the toolchain by reading `build.zig.zon`. Do not suggest restating the version in a workflow file.
- **Tests must not write to stdout**: `zig build test` runs the test binary with stdout wired to the build runner's IPC channel. Suggest writing into a buffer, as `src/root.zig` does, rather than printing.

If `.github/copilot-instructions.md` does not exist, skip this step.

### 23. Create Initial Commit

First check whether any generated path is covered by an ignore rule. Run this **every time**, not only for a target that was already a repository: a fresh `git init` still reads whatever `.gitignore` the directory already held, and a global `core.excludesFile` applies to any repository at all.

```bash
git check-ignore -v \
  build.zig build.zig.zon \
  src/root.zig src/main.zig \
  typos.toml Makefile .gitignore .editorconfig \
  .github/workflows/ci.yml .github/workflows/release.yml \
  .github/copilot-instructions.md \
  .claude/settings.json \
  LICENSE README.md CHANGELOG.md \
  docs/plans/todo/.gitkeep docs/plans/done/.gitkeep tests/.gitkeep
```

`.github/copilot-instructions.md` is in the list because step 22 may have modified it and this step stages it. Drop the paths this run did not touch before running the probe, or accept that it reports on a file you are not about to stage.

Anything it prints would make `git add` refuse that path and abort the commit. It reports the rule alongside the file, so show the user both and ask what they want, rather than forcing the file in. A repository that ignores `.claude/` or `docs/` usually means it, and overriding that silently is not the skill's call: committing the rest and naming what was left out is the better default. Adding a path the user does want is `git add -f <that path>`, which they can ask for.

Then stage the files this run generated, **each by its full path**, and create the initial commit.

The two lists below are the standalone case, where step 22 found no `.github/copilot-instructions.md` and skipped. **When step 22 did modify that file, add `.github/copilot-instructions.md` to both lists**; when it did not, leave it out of both. `git add` aborts with `pathspec ... did not match any files` on a path that is not there, so an unconditional entry would break the commit in exactly the case the file is absent.

```bash
git add \
  build.zig build.zig.zon \
  src/root.zig src/main.zig \
  typos.toml Makefile .gitignore .editorconfig \
  .github/workflows/ci.yml .github/workflows/release.yml \
  .claude/settings.json \
  LICENSE README.md CHANGELOG.md \
  docs/plans/todo/.gitkeep docs/plans/done/.gitkeep tests/.gitkeep
git commit -S -m "feat: scaffold Zig CLI project" -- \
  build.zig build.zig.zon \
  src/root.zig src/main.zig \
  typos.toml Makefile .gitignore .editorconfig \
  .github/workflows/ci.yml .github/workflows/release.yml \
  .claude/settings.json \
  LICENSE README.md CHANGELOG.md \
  docs/plans/todo/.gitkeep docs/plans/done/.gitkeep tests/.gitkeep
```

Drop any `.gitkeep` that step 20 found already present, from both the `git add` and the pathspec. `touch` leaves an existing file's contents alone, so a pre-existing one may hold someone's data, and staging it would put that data in the scaffold commit. Step 3's preflight reports which of the three exist; commit only the ones this run created.

The pathspec after `--` is not redundant with the `git add`. A bare `git commit` commits the whole index, so anything the user had already staged before this run would go into the signed commit no matter how narrow the `git add` was, since staging generated files does not unstage theirs. Repeating the paths on the commit confines it to them and leaves unrelated staged work in the index untouched.

Skip this step entirely if `git init` failed in step 4. There is no repository to commit to, and `git add` and `git commit` will both fail. Say plainly in the summary that the files were generated but no initial commit was created.

Drop only a path this run neither created **nor modified**: steps 12, 13 and 19 merge into an existing `.gitignore`, `.editorconfig` or `.claude/settings.json` rather than replacing it, and those edits still belong in the commit. Dropping them because the file predates the run would leave the Zig ignore rules and the build permissions unstaged.

**Do not use `git add -A`, and do not name a directory.** Step 3 allows scaffolding into a directory that is already a git repository, and step 4 skips `git init` when it is. `-A` sweeps the whole working tree, and `git add` applied to a directory is recursive, so naming `src`, `.github`, `.claude`, `docs`, or `tests` stages whatever else happens to be under them. Either way the user's unrelated work lands in a signed commit they did not ask for. Full paths are what make the set exact.

Check the working tree **before** generating anything, in step 3, not here. Run `git status --porcelain` then, and if the repository already carries changes, tell the user and let them decide whether to continue. A check at this point is too late to help: by the time this step runs, anything swept in has already been committed.

### 24. Summary

Print a summary of what was created:

- List every file and directory generated
- Note the detected Zig version written into `minimum_zig_version`, and the fingerprint the compiler emitted
- Remind the user to:
  - Run `make help` to see available Makefile targets
  - Run `make check` before pushing, which runs the format check, the build and the tests together
  - Run the add-community-files skill to add CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/SECURITY.md, and .github/PULL_REQUEST_TEMPLATE.md
  - Avoid running the scaffold-new-repo skill from here on. It belongs before this one, never after: it writes its own LICENSE, README.md and CHANGELOG.md, and a `.claude/settings.json` with an empty allowlist, so running it now overwrites the Zig-specific files and drops the permissions step 19 seeded. If it has not run yet and its agent config files are wanted, say so and let the user decide, rather than running it and undoing this scaffold
  - Run the set-up-installers skill when ready to set up a Homebrew formula and shell install script
  - Run the add-scrut-cli-tests skill to add snapshot tests for the CLI. It edits `.github/workflows/ci.yml`, adding a `test-scrut` job beside the `ci` job rather than changing that job's inputs, so the `run-zig-ci.yml` call's own `run-scrut` stays off. Keep one or the other rather than both, since enabling both runs the snapshot tests twice
  - Add a `.github/dependabot.yml` with the `github-actions` ecosystem if the workflow pins should keep themselves current. The scaffold pins them to the SHA that was latest when it ran, and nothing updates them on its own
  - Tag a release with `git tag v0.1.0 && git push origin v0.1.0` to trigger the release workflow

## Error Handling

- If `zig version` fails, Zig is not installed or not on the PATH. Point the user at [ziglang.org/download](https://ziglang.org/download/) and stop.
- If the installed Zig is older than 0.16, stop. These templates use `std.Io` and the `std.process.Init` form of `main`, neither of which exists in 0.15.
- If `zig build` reports `name must be a valid bare zig identifier`, or `expected expression, found '.'` on the `.name` line, the package name is not a bare non-keyword identifier. Go back to step 1's validation table: a hyphen, a leading digit, and a Zig keyword each produce one of those two errors, and `.@"..."` quoting fixes none of them. The binary name in `build.zig` is unaffected and keeps its hyphens.
- If `zig build` reports a missing or invalid fingerprint after step 21, the value was transcribed incorrectly. Re-read the diagnostic and take the last `0x` value on the line.
- If step 3's preflight listed any existing path, ask the user before overwriting. That covers every path this run writes, not only the Zig ones: `README.md`, `LICENSE`, `CHANGELOG.md`, `Makefile` and `typos.toml` are the ones most likely to already exist, and losing them is what the preflight is for
- If `git init` fails, continue generating files but warn the user, and **skip both the rest of step 4 and all of step 23**. With no repository the identity re-reads, `git add` and `git commit` all fail. Report that the files were generated and no initial commit was created, rather than letting those commands fail one after another through the run
- If `git commit -S` fails because signing is not configured, tell the user rather than retrying without `-S`. Signing is deliberate, and dropping it is the user's call.
- If the build verification fails, show the error and attempt to fix it before continuing

## Reference Templates

- `./references/build-zig-zon.md` -- `build.zig.zon` manifest template
- `./references/build-zig.md` -- `build.zig` build script template
- `./references/root-zig.md` -- `src/root.zig` library module
- `./references/main-zig.md` -- `src/main.zig` CLI entry point
- `./references/typos.md` -- `typos.toml`
- `./references/makefile.md` -- Makefile template
- `./references/gitignore.md` -- `.gitignore` template
- `./references/editorconfig.md` -- `.editorconfig` template
- `./references/ci-workflow.md` -- CI workflow
- `./references/release-workflow.md` -- release workflow
- `./references/license.md` -- MIT license template
- `./references/readme.md` -- README template

## Refresh `cboone/gh-actions` SHAs before scaffolding

The `cboone/gh-actions` reusable-workflow refs in this skill's templates are SHA-pinned with a `# vX.Y.Z` comment that was current when the template was authored. New releases of `cboone/gh-actions` rot those SHAs. Before emitting a workflow into a user's repo, refresh both the SHA and the comment to current latest:

```bash
TAG="$(gh release view --repo cboone/gh-actions --json tagName --jq '.tagName')"
SHA="$(gh api "repos/cboone/gh-actions/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

Replace each `cboone/gh-actions/.../<workflow>.yml@<old-sha> # <old-tag>` in the emitted workflow with the new SHA and tag. Dependabot in the user's repo keeps them in sync afterwards.

That last sentence assumes a Dependabot configuration this skill does not generate. A scaffolded project has no `.github/dependabot.yml`, so nothing updates the pins until one exists with the `github-actions` ecosystem enabled. Say so in the summary: the refresh above is what makes the pin current at scaffold time, and it is the only thing keeping it current until the user adds that configuration.
