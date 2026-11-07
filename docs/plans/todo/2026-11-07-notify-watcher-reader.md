# Notify rollout reader

Replace the Codex failure watcher's repeated EOF polling with a persistent
`tail` reader. Read session metadata once, skip complete startup records at a byte offset,
and extract each new record's fields in one jq invocation. Preserve
failure filtering, delivery claims, notification payloads, partial records and
the final drain after the owner exits.

Existing `tail` and a Bash supervisor cover the reader and owner checks;
no new watcher, dependency or live configuration is needed. The issue proposes this approach. Existing notify fixtures provide capture-only delivery.
Neither hook manifest nor the `notify` hook entry point needs modification.

1. Commit launch-count instrumentation and sample rollout inputs. Save baseline
   startup and idle measurements outside the checkout.
2. Implement the persistent reader and single-pass field extraction. Exercise
   all existing failure shapes and startup, shutdown and partial-record cases.
3. Commit and run plants for idle polling and historical per-line parsing, with
   copy-load and unchanged-baseline preflight before the checked plant gate.
4. Run the full local review order on frozen commits, with hashed input
   preflight, then trim, baseline Semgrep, lint, exact-tree tidy and final gates.
5. Open a ready PR closing the watcher launch issue and report receipts,
   generated measurements and hook impact to TOOLING. Do not wire or merge it.

All runtime inputs are committed sample rollouts. Evidence and owned helper
snapshots live under the workstream's mailbox evidence directory. Results remain
unverified until published through checked gates.
