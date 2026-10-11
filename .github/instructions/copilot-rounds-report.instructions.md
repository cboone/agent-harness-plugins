---
applyTo: "bin/copilot-rounds-report,tests/scrut/copilot-rounds-report.md,tests/data/copilot-rounds-report/**"
---

# Copilot rounds report review instructions

These search behaviors are verified against live GitHub search and are intentional:

- **`owner:` is a valid search qualifier**: GitHub issue and pull request search accepts `owner:LOGIN` for both users and organizations, with the same results as `user:` and `org:`. Repeated `owner:` qualifiers combine with OR, so `owner:a owner:b` returns pull requests from either. Do not flag the owner-scoped search as incorrect or suggest `user:`/`org:` instead.
- **`author:@me`, bot authors and `sort:created-asc` resolve as written**: `@me` names the authenticated user, `author:NAME[bot]` and `author:app/NAME` return the same pull requests, and `sort:created-asc` orders results by creation time. Owner and author values are validated as single logins before they reach the search string.
- **The High share is a share of rated findings, and says so**: the findings-per-round table divides High findings by the findings that carry a severity badge and prints that denominator ("of N"). Findings without a recognized badge lower N rather than skewing the share, and the report warns when badge and finding counts disagree. Do not flag the share as misstating severity when N differs from the findings count.
