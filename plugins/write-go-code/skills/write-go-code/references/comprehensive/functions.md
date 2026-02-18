# Functions

## Multiple Return Values

Standard pattern for error handling:

```go
func Load(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("read config: %w", err)
    }
    // ...
    return config, nil
}
```

**Comma-ok idiom** for optional results:

```go
func Lookup(key string) (value string, ok bool) {
    v, found := cache[key]
    return v, found
}

// Usage
if val, ok := Lookup("key"); ok {
    // use val
}
```

## Named Return Parameters

**Use when:**

- Multiple parameters of same type
- Meaning not clear from context
- Documentation benefit

```go
// Good - clarifies which float is which
func Location() (lat, long float64, err error)

// Good - documents the return values
func Split(path string) (dir, file string)
```

**Avoid when:**

- Creates repetition with function name
- Single return or obvious meaning

```go
// Bad - repetitive
func (n *Node) Parent() (node *Node)

// Good
func (n *Node) Parent() *Node
```

## Naked Returns

Return without arguments returns named values:

```go
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return  // Returns x and y
}
```

**Only use in short functions.** In longer functions, be explicit:

```go
func processData(data []byte) (result []byte, err error) {
    // ... many lines ...
    return result, err  // Explicit - clearer
}
```

## Defer

Schedules function to run when enclosing function returns:

```go
func ReadFile(path string) ([]byte, error) {
    f, err := os.Open(path)
    if err != nil {
        return nil, err
    }
    defer f.Close()  // Runs when ReadFile returns

    return io.ReadAll(f)
}
```

**Key behaviors:**

1. Arguments evaluated immediately:

```go
func trace(msg string) {
    fmt.Println("enter:", msg)
}
func un(msg string) {
    fmt.Println("leave:", msg)
}

func foo() {
    defer un(trace("foo"))  // trace runs NOW, un runs on return
    // ...
}
```

1. LIFO order:

```go
defer fmt.Println("first")
defer fmt.Println("second")
defer fmt.Println("third")
// Output: third, second, first
```

1. Can modify named return values:

```go
func double(x int) (result int) {
    defer func() { result *= 2 }()
    return x  // Returns x * 2
}
```

## Defer for Cleanup

**Mutex unlock:**

```go
func (c *Counter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}
```

**Close resources:**

```go
resp, err := http.Get(url)
if err != nil {
    return err
}
defer resp.Body.Close()
```

**Cleanup in loops** - be careful:

```go
// Bad - defers accumulate until function returns
for _, path := range paths {
    f, _ := os.Open(path)
    defer f.Close()  // Won't close until loop ends
}

// Good - use closure
for _, path := range paths {
    func() {
        f, _ := os.Open(path)
        defer f.Close()
        // process f
    }()
}
```

## Variadic Functions

Accept variable number of arguments:

```go
func Printf(format string, args ...interface{})
func Min(values ...int) int

// Call with individual args
Min(1, 2, 3)

// Call with slice (spread operator)
nums := []int{1, 2, 3}
Min(nums...)
```

## Function Types

Functions are first-class values:

```go
type Handler func(w http.ResponseWriter, r *http.Request)

func middleware(next Handler) Handler {
    return func(w http.ResponseWriter, r *http.Request) {
        // before
        next(w, r)
        // after
    }
}
```

## Closures

Function literals capture variables:

```go
func counter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

c := counter()
c()  // 1
c()  // 2
```

**Watch for loop variable capture:**

```go
// Bug - all closures share same i
for i := 0; i < 3; i++ {
    funcs[i] = func() { fmt.Println(i) }
}

// Fix - capture by parameter
for i := 0; i < 3; i++ {
    i := i  // Shadow with new variable
    funcs[i] = func() { fmt.Println(i) }
}
```

## Methods vs Functions

Methods have a receiver; functions don't:

```go
// Method - has receiver
func (c *Client) Connect() error

// Function - no receiver
func Connect(addr string) (*Client, error)
```

Use methods when:

- Operation is on a specific type
- Need to satisfy an interface
- State modification needed

Use functions when:

- No associated type
- Constructor (`NewXxx`)
- Utility operations
