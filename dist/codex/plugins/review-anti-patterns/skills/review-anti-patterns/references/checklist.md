# Anti-pattern checklist

Thirteen defect patterns that most often get past a general local review and come back as Copilot findings in later rounds, written as the questions a reviewer asks. They come from a review of 132 pull requests and about 500 Copilot reviews, in which the patterns below accounted for most findings after round 1, and most of those findings were in code or text that the previous fix had just added.

Each item names the groups it applies to (code, agent prose, docs), the questions to ask, what settles them, and an example. Cite an item by its heading in a finding's title, for example `Sibling input forms: …`.

## Code

### Sibling input forms

**Applies to:** code, and agent prose that tells an agent which inputs to reject.

A blocklist, regular expression or sanitizer rejects one form of an input and accepts its siblings.

- For each input form the change rejects or rewrites, what sibling forms exist? Consider encodings (percent, HTML entity, Unicode escapes and normalization), case, whitespace runs and other separators, CRLF and bare CR, IPv6 and numeric host forms, trailing dots and slashes, `..` after decoding, and symlinked parents.
- Does the check run before or after decoding, normalization and path resolution?
- Write the input grammar as a matrix and test every cell. For key and value redaction that is key quoting (none, `"`, `'`, escaped `\"`), separator (`=` or `:`, with and without surrounding spaces), value quoting and encoding; for an identifier, every separator the outer pattern admits. One cell fixed per round is how a chain of findings starts.
- A form the code documents as deliberately left alone is still a candidate. Can it carry the value the check protects?
- Would an allowlist of exact known-good forms, or a structural parse (a URL parser, a path resolver, a real tokenizer), remove the whole class instead of one member of it?
- When the range is the second or later fix to the same check, report replacing it with an exact-format allowlist or a structural parse as an Important finding of its own, whatever else the review finds. Another patch to the same blocklist is what the next round would answer.

**Settled by:** a sibling input traced through the code to the point where it is accepted, or the check shown to apply to a canonical form that every sibling reduces to.

**Example:** a path-safety check that went through 19 review rounds, each finding a new bypass: `..` after percent-decoding, a symlinked parent directory, a trailing separator. A log redactor patched one client ID format at a time for 14 rounds, until it logged IDs only when they matched their exact known formats.

### Boundary arithmetic

**Applies to:** code.

Time windows, ranges, cursors and pagination leave a gap, overlap or off-by-one at an edge.

- Is each bound inclusive or exclusive, and do adjacent windows agree, so that an event exactly on the boundary is counted once?
- What happens at the first and last element, a range of length zero or one, a date at midnight, a time zone or daylight-saving change, and the end of a month?
- Does a cursor or offset advance past the last item it read, and not past one it skipped?

**Settled by:** the boundary value worked through by hand, showing where it lands.

**Example:** two consecutive report windows that both used `<=` on their end time, so a run at exactly midnight counted in both.

### Stale writes

**Applies to:** code, and agent prose that writes shared state.

A late retry, a slow worker or a second session overwrites newer state, or a check and the action that relies on it are separated.

- Between reading a value and writing a decision based on it, can anything else change it? Is the write conditional on the value still being what was read (an ETag, a compare-and-swap, a `--match-head-commit`)?
- Can a retry of an older request land after a newer one and win?
- Is a file checked, then opened, in a way another process can change in between?

**Settled by:** an interleaving of two actors that produces the wrong final state, or the guard that prevents it.

**Example:** a status update retried after a timeout overwrote the newer status that a later run had already written.

### Validator gaps

**Applies to:** code.

A validator accepts input that has the right outer shape but is semantically invalid.

- Does it check nested objects, or only the top level? Unknown keys at depth, wrong types inside arrays, duplicate keys, empty strings where a value is required?
- Does it reject values that parse but cannot be right: a future timestamp for a past event, a negative count, an end before a start?
- Is the validator an allowlist of what the reader actually uses, or a blocklist of known-bad shapes?

**Settled by:** an input that passes the validator, traced to where the reader misbehaves on it.

**Example:** a stub that treated any response containing the string `errors` as a GraphQL error, so a nested field named `errors` inside the data failed the call. The fix checked only the top-level `errors` key.

### Absent or partial data

**Applies to:** code, and agent prose that reads tool or API output.

Missing, empty, truncated or paginated input is treated as a clean pass.

