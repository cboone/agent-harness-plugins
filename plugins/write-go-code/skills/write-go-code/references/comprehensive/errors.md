# Error Handling

## Error Return Convention

- Error is always the **last return value**
- Return `nil` to signal success
- Use `error` type, not custom signal values

```go
// Good
func Load(path string) (*Config, error)

// Bad - in-band error
func Lookup(key string) string  // "" means not found?
```

## Error Strings

- **Lowercase**: Unless starts with proper noun/acronym
- **No trailing punctuation**: Errors are often wrapped
- **Include context**: Operation, relevant identifiers

```go
// Good
fmt.Errorf("open config: %w", err)
fmt.Errorf("user %q not found", username)

// Bad
fmt.Errorf("Open config failed.")
fmt.Errorf("User not found")
```

## Error Flow

Handle errors first, keep happy path unindented:

```go
// Good
f, err := os.Open(name)
if err != nil {
    return err
}
defer f.Close()
// continue with f...

// Bad
f, err := os.Open(name)
if err == nil {
    defer f.Close()
    // continue with f...
} else {
    return err
}
```

## Never Discard Errors

```go
// Bad - silent failure
result, _ := doSomething()

// Good - handle or return
result, err := doSomething()
if err != nil {
    return fmt.Errorf("do something: %w", err)
}
```

## Error Wrapping

Use `%w` to wrap errors for inspection with `errors.Is`/`errors.As`:

```go
if err != nil {
    return fmt.Errorf("load user %d: %w", userID, err)
}

// Caller can check:
if errors.Is(err, os.ErrNotExist) {
    // handle missing file
}
```

## Custom Error Types

For errors that need inspection:

```go
type PathError struct {
    Op   string
    Path string
    Err  error
}

func (e *PathError) Error() string {
    return e.Op + " " + e.Path + ": " + e.Err.Error()
}

func (e *PathError) Unwrap() error {
    return e.Err
}
```

## In-Band Errors

Avoid using special values to signal errors:

```go
// Bad - ambiguous
func Lookup(key string) int {
    if notFound {
        return -1  // Is -1 a valid value?
    }
    return value
}

// Good - explicit
func Lookup(key string) (int, bool) {
    if notFound {
        return 0, false
    }
    return value, true
}

// Also good
func Lookup(key string) (int, error) {
    if notFound {
        return 0, ErrNotFound
    }
    return value, nil
}
```

## Panic

**Don't use for normal errors.** Reserved for:
- Truly unrecoverable situations
- Programming errors (impossible states)
- Initialization failures in `init()`

```go
// Acceptable - impossible to continue
func MustCompile(pattern string) *Regexp {
    r, err := Compile(pattern)
    if err != nil {
        panic("regexp: Compile(" + pattern + "): " + err.Error())
    }
    return r
}

// Bad - recoverable error
func ReadFile(path string) []byte {
    data, err := os.ReadFile(path)
    if err != nil {
        panic(err)  // Should return error instead
    }
    return data
}
```

## Recover

Use sparingly to contain failures:

```go
func safeCall(f func()) (err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("panic: %v", r)
        }
    }()
    f()
    return nil
}
```

## Sentinel Errors

Define package-level errors for comparison:

```go
var (
    ErrNotFound   = errors.New("not found")
    ErrPermission = errors.New("permission denied")
)

// Usage
if errors.Is(err, ErrNotFound) {
    // handle not found
}
```
