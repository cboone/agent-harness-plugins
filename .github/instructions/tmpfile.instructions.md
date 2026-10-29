---
applyTo: "plugins/**/*.md,tests/**/*.md,dist/**/*.md"
---

# Tmpfile pattern review instructions

Follow the [canonical tmpfile pattern](../../plugins/use-git/skills/use-git/references/tmpfile-pattern.md). Its resource checks apply to both Claude Code and Codex; command approval and filesystem access are separate.

- Prefer an explicit template under `${TMPDIR:-/tmp}`. Neither that spelling nor a command exclusion proves the resolved directory is writable. The fallback may be denied. Report a demonstrated resource-access gap even when the preferred template is present.
- Keep the non-secret file-flag pattern's `-u` convention separate from atomic reservation for sensitive temporary files. Plain `mktemp` remains appropriate for sensitive content written through a shell redirect. Do not replace it with `-u`.
- Treat sample paths as illustrative output, not fixed directories for either harness. Check the actual runtime path and active restrictions before judging access.
- Review command-permission examples using the target harness's own syntax and the actual command text. Creation can contain an unexpanded template while cleanup uses the recorded literal path. A distinctive filename prefix avoids assuming a fixed directory, but it does not grant resource access or guarantee a match.
- Preserve escaped inner quotes in copyable JSON settings examples. Do not change user settings as part of running a skill.