- What does this return for missing input, an empty list, the first page of several, a response cut off at a limit, and a response with an error field beside its data?
- Can "nothing found" be told apart from "nothing read"? Does a zero count, an empty file or a failed command reach the same branch as success?
- When a list is capped (`first: 100`, `--limit`, a search's 1,000-result ceiling), is reaching the cap detected and reported?
- When one part of the work fails, such as an extractor that raises, do the parts that do not depend on it, such as a status or result code, still get written?

**Settled by:** the empty or partial input traced to the result it produces.

**Example:** a report that printed a table of zeros when its search failed, because the failed search and an empty one produced the same empty array.

### Untrusted data in commands

**Applies to:** code, and agent prose that builds commands from external text.

Data from outside the trust boundary reaches a shell, a log, an email, an argument vector or a workflow command.

- Where does each interpolated value come from? A pull request title, branch name, issue body, file name, environment variable from a fork, or API response is untrusted.
- Is it passed as a separate argument or quoted for its destination, or spliced into a string that is then parsed? Can a leading `-` turn it into an option?
- In a GitHub Actions workflow, does `${{ … }}` expand untrusted text directly into a `run:` script?
- In a log or email, can newlines or control characters forge a second line or a header?

**Settled by:** the value traced from its source to the sink, with the escaping or argument boundary that applies, or its absence.

**Example:** a path argument that began with `-` was read as an option by `cat` and `dirname` until both calls gained `--`.

### Tests that cannot fail

**Applies to:** code.

A test passes whatever the code does, does not run, or depends on state another test leaves behind.

- If the code under test were broken in the way this test claims to catch, would the test go red? Does it assert on the output, or only that a command ran?
- Is the test registered where the runner finds it, and does the runner's output show it ran?
- Does it share fixtures, temporary files or environment with other tests in a way that makes order matter?

**Settled by:** the defect the test claims to catch, planted and observed to turn it red, or the reason it cannot. When planting is not possible inside a read-only review, report the test as unverified and suggest the `plant-defects` skill.

**Example:** a fixture reused by two tests, so the second passed only because the first had already written the file it read.

### Crashes instead of reports

**Applies to:** code.

A wrong value from a user or a file produces a stack trace or a bare interpreter error instead of a message naming the problem.

- For each value read from arguments, environment, configuration or a file: what happens when it is missing, empty, the wrong type, or out of range?
- Does the error name the value, where it came from and what was expected?

**Settled by:** the bad value traced to the line that raises.

**Example:** a date option passed straight to a parser, so `--since yesterday` ended in a parser traceback rather than "--since must be YYYY-MM-DD".

### Unrun platform configuration

**Applies to:** code, and docs that give commands.

Configuration or commands that have never been run against the real platform: workflow syntax, cloud CLI flags, API field names, query shapes.

- Has this configuration been validated by the platform's own tool, or only read?
- Does every flag, field and enum value exist in the version the project targets?
- Has each documented command been run once, exactly as written?

**Settled by:** the platform's validator or a read-only run, per `./mechanical-checks.md`, or a citation to the platform's documentation for the exact field.

**Example:** a workflow that referenced an output by a name its step never set, which parsed as YAML and failed only when the job ran.

### Unenforced trust boundary

**Applies to:** code and agent prose.

The change claims a boundary, such as "read-only", "least privilege", "never pushes" or "sandboxed", that nothing enforces.

- What mechanism enforces the claim: a token's permissions, a sandbox flag, a disallowed-tools list, a filesystem permission? Or only the instructions?
- Can any path through the code or the workflow cross the boundary, such as a fallback, an error handler or a helper that writes?
- Does an agent or reviewer instruction tell a reviewer not to raise something? That is a claim to verify like any other, and behavior that depends on import order or registration order is unverified until a test pins the order that ships.

**Settled by:** the enforcing mechanism named and checked, or the path that crosses the boundary.

**Example:** a workflow described as read-only whose job-level `permissions` block granted `contents: write`.

## All groups

### Parallel paths

**Applies to:** code, agent prose and docs.

A change updates one of several places that do the same job and leaves the others behind.

- Which other places do the same thing: another branch of the same `case`, a second implementation of the same format, a byte-identical mirror copy, a generated file, a test fixture, a caller, a sibling skill that shares the rule?
- Did every one of them change, or is there a reason one should not?
- Did the fix for a review finding land in only the one place the finding named?
- When a fix changes the order or preprocessing of one rule in a pipeline, such as moving it before decoding, every other rule in that pipeline is a sibling: does each still see the input it expects?
- For an allowlist, registry or route table, list the full set it is meant to cover, such as every public write route, and compare it with its entries. For a lookup by path or key, which spellings of the same request reach it: trailing slash, case, encoding?

**Settled by:** a repository search for the shared identifier, flag, message or literal, with each hit checked.

**Example:** a new author option accepted `@me` and plain logins, and a later fix to validate it rejected the `app/NAME` bot form that the search itself accepted.

## Agent prose

### Agent-prose control flow

**Applies to:** agent prose.

Read a skill, command or prompt as a program. An agent follows it in order and takes the first instruction that fits.

- Does each rule appear before the step that needs it, not after it or only in a reference file the step does not point to?
- Does every branch end in a defined status or next step? Trace each condition (success, failure, empty result, missing tool, user declines) to where it ends.
- Do two rules, in this file or across files the agent loads together, tell it to do different things in the same situation? Which one wins, and does the text say so?
- Do the commands the skill runs match its permission block, recommended permissions or allowed tools?
- Does a required dependency get checked before the first side effect that needs it?

**Settled by:** the path through the text quoted step by step, from the triggering condition to the point where it goes wrong.

**Example:** a skill that said "never push" in its key conventions, after a workflow step that told the agent to push the fix.

## Docs

### Docs drift

**Applies to:** every scope.

Docs, plans, READMEs, help text, comments or the pull request body disagree with the code, or with each other.

- List each identifier, flag, default, count, path, status name and stated behavior the change touched. Where else is each one described?
- Does each description still match? Check the README, the help text, plans, comments next to the code, and the pull request body.
- Do two documents now describe the same behavior differently?

**Settled by:** the document's sentence quoted beside the code or the other document it disagrees with.

**Example:** a script's warning said "1 pull requests" until its warnings agreed in number with their counts, and its README still described the earlier wording.
