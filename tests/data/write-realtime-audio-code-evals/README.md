# Write Real-Time Audio Code Evaluations

These repository-only cases evaluate the published skill's discovery, reference navigation, and recommendations. They are not part of the installed plugin and do not assert that an audio program or instrument was executed.

## Layout

- `inputs.json` contains fresh-context requests and minimal raw artifacts. It intentionally omits expected conclusions and suspected defects.
- `assessment-criteria.md` contains the separate expected recommendation, evidence, and scope limits for each stable case ID.
- `assessment.md` is the single living record of evaluations performed against a named skill revision.

## Procedure

1. Create an isolated temporary workspace for each run.
1. Give the evaluator only one input variant, the installed skill, and its local references. Do not provide assessment criteria or earlier conclusions.
1. Record the harness and model, skill revision, selected references, resulting recommendation or artifacts, and observed command completions in `assessment.md`.
1. Compare the result with the matching criterion. Record a pass, a shortfall, or unverified. A requested experiment is not a completed experiment.
1. Repeat discovery and navigation cases against the generated Codex and OpenCode layouts. Do not infer that a repository-relative companion path works in an installed copy.

Use an available supported harness. If one is unavailable, leave a case unverified rather than substituting a source-text review for an execution result.
