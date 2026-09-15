# Deferral Signals

How to recognize a concern that a unit of work set aside, and how to tell it apart from the many things that only look like one.

## What a Deferral Is

A deferral has two parts, and needs both:

1. **A concrete concern**: something specific that is wrong, missing, or worth changing, stated clearly enough that someone could act on it.
1. **A decision not to act on it in this work**: stated by either side of the conversation, or implied by where it sits, such as an out-of-scope section of a plan.

A concern with no decision is still open in the current work and belongs to it, not to a new issue. A decision with no concrete concern ("there is probably more to clean up later") gives nobody anything to act on. Neither half alone is proposed.

## Phrasings

A phrase is evidence, never a verdict. "The parser is out of scope for this module, which only tokenizes" describes a design boundary, not a deferred concern. Read the sentence around the phrase.

### Setting a concern aside

| Phrasing                           | Example shape                                                           |
| ---------------------------------- | ----------------------------------------------------------------------- |
| "out of scope"                     | "The retry path has the same flaw, but fixing it is out of scope here." |
| "worth filing"                     | "Worth filing: no CI job runs the formatter."                           |
| "follow-up"                        | "A follow-up could lower the job timeouts to match real run lengths."   |
| "should be tracked separately"     | "The flaky snapshot should be tracked separately."                      |
| "left open"                        | "I have left the pagination question open."                             |
| "not addressed here"               | "The Windows path handling is not addressed here."                      |
| "a separate concern"               | "Certificate expiry is a separate concern from the clamping fix."       |
| "deferred to"                      | "Deferred to the release work."                                         |
| "beyond this PR", "a separate PR"  | "Renaming the module is beyond this PR."                                |
| "pre-existing and unrelated"       | "The lint warning is pre-existing and unrelated to this change."        |
| "known limitation, not fixed here" | "Large repositories time out; a known limitation, not fixed here."      |

### Parking a concern

The user's side of the conversation defers too: "not now", "leave that for later", "park that", "let's not do that in this PR", "we can come back to that".

A request to file something ("file an issue for that", "create an issue to take care of the timeouts") that was not yet acted on is a deferral. One that was already acted on is tracked.

## Source Shapes

### Code markers

`TODO`, `FIXME`, `XXX`, and `HACK` count when they open a comment or are followed by `:` or `(`, as in `// TODO: handle an empty list` or `# FIXME(perf): quadratic`. A prose mention of the word ("no TODO markers remain") is not a marker.

A marker that already names an issue, such as `TODO(#123)`, is tracked.

### Review comments

- A reply that sets a finding aside: "Good catch, but out of scope for this PR."
- A review-feedback summary whose table carries a Deferred category. A Deferred row that names an issue is tracked. One tracked only in a project notes file, or not tracked at all, is a candidate.

### Documents

Plans, review documents, and issue bodies hold deferrals under headings such as `Out of scope`, `What this does not close`, `Follow-ups`, `Future work`, and `Deferred`.

`Non-goals` and `Open questions` qualify entry by entry. An entry left for later work qualifies ("Windows paths: a follow-up once the Unix path is stable"). An entry that only draws a boundary ("No Windows support") or is still being decided does not.

## Not Deferrals

| Looks like                                        | Why it is not proposed                            | Example shape                                                                   |
| ------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------- |
| A hedge or speculation                            | No decision, and often no concrete concern        | "One option would be to cache the parsed config."                               |
| An alternative considered and rejected            | A design decision, not pending work               | "A global flag was considered and dropped because it hid per-file errors."      |
| A concern resolved later in the work              | Already done                                      | The agent flags missing input validation, and a later commit adds it            |
| A concern the user declined                       | Declined is not deferred                          | "Don't worry about the branch name."                                            |
| A generic caveat                                  | Nothing to act on                                 | "This could be slow on very large repositories."                                |
| A template placeholder                            | Part of a template, not a concern                 | The `TODO: describe how to verify` line in a PR body template                   |
| A marker in generated, vendored, or fixture files | Not authored in this work, or present on purpose  | A `TODO` inside a vendored library, or in a fixture that tests marker detection |
| A marker in documentation about markers           | Illustrates syntax                                | A style guide showing the house `TODO(name):` form                              |
| An unchecked item of the issue being worked on    | This branch's own remaining work, not a new issue | A `- [ ] Update the README` checkbox in the source issue                        |
| A concern already filed                           | Tracked                                           | "Filed #412 for the claim-file drift."                                          |

## Worked Examples

1. **Session**: "The lint workflow never runs shfmt, so scripts can merge unformatted. That is outside this change." A concrete concern and a decision. Propose "Run shfmt in the lint workflow".
1. **Session**: "Every job sets a 20-minute timeout, though the runs finish in under a minute. I have left those alone." Propose "Lower CI job timeouts to match real run lengths".
1. **User**: "Record the clamping and file an issue to create new certs." Later, the clamping is recorded in the plan, but no issue exists. The certificates are a deferral; the clamping was done and is not.
1. **Session**: "One option would be to memoize the parser." A hedge. Not proposed.
1. **Session**: the agent notes a missing nil check, and two commits later the branch adds it. Resolved. Not proposed.
1. **User**: "Don't worry about the stale branch name." Declined. Not proposed.
1. **Inline review comment** on pagination, answered "Valid, but out of scope for this PR." Propose it, with the review comment as the source link.
1. **Session**: "The shared CI actions pin an old runner image; that belongs in owner/ci-actions, not here." Propose it against `owner/ci-actions`, marked third-party when that owner differs from origin's.
1. **Plan**, under `Out of scope`: "Migrating the remaining scripts, tracked in #57." Tracked. Not proposed.

## Target Repository Signals

A deferral targets another repository only when it identifies one:

- An `owner/name`, a `HOST/OWNER/NAME` selector, or a GitHub repository URL.
- A name the session already tied to a specific repository, such as "the plugins repo" after the session had established which repository that is.

A description with no identification ("the upstream library", "the shared config") is unresolved. Propose the candidate with its target marked unresolved and let the user supply it, rather than guessing.
