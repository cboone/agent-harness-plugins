# SQLite transcript search

Plan only. Build and synthetic execution need separate approval; real records need exact-subset approval. Narrow the [shared-records spike](2026-11-03-shared-records-spike.md) to transcript retrieval.

## Prior art and placement

The supplied November 5 survey favors SQLite FTS5's embedded lexical engine and transactions; use ripgrep as the independent reference. Set aside cass v0.10.0 after its fourth trial retained deleted hits, mislocated Codex lines and lost coverage warnings. ccfullsearch offers physical citations but lacks durable coverage and can follow outside history; sessions illustrates FTS5 but archive discovery undermines deletion; claudex retains deleted sessions. Tantivy needs the same custom importer/ledger; Meilisearch needs a service. Resume pickers do not establish this contract. Shared files remain curated context; memory services and sync are outside scope.

Evidence under local `~/.local/state/conductor/codex-answers/`: `2026-11-05-transcript-search-survey/report.md` (surveyed revisions and source links), `2026-11-04-cass-trial-step1/report-4.md` and `results-4.json` in that trial directory (commands, measurements and failures). Comparisons describe those inspected revisions, not verified current releases.

Propose a `transcript-search` catalog plugin: one Python standard-library SQLite CLI and shared skill, mirrored for Codex. Both harnesses use identical `rebuild`, `search`, `status` commands. Check runtime FTS5 availability. Keep private indexes outside Git. Lexical, offline, explicit invocation only: no daemon, watcher, discovery, model or network. Bound metadata output; excerpts require explicit retrieval and remain untrusted evidence.

## Contract

- Require a nonempty manifest of exact absolute regular-file paths, dialect and project labels; hash it. Reject symlinks, directories and globs. No store discovery, history following or fallback; filters only narrow scope. Defer Markdown ingestion.
- Decode Claude message/content blocks and Codex message-bearing JSONL without duplicating mirrored event/response messages. Count metadata and blank physical lines. Preserve session, role, source SHA-256, one-based physical line and zero-based half-open original-record byte range before decoding. Emit `path:line` and structured byte citations with the hash, including escaped/multibyte text.
- Every rebuild reconciles manifest membership and filesystem existence, replacing content and FTS rows transactionally. Missing files and removed entries lose searchable rows; distinguish missing, unreadable and removed outcomes. FTS5 `rebuild` alone is insufficient. Reject unstable reads; suppress invalidated sources even after rollback.
- Persist attempts independently of content publication: generation, manifest hash, source outcomes/diagnostics, observed and last-successful fingerprints, completion/failure/interruption. Restart marks unfinished attempts interrupted. Malformed/unknown content and truncated tails mean partial coverage; suppress that source. Every search/status, including zero hits, rehashes all listed files and reports committed/attempted generation, coverage state and stale/failed/missing counts. Changed, removed or unreadable sources cannot supply current hits. Distinct nonzero exits signal stale/incomplete coverage; complete zero-hit searches succeed.

## Acceptance and later approval

After build approval, commit an isolated offline synthetic trial: twelve sessions, six per harness across two projects, 24 messages, archives/subagents, excluded Markdown and a fake-token file. Deny outside-source reads. Compare twelve known-answer queries and harness/project filters with ripgrep over identical explicit files, inherited configuration/preprocessing disabled. Independently decode escapes and calculate byte spans; raw JSON matches can include metadata.

Require 12/12 recall, no scope leaks, and correct line/byte citations for both dialects with leading metadata, blanks, multibyte text and tool results. Delete a source and remove a manifest entry, rebuild, then require no hits or content/FTS rows. Append without refresh, malform/truncate JSON, remove/restrict a file, interrupt rebuilding and restart: repeated search/status, including zero hits, must retain stale/partial coverage. Include the fake-token fixture as a positive control, exclude it and rebuild, then require absence from results/index bytes. Record exits, cold/warm runtime, index/sidecar bytes, serialized limits and truncation flags against cass's measures. Plant retained-row, wrong-line and hidden-ledger defects; require rejection.

After synthetic acceptance, request approval for individually reviewed staged public tooling sessions from agent-harness-plugins and review-case-corpus: Claude project JSONL and Codex active rollouts only. Exclude archives/subagents/sidechains, memories/shared records, client/private/personal material and credential-bearing output. Approval names exact files and stores, never whole projects. Stop on unexpected reads, network/model/background activity, fake-token leaks, unusable citations, hidden coverage gaps or retained deleted hits.
