# Load-timeout plant refresh

PRs #772 and #773 changed `checked_core.py`. On `origin/main` at `a9bad10d`, three patches had stale context around guards that still exist.

- `unknown-final-state-accepted` targets the inspection timeout handler in `stop_group`. It returns an empty member list and no error when the SIGKILL inspection times out.
- `kill-reserve-consumed` targets the signal deadline loop in `stop_group`. It gives SIGKILL the SIGTERM deadline, removing its reserved observation window.
- `reconciliation-accepts-live-work` targets the reuse check after a successful leader identity read in `SupervisionRuntime.reconcile`. It records any readable leader as reused and the group as gone.

`git apply --check` exited 1 for each of these three patches before the refresh and 0 for each afterward. Every other manifest patch exited 0 both times, for 45 passing patches after the refresh.

The existing `red.contains` entries still name the assertions for these same weakenings.

## Isolated baseline inputs

The first variant failed its baseline in the receipt run.
`test_existing_manifest_normal_verdicts_are_preserved` compares the manifests
it discovers to the paths recorded in `tests/data/checked-verdict-compatibility.json`.
The test's expected inventory grew after #733, while the manifest's original
copied input list omitted eight of those files.

- `2026-11-07-installed-checklist-drift-plants.json`
- `2026-11-07-repourl-stated-check-plants.json`
- `2026-11-07-reviewer-confirmation-plants.json`
- `2026-11-08-load-bounds-clock-real-grace-clock-plants.json`
- `2026-11-08-load-bounds-lifecycle-owner-finalizer-disabled-plants.json`
- `2026-11-08-load-bounds-lifecycle-registration-diagnostic-suppressed-plants.json`
- `2026-11-08-load-bounds-readers-early-reader-1-plants.json`
- `2026-11-08-load-bounds-readers-early-reader-5-plants.json`

With those manifests present, the compatibility test passed and the baseline
reached `test_plant_fixture_execution_covers_declared_detector_waits`. Its
static inspection follows each manifest's check script and reads the detector
sources to calculate wait bounds. The copied input list also includes these
files so the audit covers the same detectors in the isolated copy.

- `docs/reviews/2026-11-07-installed-checklist-drift-plants/check.bash`
- `docs/reviews/2026-11-07-installed-checklist-drift-plants/detector.py`
- `docs/reviews/2026-11-07-repourl-stated-check-plants/check`
- `docs/reviews/2026-11-07-reviewer-confirmation-plants/check.sh`
- `docs/reviews/2026-11-08-load-bounds-plants/check-clock.bash`
- `docs/reviews/2026-11-08-load-bounds-plants/check-lifecycle.bash`
- `docs/reviews/2026-11-08-load-bounds-plants/check.bash`
- `tests/notification_load_test.py`

The budget test takes the notification clock's wait from a fixed declaration
when it reads the other manifests. It does not read the clock script.
