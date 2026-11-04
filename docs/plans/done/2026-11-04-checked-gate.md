# Checked gate runner

Extend `plant-defects` with a manifest-driven check/action runner and a shared
execution core. CONDUCTOR authorized corrective work under the grouped-shell
stop. No activation, hooks or instruction changes belong to this branch.

Prior art: reuse `checked-plant`'s bounded capture, process-group cleanup,
regular-file reader, failure formatter and atomic JSON publication. Its existing
behavior remains the compatibility contract. The two approved proposals favor
this extension over a new plugin or a launcher change.

1. Extract the common primitives, retaining checked-plant behavior. Resolve the
   conflict between module extraction and source-inspecting tests with TOOLING.
1. Add ordered checks, opaque argv and supervised staged pipelines, Git/input fingerprints, one
   guarded action, atomic receipts, independent verification and receipt rendering.
1. Add Scrut restart coverage and checked plants for the action, pipeline,
   fingerprint, completeness and verification boundaries.
1. Document the manifest and trust boundaries; bump plant-defects to 1.2.0 and
   rebuild generated mirrors.
1. Run the full local review order, planted boundary checks, Semgrep baseline,
   lint, locked full suite, version validation and exact-tree signed commit tidy.
1. Push and open a ready PR; report evidence and review rounds to TOOLING.

The action runs once only after every declared check has complete matching exit
and capture evidence and HEAD/tree/declared index and files remain unchanged.
Receipts bind checks to the pre-action tree; action mutations are recorded
separately. Verification rejects failed, incomplete, malformed or mismatched
receipts. Rendering quotes recorded exits, including refused and failed runs.
