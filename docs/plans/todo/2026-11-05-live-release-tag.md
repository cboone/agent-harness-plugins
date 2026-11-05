# Switch both harnesses to the live release tag

**Decision:** use `live` as an explicitly approved release pointer in `cboone/agent-harness-plugins`. Plan only: implementation, tag publication and either harness's activation need your separate yes in TOOLING's window.

## Release and helper safety

`live` points to the exact reviewed `main` commit already published as `catalog-<full-SHA>`, never a work branch. Keep immutable catalog tags and plugin manifest versions. TOOLING prepares the old/new SHA pair and rollback target; you publish the initial tag and each later move, only after your window yes. Extend the existing [release workflow](../../../.github/workflows/release.yml) and [release guidance](../../../plugins/release/skills/release/SKILL.md) with this manual promotion step; no automatic `live` movement on merge. A move needs an exact old-target lease and explicit authorization for that tag replacement.

Recommend landing [the helper snapshot fix](https://github.com/cboone/agent-harness-plugins/issues/729) before the first promoted release: snapshot complete helper bundles into task-owned directories, verify SHA-256 and modes before every invocation, and retain version/hash identity through run, render and verify. Cover review helpers, both trims and checked runners; plant a release during a running task and prove it survives. Existing workers must already hold verified snapshots or finish before activation. A quiet-worker-only move is the fallback, not the permanent design: startup/resume refresh timing remains unknown. The tag controls release selection; snapshots protect in-flight work.

## Config and deliberate updates

After approval, preserve the existing marketplace URL and plugin enablement. In `~/.codex/config.toml`, set the marketplace table to:

```toml
[marketplaces.agent-harness-plugins]
source_type = "git"
source = "https://github.com/cboone/agent-harness-plugins.git"
ref = "live"
```

In Claude's user `settings.json`, merge this entry under `extraKnownMarketplaces`:

```json
{"agent-harness-plugins":{"source":{"source":"git","url":"https://github.com/cboone/agent-harness-plugins.git","ref":"live"},"autoUpdate":false}}
```

Snapshot previous settings and record marketplace SHA, installed versions and helper hashes before switching. Do not re-add an existing marketplace name: the tests refused that operation. Run:

```bash
codex plugin marketplace upgrade agent-harness-plugins --json
claude plugin marketplace update agent-harness-plugins --json
claude plugin update plant-defects@agent-harness-plugins --scope user --json
```

Repeat the last command for **every installed plugin** from this marketplace, replacing `plant-defects` with its name. Marketplace refresh alone leaves Claude's installed copy unchanged. Restart Claude after plugin updates; restart Codex and verify loaded versions too. Keep Claude `autoUpdate: false`; no Codex automatic-update switch was established. Disabled plugins are not an update lock.

## First move and rollback

Use disposable authenticated sessions in each harness, with separately authorized login and no credential copying or real transcript inspection. Before and after the first real move, record source SHA, installed manifest versions, helper hashes and old-cache presence: check a new session and resume before deliberate refresh, then repeat after updates and restart. Require both harnesses to resolve the approved target and successfully invoke snapshotted helpers; unexpected movement or any failure stops rollout. Private-probe GitHub authentication differs from the public marketplace; successful authenticated startup/resume remains unconfirmed.

Rollback: stop rollout, preserve evidence, and restore saved config entries. To restore plugin content as well, obtain your window yes to return `live` to the recorded previous release using the exact-current-target lease, repeat both update sequences and restarts, and verify SHAs, versions and helper hashes. Config restoration alone cannot restore Codex's deleted cache; Claude downgrade behavior also needs verification. Never reuse another bundle to render existing results.

**Prior art:** `report.md`, `report-2.md` and `report-3.md` in `~/.local/state/conductor/codex-answers/2026-11-04-live-tag-test/` establish unchanged-tag pins, refused `file://` sources, then deliberate moved-tag adoption in a private GitHub probe. Codex deleted the old cache; Claude retained it. No immediate movement in stopped consumers proves nothing about authenticated lifecycle paths. [Codex config](https://learn.chatgpt.com/docs/config-file/config-reference) supports refs; [plugin docs](https://developers.openai.com/plugins/build/plugins) document explicit upgrades. [Claude loading docs](https://code.claude.com/docs/en/plugins/loading#when-auto-update-runs) document auto-update controls; tests establish the separate plugin update and restart requirement. Reuse these mechanisms rather than add a watcher.
