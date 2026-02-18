# Testing

## Test Failure Messages

Include enough information to debug without re-running:

```go
// Good - includes function, input, got, want
if got != want {
    t.Errorf("Reverse(%q) = %q, want %q", input, got, want)
}

// Bad - unhelpful
if got != want {
    t.Error("wrong result")
}
```

## Got Before Want

Convention: actual value before expected:

```go
// Good
t.Errorf("Add(2, 3) = %d, want %d", got, want)

// Confusing
t.Errorf("want %d, got %d", want, got)
```

## Table-Driven Tests

For multiple test cases:

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"positive", 2, 3, 5},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```

## Error vs Fatal

- **t.Error/Errorf**: Test continues; use when subsequent checks are meaningful
- **t.Fatal/Fatalf**: Test stops; use when further checks would be invalid

```go
// Use Fatal for setup failures
f, err := os.Open(testFile)
if err != nil {
    t.Fatalf("failed to open test file: %v", err)
}

// Use Error for test assertions (allows multiple failures)
if got != want {
    t.Errorf("got %v, want %v", got, want)
}
```

## Comparison

Use `cmp` package for complex comparisons:

```go
import "github.com/google/go-cmp/cmp"

if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("mismatch (-want +got):\n%s", diff)
}
```

## Test Helpers

Mark functions as helpers for better error locations:

```go
func assertNoError(t *testing.T, err error) {
    t.Helper()  // Error points to caller, not this line
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
}
```

## Example Functions

Runnable examples appear in documentation:

```go
func ExampleReverse() {
    fmt.Println(Reverse("hello"))
    // Output: olleh
}
```

## Test Organization

- Test files: `foo_test.go` alongside `foo.go`
- Test functions: `TestFunctionName`
- Benchmark functions: `BenchmarkFunctionName`
- Example functions: `ExampleFunctionName`

```go
// foo_test.go
package foo

func TestBar(t *testing.T) { ... }
func BenchmarkBar(b *testing.B) { ... }
func ExampleBar() { ... }
```

## Avoid Assertion Libraries

Use standard library; write explicit checks:

```go
// Good - clear and explicit
if got != want {
    t.Errorf("got %v, want %v", got, want)
}

// Avoid - hides what's being tested
assert.Equal(t, want, got)
```

## Test Data

Use `testdata` directory (ignored by Go tools):

```text
package/
  foo.go
  foo_test.go
  testdata/
    input.txt
    expected.txt
```

## Cleanup

Use `t.Cleanup` for deferred cleanup:

```go
func TestWithTempFile(t *testing.T) {
    f, err := os.CreateTemp("", "test")
    if err != nil {
        t.Fatal(err)
    }
    t.Cleanup(func() { os.Remove(f.Name()) })
    // test using f...
}
```

## Parallel Tests

Mark independent tests for parallel execution:

```go
func TestA(t *testing.T) {
    t.Parallel()
    // ...
}

func TestB(t *testing.T) {
    t.Parallel()
    // ...
}
```
