# Go Style Essential Checklist

Quick reference for code reviews. For detailed guidance, see `../comprehensive/`.

## Formatting

- [ ] Code formatted with `gofmt`
- [ ] Imports organized with `goimports` (stdlib, external, local)
- [ ] Opening brace on same line as control statement

## Naming

- [ ] Package names: lowercase, single-word, no underscores
- [ ] Avoid meaningless names: `util`, `common`, `misc`, `api`, `types`
- [ ] Exported: `MixedCaps`; unexported: `mixedCaps`
- [ ] Initialisms consistent: `URL`, `HTTP`, `ID` (not `Url`, `Http`, `Id`)
- [ ] Receiver names: 1-2 letters, consistent across type (`c` for `Client`)
- [ ] Variable length proportional to scope (short for small scopes)
- [ ] No redundant naming (`File` not `ChubbyFile` in package `chubby`)
- [ ] Getters without "Get" prefix (`Owner()` not `GetOwner()`)
- [ ] Single-method interfaces: `-er` suffix (`Reader`, `Writer`)

## Error Handling

- [ ] Error strings: lowercase, no trailing punctuation

  ```go
  // Good
  fmt.Errorf("something failed")
  // Bad
  fmt.Errorf("Something failed.")
  ```

- [ ] All errors checked (no `_` discards without justification)
- [ ] Handle errors first, return early, keep happy path unindented

  ```go
  // Good
  if err != nil {
      return err
  }
  // continue with normal flow

  // Bad
  if err != nil {
      // error handling
  } else {
      // normal code
  }
  ```

- [ ] No in-band errors (`-1`, `""`, `nil` as error signals)
- [ ] Use `%w` for error wrapping: `fmt.Errorf("failed to load: %w", err)`
- [ ] No `panic()` for normal error handling

## Documentation

- [ ] Package comment adjacent to `package` clause (no blank line)

  ```go
  // Package config handles configuration loading.
  package config
  ```

- [ ] Doc comments: full sentences, start with name, end with period

  ```go
  // Load reads configuration from the specified path.
  func Load(path string) (*Config, error)
  ```

- [ ] All exported names documented

## Control Structures

- [ ] Omit `else` when `if` body ends in `return`, `break`, `continue`
- [ ] Use `range` for iteration
- [ ] Comma-separated switch cases (not fallthrough): `case 'a', 'b', 'c':`
- [ ] Type switches: `switch t := x.(type)`

## Data Types

- [ ] `new` for zero-value allocation; `make` for slices/maps/channels

  ```go
  p := new(Config)           // *Config, zeroed
  s := make([]int, 10)       // []int, length 10
  m := make(map[string]int)  // map, initialized
  ```

- [ ] Nil slices preferred: `var t []string` not `t := []string{}`
- [ ] Composite literals with field names for clarity

  ```go
  // Good
  return &File{fd: fd, name: name}
  // Fragile (breaks if fields reordered)
  return &File{fd, name, nil, 0}
  ```

- [ ] Comma-ok idiom for map lookups when needed

  ```go
  if val, ok := m[key]; ok {
      // key exists
  }
  ```

## Functions

- [ ] Multiple return values for errors
- [ ] Named return parameters when same type repeated or for documentation
- [ ] `defer` for cleanup (files, mutexes, connections)

  ```go
  f, err := os.Open(name)
  if err != nil {
      return err
  }
  defer f.Close()
  ```

- [ ] Avoid naked returns in functions longer than a few lines

## Concurrency

- [ ] Context as first parameter: `func Foo(ctx context.Context, ...)`
- [ ] Goroutine lifetimes explicit and documented
- [ ] Prefer synchronous functions (callers can add concurrency)
- [ ] Don't store Context in structs; pass as parameter

## Interfaces

- [ ] Define interfaces where used, not where implemented
- [ ] Return concrete types; let consumers define interfaces
- [ ] Type assertions use comma-ok: `str, ok := value.(string)`
- [ ] Embed to compose, not inherit

## Testing

- [ ] Failures include: function name, inputs, got, want

  ```go
  if got != want {
      t.Errorf("Foo(%q) = %d, want %d", input, got, want)
  }
  ```

- [ ] Format: `got != want` (actual before expected)
- [ ] Table-driven tests for multiple cases
- [ ] Prefer `t.Error` over `t.Fatal` when possible

## Code Organization

- [ ] Import groups: stdlib, blank line, external, blank line, local
- [ ] No import renaming unless collision
- [ ] Pass values, not pointers, for small immutable data
- [ ] Receiver type consistent across all methods of a type

## CLI Commands

- [ ] Cobra root commands with both `Run`/`RunE` and subcommands set a combined usage template so help shows one line: `myapp [command] [flags]`
