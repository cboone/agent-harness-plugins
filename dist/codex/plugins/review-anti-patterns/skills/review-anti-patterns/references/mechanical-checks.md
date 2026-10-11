# Mechanical checks

Some checklist items cannot be settled by reading. Whether a workflow expression is valid, whether a cloud CLI accepts a flag, or whether a test can fail depends on how a tool behaves, and a reviewer's belief about that is the guess that Copilot later corrects. This file lists commands that settle those items.

## Rules

- **Run only what the project already supports.** A check counts as supported when the tool is installed and the project already uses it: a Makefile target, a package script, a CI step, a configuration file, or an initialized working directory. Do not install a tool, add configuration, or initialize anything to make a check possible.
- **Run only read-only checks.** A check that writes files in the repository, changes the index, deploys, sends a request that changes remote state, or needs credentials the session does not have is not run. `terraform init` writes `.terraform/`, so it is not a read-only check, and `terraform validate` runs only where a working directory is already initialized.
- **Prefer the project's own command.** When the project wraps a tool in `make lint` or a package script, run that command over the scope's files instead of calling the tool directly, so its configuration and version apply.
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
| Tests the change adds        | the test run on its own, confirming from the runner's output that it ran and how many cases it ran                               |
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
