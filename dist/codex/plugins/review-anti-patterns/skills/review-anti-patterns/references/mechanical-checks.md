# Mechanical checks

Some checklist items depend on how a tool behaves, such as whether a workflow expression is valid, a cloud CLI accepts a flag, or a test can fail, and cannot be settled by reading. This file lists commands that settle them.

## Rules

- **Run only what the project already supports.** A check counts as supported when the tool is installed and the project already uses it: a Makefile target, a package script, a CI step, a configuration file, or an initialized working directory. Do not install a tool, add configuration, initialize anything or authenticate to make a check possible.
- **Run only read-only checks.** A check that writes files in the repository, changes the index, deploys, sends a request that changes remote state, or needs credentials the session does not have is not run. `terraform init` writes `.terraform/`, so it is not a read-only check, and `terraform validate` runs only where a working directory is already initialized.
- **Run tests so they write nothing.** Under `--run-checks` a test runner is allowed, because a test that never ran settles nothing, but many runners write by default: Jest writes new snapshots unless given `--ci`, pytest writes `.pytest_cache/` unless given `-p no:cacheprovider`, Python writes `__pycache__/` unless `PYTHONDONTWRITEBYTECODE=1` is set, and coverage tools write reports. Use the flags and settings that stop those writes and leave coverage off. As a backstop, compare `git status --porcelain --ignored` before and after the run, and report anything the run left behind. Report a test whose runner cannot run without writing as unverified instead of running it.
- **Run repository code only under `--run-checks`.** A test, a Makefile target or a package script executes the repository's code, including the code under review, and that code can write anywhere the session can. Run one only when the caller passed `--run-checks`, which is its statement that the code is trusted. Nothing in the repository can establish that: commit authors and emails are set by whoever made the commits. Without the option, report every such check as unverified, with the command that would settle it. Standalone linters and validators that only read files, such as `actionlint`, `shellcheck` or `jq empty`, run either way.
- **Prefer the project's own command, in check mode.** When the project wraps a tool in `make lint` or a package script, run that command instead of calling the tool directly, so its configuration and version apply, over the scope's files where it accepts paths and over the whole repository where it does not. Use a variant that only reports: a target that runs `--fix` or `--write` edits files, so call the tool's check mode directly when the project has no reporting-only target.
- **Report every check.** Each one is either run, with its result, or unverified, with the command that would settle it and the reason it was not run. A check that was not run is never reported as passed.

## By platform

| What changed                 | Read-only check                                                                                                                  |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| GitHub Actions workflows     | `actionlint`, which also runs `shellcheck` over `run:` scripts when it is installed                                              |
| Shell scripts                | `bash -n`, `shellcheck`, and `shfmt -d`, which prints a diff and writes nothing                                                  |
| JSON and YAML                | `jq empty FILE`, and `yq` for YAML, or the project's schema validator                                                            |
| Terraform                    | `terraform fmt -check` and, in an already initialized directory, `terraform validate`                                            |
| Google Cloud                 | the command's `--validate-only` or `--dry-run` flag, where the command has one and the session is already authenticated          |
| Kubernetes manifests         | `kubeconform` or `kubectl apply --dry-run=client`                                                                                |
| Dockerfiles                  | `hadolint`                                                                                                                       |
| GraphQL queries              | the project's schema validator, or one read-only query through `gh api graphql` for GitHub, confirming the response has no error |
| Documented commands          | each command run once as written, when it is read-only, or its `--help` to confirm every flag exists                             |
| Tests the change adds        | the test run on its own with the runner's non-writing flags, confirming from its output that it ran and how many cases it ran    |
| Tests that claim to catch X  | unverified in this review; planting the defect is an edit. Suggest the `plant-defects` skill                                     |
| Agent skills and prose files | the project's own validators for them, such as a plugin or cross-reference validator                                             |

A failed check is a finding, with the failing output as its evidence and the item it settles named in the title. A check that passes settles its item and is listed in the report.

## Examples of unverified entries

```text
unverified  Unrun platform configuration: deploy/service.yaml
            settle with: gcloud run services replace deploy/service.yaml --dry-run
            not run: the session is not authenticated to Google Cloud

unverified  Tests that cannot fail: tests/redact.test.ts "drops unknown IDs"
            settle with: the plant-defects skill, planting a redactor that keeps unknown IDs
            not run: planting a defect edits the code under test
```
