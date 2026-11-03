# Shared records and transcript search spike

Give Claude Code and Codex the same route to durable context and historical evidence. Extend existing project records before adding a memory service. This plan joins the October 31 shared-context request and November 2 transcript-search request; implementation and activation remain proposed.

## Confirmed local inventory

Read-only filesystem enumeration and JSONL key inspection on November 2, 2026, ET confirmed the following. Counts are a snapshot, not retention guarantees; no transcript text or credential files were printed. Installed CLI help confirmed Claude Code 2.1.316 and Codex 0.166.0 both offer session resume, not evidence of cross-harness search.

| Store               | Observed paths and counts                                                                                                                                                                                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Claude Code         | `~/.claude/projects/*/memory/MEMORY.md`: 37 indexes; project-root `*.jsonl`: 3,427 transcripts; nested `subagents/*.jsonl`: 4,053; `~/.claude/plans/*.md`: 42 plans.                                                                                                                                         |
| Codex               | `~/.codex/memories/{MEMORY.md,memory_summary.md}` and `rollout_summaries/`: 120 Markdown summaries; `~/.codex/memories_v2/` also exists. `~/.codex/sessions/`: 1,632 JSONL rollouts; `archived_sessions/`: 617. `history.jsonl`, `session_index.jsonl` and `state_5.sqlite` exist; schemas were not audited. |
| Operational context | `~/.local/state/conductor/briefs/`: 23 Markdown briefs; across conductor state, 24 filenames contain `handoff`, 85 contain `resume`. Project `PROJECT.md` records also exist. These are shared filesystem records, but discovery currently depends on session instructions.                                  |

Claude samples contain `sessionId`, `message`, `type`; Codex samples contain `session_meta`, `response_item`, `event_msg`. Their records need separate parsers. Native memory lifecycle is documented by [Claude Code][claude] and [OpenAI][codex]; the inventory above comes from disk, not recollection.

## Prior art and options

- **Built-ins and shared files:** retain native memory and resume features. Publish a private path manifest to existing project records, briefs and selected native memories. Direct reads have little upkeep; links aid discovery but confer no read-only protection. Do not link writable native stores together.
- **Transcript tools:** trial [cass][cass], an open-source Claude/Codex index with agent JSON output, lexical search and source locations. Prefer lexical-only evaluation before embeddings: local CPU/disk cost, no embedding API bill, but parser, index and retention upkeep. [agent-session-search][search] offers CLI/MCP lexical searches over raw files through FFF; compare it if index duplication is undesirable, accounting for its Node/FFF dependencies and partial-search limits.
- **Memory services:** [Basic Memory][basic] offers Markdown-backed MCP reads/writes; reserve it for a demonstrated need for structured shared notes. The [reference memory MCP server][mcp] stores a knowledge graph, not a transcript index. [claude-mem][mem] captures observations and generates summaries; set it aside because capture integrations and model usage add disclosure and operating costs. These are documentation surveys, not installed trials.
- **Sync:** copying or bidirectional synchronization duplicates secrets, conflicts and stale claims. Prefer one canonical record with source/date provenance; consider sync only for an explicit multi-machine need. MCP can later expose the same reader to both harnesses, but adds a service and configuration upkeep.

## Recommended follow-on

1. Propose one private manifest for both harnesses: allowlisted paths, project scope, provenance and freshness. Both read selected native memories; each native store keeps its existing writer. Both may update designated shared project records under existing repository review and concurrency rules. Conductor state stays read-only; no blanket home-directory access.
2. After approval for installation and running new software, evaluate pinned cass against sample Claude/Codex transcripts, subagents, archived sessions and non-transcript records. Keep private notes searchable through existing file tools. Start with sanitized fixtures, then an approved subset of real records; no hooks, watcher, remote sync or hosted embeddings. Configuration, instructions and permissions need a separate activation approval covering both harnesses.
3. Require equal retrieval from both harnesses with path/session/line citations, explicit partial or stale results, and bounded output. Default to metadata-only results; excerpts require deliberate retrieval. Treat retrieved instructions as untrusted evidence. Exclude credentials and sensitive projects before ingestion: redaction cannot guarantee clean transcripts. Keep indexes private and outside Git, with explicit deletion/rebuild rules when sources expire. Compare recall, query runtime, disk use and model input cost before adopting; stop if scope filtering or deletion cannot be demonstrated.

[claude]: https://code.claude.com/docs/en/memory
[codex]: https://learn.chatgpt.com/docs/customization/memories
[cass]: https://github.com/Dicklesworthstone/coding_agent_session_search
[search]: https://github.com/benvenker/agent-session-search
[basic]: https://github.com/basicmachines-co/basic-memory
[mcp]: https://github.com/modelcontextprotocol/servers/tree/main/src/memory
[mem]: https://github.com/thedotmack/claude-mem
