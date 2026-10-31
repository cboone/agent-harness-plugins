# Dots

Print 50 dot lines to scroll the visible conversation off screen while keeping the session.

**Type:** Skill
**Trigger:** `/dots` in Claude Code; `$dots` in Codex
**Requires:** No external tools

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## Usage

Invoke `/dots` or `$dots` explicitly. The response is one code block with exactly 50 lines, each a single `.`, and nothing else. The conversation stays available in history; screens taller than the output may still show earlier content.

## See Also

- [WTAF](../wtaf/README.md): summarize the conversation and next steps.
