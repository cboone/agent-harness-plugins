# Choosing a Board

A board costs more than an answer. It has a URL to keep, a sync to repeat, and a page that misleads once nobody re-syncs it. It repays that cost only when the analysis has all three of these properties.

| Property                     | Ask                                                   | A board when                                               | The terminal when                                      |
| ---------------------------- | ----------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------ |
| Re-run against changing data | Will this answer be wrong after the next merge?       | Issues open and close, branches land, and the answer moves | The data is settled, or the question is about the past |
| Scanned, not read            | Does the reader want "what do I do next" at a glance? | The reader returns to pick the next item                   | The reader wants an explanation or an argument         |
| Kept open                    | Will someone consult it more than once?               | It is a working surface for days or weeks                  | It answers one question and is done                    |

With all three, a board is warranted. Missing any one, answer in the terminal and say why in a sentence, for example: "This is a one-time answer, so here it is rather than a board."

## Signals

A request for a board is a strong signal but not a sufficient one. These make the case:

- The same analysis has already been derived more than once in the session, or the user says they will ask again.
- Several people, or several parallel sessions, need the same picture at the same time.
- The analysis has a natural cadence: after each merge, each morning, each release.

These argue against:

- The user asked a question with a single answer, such as "which issue should I do next".
- The source data will not change before the reader acts on the answer.
- The analysis is an argument that must be read in order, such as a design review.

## Compose, Do Not Re-derive

A board publishes an analysis; it is not a second analysis engine. When an installed skill already produces part of the analysis, use its method rather than inventing another. The `suggest-next-issue` skill already detects work in progress and weighs issues by priority, dependencies, age, and activity, and the backlog board reuses both. The board type's reference names what the board adds on top.

## One Board per Question

Keep one board per repository and board type. A second board for the same question splits the reader's attention and guarantees that one of the two goes stale. When the user asks for a variant, such as a filtered subset, put it on the existing board only if every reader benefits; otherwise answer the variant in the terminal.
