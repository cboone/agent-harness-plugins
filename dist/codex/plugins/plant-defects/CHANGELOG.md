# Changelog

## 1.3.0

- Route command, pipeline-stage and process-inspection launches through one
  active-deadline check immediately before launch, guarded by script AST checks.
- Include allocation publication and parent-state audit-lock waits in call
  limits, and refuse expired calls immediately before process creation.
- Use independent inclusive wall-clock limits for supervised calls, with
  cooperative TERM unwinding and recorded containment ownership.
- Preserve EPERM and phase deadline causes separately, failing closed when group
  cleanup cannot be confirmed.
- Add optional `git_timeout` for Git initialization, patch validation and patch
  application. The default remains the manifest's `timeout`.
- Keep restart-fixture assertion diagnostics free of captured runner output.
