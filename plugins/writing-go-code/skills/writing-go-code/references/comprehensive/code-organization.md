# Code Organization

## Formatting

**Always use `gofmt`** - no exceptions. It handles:
- Indentation (tabs)
- Alignment
- Spacing

**Use `goimports`** - superset of gofmt that also manages imports.

## Import Organization

Group imports with blank lines between groups:

```go
import (
    // Standard library
    "context"
    "fmt"
    "os"

    // External packages
    "github.com/spf13/cobra"
    "github.com/spf13/viper"

    // Local packages
    "github.com/yourorg/project/internal/config"
    "github.com/yourorg/project/internal/output"
)
```

## Import Renaming

**Avoid unless necessary** for collisions:

```go
// Avoid
import (
    c "context"
    f "fmt"
)

// Acceptable - collision
import (
    "crypto/rand"
    mathrand "math/rand"
)
```

## Import for Side Effects

Use blank identifier; only in main or tests:

```go
import _ "net/http/pprof"  // Registers HTTP handlers
```

## Import Dot

**Never use** except in tests with circular dependencies:

```go
// Avoid - obscures code origin
import . "fmt"
Println("hello")  // Where does Println come from?
```

## Package Comments

Adjacent to package clause, no blank line:

```go
// Package config handles application configuration loading
// and validation from multiple sources.
package config
```

For `package main`:
```go
// Command bopca runs Claude Code in containers.
package main
```

## File Organization

Typical order within a file:

1. Package comment and clause
2. Imports
3. Constants
4. Package-level variables
5. Types
6. Constructor functions (`New...`)
7. Methods (grouped by receiver type)
8. Helper functions
9. `init()` function (if needed)

## Nil Slices

Prefer nil slice declaration:

```go
// Good - nil slice
var names []string

// Avoid - non-nil empty slice
names := []string{}
```

Exception: JSON encoding (nil becomes `null`, empty becomes `[]`).

## Pass Values vs Pointers

**Pass values** for small, immutable data:
```go
// Good - strings are small
func greet(name string) string

// Good - small struct
func distance(p1, p2 Point) float64
```

**Pass pointers** when:
- Function needs to modify the value
- Value is large (benchmark if unsure)
- Value contains sync primitives

```go
// Pointer needed - modifies receiver
func (c *Counter) Increment()

// Pointer needed - large struct
func processLargeData(data *LargeStruct)
```

## Interfaces

**Define where used**, not where implemented:

```go
// Good - consumer defines interface
package consumer

type DataFetcher interface {
    Fetch(ctx context.Context, id string) ([]byte, error)
}

func Process(fetcher DataFetcher) error {
    // ...
}

// Bad - producer exports interface
package producer

type Fetcher interface {
    Fetch(ctx context.Context, id string) ([]byte, error)
}

type HTTPFetcher struct{}
func (f *HTTPFetcher) Fetch(...) ([]byte, error) { ... }
```

**Return concrete types** from constructors:

```go
// Good
func NewHTTPClient() *HTTPClient

// Avoid
func NewHTTPClient() Client
```

## Line Length

No rigid limit. Guidelines:
- Don't break lines arbitrarily to stay under N characters
- Break at semantic boundaries
- Long lines often indicate need for refactoring
- Extract complex expressions into named variables

```go
// Acceptable long line
result, err := client.FetchUserDataWithRetry(ctx, userID, maxRetries, retryDelay)

// Better if too long - extract variables
opts := FetchOptions{MaxRetries: 3, Delay: time.Second}
result, err := client.FetchUserData(ctx, userID, opts)
```

## Semicolons

Go inserts semicolons automatically. Key rule:
- Opening brace must be on same line as control statement

```go
// Good
if condition {
    // ...
}

// Won't compile - semicolon inserted after condition
if condition
{
    // ...
}
```
