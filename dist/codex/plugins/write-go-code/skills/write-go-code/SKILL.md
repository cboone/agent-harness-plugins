---
name: write-go-code
description: >-
  Go code style guide based on Google Go Style Guide, Effective Go, Code Review
  Comments, and Cobra CLI behavior.
---

# Write Go Code

## Core Principles

1. **Clarity over cleverness** - Code should be obvious to readers
1. **Simplicity** - Accomplish goals in the most straightforward way
1. **Consistency** - Match surrounding code and project conventions
1. **Minimal indentation** - Handle errors early, keep happy path unindented

## Workflow

1. Run automated checks (`make lint`, `make fmt` or `gofmt`, `goimports`)
1. Review against essential checklist: `references/essential/checklist.md`
1. For specific questions, consult: `references/comprehensive/{topic}.md`
1. When creating or editing Cobra root commands, consult: `references/comprehensive/cobra.md`

## Reference Navigation

**Quick reviews (default):**

- `references/essential/checklist.md` - Condensed, actionable rules

**Deep dives by topic:**

- `references/comprehensive/naming.md` - Package names, identifiers, receivers
- `references/comprehensive/errors.md` - Error handling, panic/recover
- `references/comprehensive/concurrency.md` - Goroutines, channels, context
- `references/comprehensive/testing.md` - Test quality and patterns
- `references/comprehensive/code-organization.md` - Imports, packages, structure
- `references/comprehensive/data-types.md` - new vs make, slices, maps
- `references/comprehensive/functions.md` - Multiple returns, defer
- `references/comprehensive/interfaces.md` - Embedding, type assertions
- `references/comprehensive/makefile-conventions.md` - Required CI targets, fmt vs format
- `references/comprehensive/cobra.md` - Cobra root command usage templates

## Sources

- [Effective Go](https://go.dev/doc/effective_go)
- [Google Go Style Guide](https://google.github.io/styleguide/go/)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
