# Codex fallback guidance

The skill and references retain CLAUDE.md fallback beside a symlink, explain filename precedence, and exclude global guidance from the project byte cap. The root budget rule now checks the project chain. Build and version audit passed; the longest project chain measured 10067 bytes.

Issue: <https://github.com/cboone/agent-harness-plugins/issues/636>.

## Verification

Installed codex-cli 0.164.0 debug prompt-input probes used an isolated home and repository:

| Case                                                | Global marker | Root marker | Nested fallback marker |
| --------------------------------------------------- | ------------- | ----------- | ---------------------- |
| Fallback enabled; root CLAUDE symlink beside AGENTS | 1             | 1           | 1                      |
| Fallback disabled                                   | 1             | 1           | 0                      |
| Project cap reduced to 8 bytes                      | 1             | 0           | 0                      |
| Empty root override                                 | 1             | 0           | 1                      |

The empty-file probe corrects the non-empty wording in the [official discovery page](https://learn.chatgpt.com/docs/agent-configuration/agents-md). Only documentation changed; no runtime test was added.

## Review

Standalone read-only gpt-6.1-sol, high effort, 872000-token window; snapshots stayed unchanged with no lasting changes found.

| Reviewer's label                                      | Our severity                                                | Take or record                                                              | Review again                                                     |
| ----------------------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| important: empty files do not trigger fallback        | Important: guidance could silently be skipped               | Took; corrected every affected statement and verified the empty-file case   | Docs-only fix; general Nit loop ended: fixes changed no behavior |
| important: discovery settings nested in sandbox table | Important: copied configuration ignores the documented keys | Took; TOOLING authorized moving all three keys above the first table header | Docs-only fix; structural loop ended: fixes changed no behavior  |

Small-change review escalated to full order after the Important finding. Structural anti-patterns found the table issue; report-only simplify found none. TOOLING limited the table repair to this block and requested reporting other examples rather than fixing them. All three TOML examples parse; no additional misplaced discovery or search keys were found in the other examples. The prose trim applied four wording changes at low effort with the same model/window. Comment trim had no applicable source comments.

Local make test-all passed lint/validation and 30 of 31 documents; only unchanged launch-workmux.md failed. TOOLING's accepted exception references <https://github.com/cboone/agent-harness-plugins/issues/439>, <https://github.com/cboone/agent-harness-plugins/issues/397> and <https://github.com/cboone/agent-harness-plugins/issues/435>; green PR CI remains required.

## TOML probe

The main example is parsed as TOML and checked for root-level discovery and search keys. This manual check is not part of CI:

````python
import re
import tomllib
from pathlib import Path

path = Path("plugins/clean-up-agent-config/skills/clean-up-agent-config/references/agent-config-files.md")
blocks = re.findall(r"^```toml\n(.*?)^```", path.read_text(), re.M | re.S)
main = next(tomllib.loads(block) for block in blocks if "[sandbox_workspace_write]" in block)
keys = {"project_doc_max_bytes", "project_doc_fallback_filenames", "web_search"}
assert keys <= main.keys()
assert not keys.intersection(main["sandbox_workspace_write"])
````

Restoring the old table nesting in the actual source made the TOML probe fail on all three missing top-level keys. Restoring the repair passed; all three examples parsed. The report-only Semgrep baseline scan in a disposable shared clone completed with zero new findings and no errors. Semgrep listed the manifest and changed Markdown as scanned; the TOML probe checked the examples' key scoping.
