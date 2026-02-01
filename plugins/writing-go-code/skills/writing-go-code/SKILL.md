---
name: writing-go-code
description: Go code style guide based on Google Go Style Guide, Effective Go, and Code Review Comments. Use when: (1) writing new Go code, (2) reviewing Go code for style compliance, (3) refactoring existing Go code, (4) conducting code reviews. Covers naming, error handling, concurrency, testing, data types, functions, interfaces, and code organization.
---

# Writing Go Code

## Core Principles

1. **Clarity over cleverness** - Code should be obvious to readers
2. **Simplicity** - Accomplish goals in the most straightforward way
3. **Consistency** - Match surrounding code and project conventions
4. **Minimal indentation** - Handle errors early, keep happy path unindented

## Workflow

1. Run automated checks (`make lint`, `make fmt` or `gofmt`, `goimports`)
2. Review against essential checklist: `references/essential/checklist.md`
3. For specific questions, consult: `references/comprehensive/{topic}.md`

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

## Sources

- [Effective Go](https://go.dev/doc/effective_go)
- [Google Go Style Guide](https://google.github.io/styleguide/go/)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
