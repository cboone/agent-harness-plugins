# Aspects

Each aspect is one focused review, adapted from an agent in `pr-review-toolkit` (Apache-2.0; see the plugin's `NOTICE`). Its instructions live in `./aspects/<name>.md`, and `codex-aspects prompt` combines them with the scope and the output contract.

| Aspect     | Source agent            | Instructions            | Applies when                                        |
| ---------- | ----------------------- | ----------------------- | --------------------------------------------------- |
| `code`     | `code-reviewer`         | `./aspects/code.md`     | Always                                              |
| `errors`   | `silent-failure-hunter` | `./aspects/errors.md`   | Error handling was added or changed                 |
| `tests`    | `pr-test-analyzer`      | `./aspects/tests.md`    | Tests, or behavior that tests should cover, changed |
| `comments` | `comment-analyzer`      | `./aspects/comments.md` | Comments or documentation were added or changed     |
| `types`    | `type-design-analyzer`  | `./aspects/types.md`    | Types were added or changed                         |
| `simplify` | `code-simplifier`       | `./aspects/simplify.md` | Last, and only when the review allows it            |

## Arguments

- Omitted arguments or `all` select review aspects except `simplify`; step 2 drops inapplicable aspects.
- Named aspects select exactly those, in any order, and each runs even when the criteria below would skip it.
- Review names added to `all` do not change its selection. Explicit `simplify` authorizes the later editing pass. `simplify` alone is rejected; use `all simplify` or include at least one review aspect.
- An unknown name stops the skill before any review runs: report it and list the valid names. Do not guess what was meant.

## Deciding what applies

Read the diff of every bucket in the scope, not only the file names. When unsure, run the aspect: a review that finds nothing costs one run, while a skipped one leaves an area unread.

- **`errors`**: the change adds or alters a try/catch or try/except block, an error return or `Result`, an error callback, a fallback or default used on failure, retry logic, or optional chaining or null coalescing on an operation that can fail. In shell, also `|| true`, `2> /dev/null`, `set +e`, unchecked exit statuses and `trap`.
- **`tests`**: test files changed, or code changed whose behavior tests should pin, which is most logic changes. A change only to documentation, comments or configuration that no test exercises does not qualify.
- **`comments`**: code comments, docstrings, or documentation files such as READMEs and Markdown references were added or changed. A change that leaves comments next to changed code untouched also qualifies when those comments may now be wrong.
- **`types`**: a type, class, struct, interface, enum, schema or other data definition was added or its fields or invariants changed. A change that only uses existing types does not qualify.
- **`simplify`**: selected explicitly by name only, then gated by step 6 of the workflow. It never runs alongside the review aspects.

Record every aspect left out, with the specific reason, for the report's **Aspect runs** table.
