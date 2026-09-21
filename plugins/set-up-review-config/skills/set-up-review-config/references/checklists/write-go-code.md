# Go Review Checklist

Applies to Go source and test files (`*.go`). Cite findings as `write-go-code: Rule name`.

## Important

- **Checked errors**: Every returned error is handled or returned. Discarding one with `_` needs a comment explaining why it cannot matter.
- **Wrapped errors**: An error passed up to callers that may inspect it is wrapped with `%w`, not `%v`, so `errors.Is` and `errors.As` keep working.
- **No panic for expected failures**: Invalid input, missing files and network failures return an `error`. `panic` is reserved for programming errors, impossible states and `init` failures.
- **In-band errors**: Failure is reported through an `error` or `ok` result, never through a special value such as `-1`, `""` or `nil`.
- **Goroutine exits**: Every new goroutine has an explicit exit path, such as a closed channel or a cancelled context. A goroutine that can block forever is a leak.
- **Loop variable capture**: When the `go` directive in `go.mod` is below 1.22, a goroutine closure started in a loop receives the loop variable as a parameter instead of capturing it.
- **Context first**: A function that performs I/O or can block takes `ctx context.Context` as its first parameter and passes it on. Contexts are never stored in struct fields, and `context.Background()` is created only in `main`, `init` and tests.
- **Deferred cleanup**: Files, response bodies, locks and connections are released with `defer` immediately after they are acquired successfully.
- **Safe type assertions**: A type assertion on a value that can hold another type uses the comma-ok form or a type switch.

## Nits

- **Error strings**: Lowercase unless they begin with a proper noun or acronym, no trailing punctuation, and they name the operation and the relevant identifiers.
- **Early return**: Errors and edge cases are handled first so the normal path stays unindented; no `else` after a branch that ends in `return`, `break` or `continue`.
- **Package names**: Short, lowercase, single word, and meaningful; not `util`, `common`, `misc`, `api` or `types`.
- **Initialisms**: One case per initialism: `URL`, `HTTP`, `ID`, `userID`, not `Url`, `Http` or `Id`.
- **No stutter**: Exported names do not repeat their package name, for example `config.Load`, not `config.LoadConfig`.
- **Getters**: No `Get` prefix, for example `Owner()`, not `GetOwner()`.
- **Receiver names**: One or two letters, the same across every method of a type, never `this` or `self`.
- **Name length follows scope**: Short names in small scopes, descriptive names for package-level identifiers.
- **Doc comments**: Every exported identifier has a full-sentence comment that begins with its name and ends with a period. A package comment sits directly above the `package` clause.
- **Interfaces at the consumer**: Interfaces are declared where they are used; constructors return concrete types. A single-method interface takes an `-er` name.
- **Nil slices**: `var s []T` instead of `s := []T{}`, unless an empty non-nil slice is required, such as JSON `[]`.
- **Keyed literals**: Struct literals of types from other packages name their fields.
- **Naked returns**: Only in functions of a few lines.
- **Synchronous APIs**: Functions return results directly and let callers add concurrency, instead of starting goroutines the caller cannot control.
- **Test failure messages**: Name the function and its input and show got before want, for example `Foo(%q) = %d, want %d`.
- **Table-driven tests**: Repeated cases use a table, with subtests where names help.
- **Error over Fatal**: Tests use `t.Error` and continue unless later checks depend on the failed one.
- **Cobra usage lines**: A runnable root command with subcommands shows one combined `[command] [flags]` usage line only when its `Use` has no positional arguments. Otherwise the root form and the subcommand form stay separate lines.

## Do not flag

- **Formatting**: Layout, brace placement and import grouping that `gofmt` or `goimports` produce.
- **Linter findings**: Anything a linter reports when that linter runs in CI, such as `go vet`, `staticcheck` or `golangci-lint`.
- **Generated code**: Files marked `// Code generated ... DO NOT EDIT.`.
- **Unexported identifiers**: Missing doc comments on unexported names.
- **Must functions**: A `MustX` helper that panics on failure, when it is used with constant input or during initialization.
