# Save GitHub traffic history

Issue: #561

## Context

Claude Code, Codex CLI and OpenCode install this marketplace by cloning the whole repository, so the GitHub traffic API is the only install signal. It keeps 14 days, and its clone counts include this repository's own Actions checkouts, which can dominate a day (236 clones from 21 unique sources on 2026-10-06).

## Decisions

- The dataset lives on an orphan `traffic-data` branch. Daily commits stay out of `main` history, and the workflow pushes them with `GITHUB_TOKEN`, which starts no other workflow.
- A generated `README.md` on the data branch carries a daily table for the latest 14 days and a weekly table for all history. No chart for now.
- Automation clones per day are the `actions/checkout` steps that ran in every job of every attempt, plus jobs of runs with the `dynamic` event (Copilot pull request reviews and Dependabot updates), which clone the repository without a checkout step. Each completed UTC day inside the current traffic window is counted once, on the first run that finds all of its Actions runs completed.

## Changes

1. Add `bin/record-traffic`: fetch `traffic/clones`, `traffic/views`, `traffic/popular/referrers` and `traffic/popular/paths`; merge daily counts into `daily.json` keyed by date; save referrers and paths as dated snapshots; count automation clones; regenerate `README.md`.
1. Add `.github/workflows/traffic-history.yml`: daily schedule plus `workflow_dispatch`, SHA-pinned checkout, `concurrency`, `timeout-minutes`. Reads the APIs with a `TRAFFIC_TOKEN` secret (fine-grained, this repository only, Administration read and Actions read) and commits to `traffic-data` with `GITHUB_TOKEN`.
1. Add `tests/scrut/record-traffic.md` against `tests/fixtures/gh-stub` with data under `tests/data/record-traffic/`, registered in the `Makefile` and `ci.yml`.
1. Document the tool in `bin/AGENTS.md` and the root `AGENTS.md`.

## Limits

- Unique cloner counts cannot be adjusted for automation, so the external figure is an estimate of clones, not of people.
- Marketplace update fetches from existing installs still count as clones.
- A run's checkouts are dated by the run's creation day, and each day is counted once. Re-run attempts that start after that count are never included.

## Setup

1. Store a token with Administration read and Actions read access as the `TRAFFIC_TOKEN` repository secret (done 2026-10-07).
1. Seed `traffic-data` with the current 14-day window (done locally with `bin/record-traffic` on 2026-10-07, because `workflow_dispatch` needs the workflow on `main`).
1. After merge, run the workflow once with `workflow_dispatch` to check the token and the push.
