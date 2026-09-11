# Sync Metadata

Every board states when it was synced and against what revision. Without that, a reader cannot tell a board synced this morning from one that went stale a week ago, and a stale board is worse than none, because it is trusted.

## Required Fields

| Field         | Value                                                | Source                                                   |
| ------------- | ---------------------------------------------------- | -------------------------------------------------------- |
| `sync.at`     | The moment the data was gathered, in UTC             | `date -u +%Y-%m-%dT%H:%M:%SZ`                            |
| `sync.branch` | The default branch the board was synced against      | `gh repo view --json defaultBranchRef`                   |
| `sync.commit` | The full SHA at the tip of that branch on the remote | `git fetch origin BRANCH && git rev-parse origin/BRANCH` |

Take the commit from the remote-tracking branch after a fetch, never from the local checkout. A worktree on a feature branch, or a local default branch that has fallen behind, reports a revision the board was not synced against.

## Optional Fields

| Field                   | Value                                                            |
| ----------------------- | ---------------------------------------------------------------- |
| `sync.timeZone`         | The user's IANA zone, such as `America/New_York`                 |
| `sync.openPullRequests` | The count of open pull requests                                  |
| `sync.extra`            | Further revision markers the repository has, each a short phrase |

With `timeZone` set, every viewer sees the sync time the user sees. On macOS and most Linux systems, `readlink /etc/localtime` ends in the zone name. When the zone cannot be determined, omit the field and each viewer sees the time in their own zone. Validation rejects a name the time zone database does not have, and a page given one anyway shows the time in UTC, so its viewers still agree.

Use `extra` for anything else that pins what the board reflects, such as a catalog version tag, a release, or a count of packages. The footer lists each entry after the issue counts, so keep them short.

## What the Page Shows

- The header shows the sync date and time, and a live age, such as "Synced 3 hours ago", that the page recomputes every minute from the viewer's clock. After a full day the age turns amber, and after three days it turns red.
- The footer repeats the time, links the branch and the short commit, lists the counts and every `extra` entry, and reminds the reader that the source, not the page, is authoritative.

## When to Re-sync

Re-sync after anything that changes what the board claims: an issue opened, closed, or moved to another milestone, a pull request merged, or a branch or worktree started. When the user comes back to a board after a gap, check its age before relying on it, and re-sync first if it predates the work it would drive.
