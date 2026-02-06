# Concurrency

## Core Principle

> Do not communicate by sharing memory; instead, share memory by communicating.

Use channels to pass data between goroutines rather than shared variables with locks.

## Context

**Always pass as first parameter:**
```go
func DoSomething(ctx context.Context, arg string) error
```

**Never store in structs:**
```go
// Bad
type Server struct {
    ctx context.Context
}

// Good - pass to methods
func (s *Server) Handle(ctx context.Context, req *Request) error
```

**Create base contexts only in main or tests:**
```go
func main() {
    ctx := context.Background()
    // ...
}
```

## Goroutines

**Prefix function call with `go`:**
```go
go processRequest(req)

// With closure
go func() {
    result := compute()
    results <- result
}()
```

**Closures capture variables by reference:**
```go
// Bug - all goroutines see final value of i
for i := 0; i < 10; i++ {
    go func() {
        fmt.Println(i)  // Likely prints "10" ten times
    }()
}

// Fix - pass as parameter
for i := 0; i < 10; i++ {
    go func(n int) {
        fmt.Println(n)
    }(i)
}
```

## Goroutine Lifetimes

**Make exit conditions explicit.** Goroutines that block forever leak.

```go
// Bad - how does this goroutine exit?
go func() {
    for req := range requests {
        process(req)
    }
}()

// Good - clear exit via channel close
func worker(ctx context.Context, requests <-chan Request) {
    for {
        select {
        case req, ok := <-requests:
            if !ok {
                return  // Channel closed
            }
            process(req)
        case <-ctx.Done():
            return  // Context cancelled
        }
    }
}
```

## Channels

**Unbuffered** - synchronizes sender and receiver:
```go
ch := make(chan int)
```

**Buffered** - sender blocks only when full:
```go
ch := make(chan int, 100)
```

**Signal completion:**
```go
done := make(chan struct{})
go func() {
    defer close(done)
    // do work
}()
<-done  // Wait for completion
```

**Range over channel:**
```go
for msg := range messages {
    process(msg)
}
// Loop exits when channel is closed
```

## Select

Multiplex channel operations:

```go
select {
case msg := <-messages:
    handle(msg)
case <-ctx.Done():
    return ctx.Err()
case <-time.After(timeout):
    return ErrTimeout
default:
    // Non-blocking: runs if no other case ready
}
```

## Synchronous vs Asynchronous

**Prefer synchronous functions.** Callers can add concurrency:

```go
// Good - synchronous
func Process(data []byte) ([]byte, error) {
    // process and return
}

// Caller adds concurrency if needed
go func() {
    result, err := Process(data)
    // ...
}()

// Avoid - forces concurrency on caller
func ProcessAsync(data []byte) <-chan Result {
    ch := make(chan Result)
    go func() {
        // ...
    }()
    return ch
}
```

## Limiting Concurrency

Use buffered channel as semaphore:

```go
var sem = make(chan struct{}, maxConcurrent)

func process(item Item) {
    sem <- struct{}{}        // Acquire
    defer func() { <-sem }() // Release
    // do work
}
```

## WaitGroup

Wait for multiple goroutines:

```go
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(it Item) {
        defer wg.Done()
        process(it)
    }(item)
}
wg.Wait()
```

## Mutex

Protect shared state when channels aren't appropriate:

```go
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}
```

**Never copy types containing `sync.Mutex`.**
