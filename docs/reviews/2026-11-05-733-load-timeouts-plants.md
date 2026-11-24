# Load-timeout plant refresh

PRs #772 and #773 changed `checked_core.py`. On `origin/main` at `a9bad10d`, three patches had stale context around guards that still exist.

- `unknown-final-state-accepted` targets the inspection timeout handler in `stop_group`. It returns an empty member list and no error when the SIGKILL inspection times out.
- `kill-reserve-consumed` targets the signal deadline loop in `stop_group`. It gives SIGKILL the SIGTERM deadline, removing its reserved observation window.
- `reconciliation-accepts-live-work` targets the reuse check after a successful leader identity read in `SupervisionRuntime.reconcile`. It records any readable leader as reused and the group as gone.

`git apply --check` exited 1 for each of these three patches before the refresh and 0 for each afterward. Every other manifest patch exited 0 both times, for 45 passing patches after the refresh.

The existing `red.contains` entries still name the assertions for these same weakenings. Red and green execution is pending until SL-VF finishes its Scrut run.
