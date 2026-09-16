# Write Real-Time Audio Code Evaluations

These repository-only cases evaluate the published skill's discovery, reference navigation, and recommendations. They are not part of the installed plugin and do not assert that an audio program or instrument was executed.

## Layout

- `inputs.json` maps each fresh-context request to opaque artifact IDs. `artifacts.json` contains the associated source snippets, serialized state, traces, logs, and build records. The evaluator receives only the selected artifacts, never the criteria or a prior conclusion.
- `assessment-criteria.md` contains the separate expected recommendation, evidence, and scope limits for each stable case ID.
- `assessment.md` is the single living record of evaluations performed against a named skill revision.

## Procedure

1. Create an isolated temporary workspace for each run.
1. Copy only one input variant's selected artifacts, the installed skill, and its local references into that workspace. For RTAC-029, the operator also provisions the installed `plant-defects` skill and its bundled references before starting the evaluator, and registers both skills through the harness's supported discovery mechanism. Verify that the evaluator can discover and read the companion; an artifact claiming it is installed is insufficient. This setup does not authorize the evaluator to install tools, mutate the target, commit, or publish. RTAC-030 must expose only the audio skill and its local references, with the companion absent. Submit the selected variant's `request` field from `inputs.json` as the evaluator's task prompt. Do not provide assessment criteria, unrelated artifacts, or earlier conclusions.
1. Record the harness and model, skill revision, selected references, resulting recommendation or artifacts, and observed command completions in `assessment.md`. For RTAC-029, also record the companion revision and discovery verification. If the harness cannot expose the installed companion, leave that case unverified.
1. Compare the result with the matching criterion. Record a pass, a shortfall, or unverified. A requested experiment is not a completed experiment.
1. Repeat discovery and navigation cases against the generated Codex and OpenCode layouts. Do not infer that a repository-relative companion path works in an installed copy.

Use an available supported harness. If one is unavailable, leave a case unverified rather than substituting a source-text review for an execution result.
