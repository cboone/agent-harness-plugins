# Give plant detectors an explicit execution margin

TOOLING native000037 and native000038 reopen test-only work under gate
6f62aceb after the default-parallel restart failed in bounded-capture.

- Keep production allocation behavior and the document cap unchanged.
- Use the approved detector wait, cleanup allowance and inclusive check limit.
- Inventory every compatible checked-plant manifest and generated regression
  fixture. Derive declared waits from detector code and reject an execution
  window smaller than twice a declared wait.
- Persist unexpected inner results without printing their captured output.
- Plant the old window/wait mismatch and the new diagnostic boundaries.
- Commit the tests, run lint and baseline static checks, replay the complete
  plant set, and rerun the default-parallel suite on the final committed head.
- Retain load, thermal and survivor observations, then publish the ready PR.
  Production timing defects still stop and report. TOOLING retains the merge
  hold; no CI watcher or worker merge follows the handoff.
