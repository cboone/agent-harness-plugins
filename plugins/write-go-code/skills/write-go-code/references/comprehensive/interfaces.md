# Interfaces

## Interface Basics

Interfaces define behavior (set of methods):

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}
```

**Implicit satisfaction** - no `implements` keyword:
```go
type MyReader struct{}

func (r *MyReader) Read(p []byte) (n int, err error) {
    // implementation
}
// MyReader now satisfies Reader interface
```

## Interface Naming

**Single-method interfaces**: method name + `-er` suffix:
- `Reader` (has `Read`)
- `Writer` (has `Write`)
- `Closer` (has `Close`)
- `Stringer` (has `String`)
- `Formatter` (has `Format`)

**Multi-method interfaces**: descriptive noun:
- `ReadWriter`
- `ReadWriteCloser`
- `FileSystem`

## Define Where Used

Interfaces belong in the **consuming** package:

```go
// Good - consumer defines what it needs
package storage

type DataStore interface {
    Get(key string) ([]byte, error)
    Put(key string, value []byte) error
}

func NewCache(store DataStore) *Cache {
    // ...
}

// Bad - producer exports interface
package redis

type Store interface {  // Don't do this
    Get(key string) ([]byte, error)
    Put(key string, value []byte) error
}
```

## Return Concrete Types

Constructors should return concrete types:

```go
// Good
func NewClient(addr string) *Client

// Avoid
func NewClient(addr string) ClientInterface
```

Let consumers define interfaces based on what methods they need.

## Interface Embedding

Compose interfaces by embedding:

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type ReadWriter interface {
    Reader
    Writer
}

type ReadWriteCloser interface {
    Reader
    Writer
    Closer
}
```

## Type Assertions

Extract concrete type from interface:

```go
// Unsafe - panics if wrong type
s := i.(string)

// Safe - comma-ok idiom
s, ok := i.(string)
if !ok {
    // i is not a string
}
```

**Best practice**: Always use comma-ok form unless you're certain of the type.

## Type Switches

Discover dynamic type:

```go
switch v := i.(type) {
case string:
    fmt.Printf("string: %s\n", v)
case int:
    fmt.Printf("int: %d\n", v)
case nil:
    fmt.Println("nil")
default:
    fmt.Printf("unknown type: %T\n", v)
}
```

## Struct Embedding

Embed types to "inherit" methods:

```go
type Reader struct {
    // fields
}

func (r *Reader) Read(p []byte) (n int, err error) {
    // implementation
}

type BufferedReader struct {
    *Reader  // Embedded - gets Read method
    buffer   []byte
}

// BufferedReader now has Read method
br := &BufferedReader{Reader: r}
br.Read(p)
```

**Embedding is not inheritance:**
- Embedded type's methods receive embedded type as receiver
- Outer type can override by defining same method
- Access embedded type directly: `br.Reader.Read(p)`

## Name Conflicts

Outer names shadow inner:

```go
type Inner struct {
    Name string
}

type Outer struct {
    Inner
    Name string  // Shadows Inner.Name
}

o := Outer{}
o.Name        // Outer's Name
o.Inner.Name  // Inner's Name
```

## Empty Interface

`interface{}` (or `any` since Go 1.18) accepts any type:

```go
func Print(v any) {
    fmt.Printf("%v\n", v)
}

Print(42)
Print("hello")
Print([]int{1, 2, 3})
```

**Prefer `any` over `interface{}`** in new code.

## Interface Values

Interface value = (type, value) pair:

```go
var w io.Writer        // (nil, nil) - nil interface
var f *os.File = nil
w = f                  // (*os.File, nil) - non-nil interface!

w == nil               // false - interface holds type info
```

**Nil interface vs nil concrete value:**
```go
func returnsWriter() io.Writer {
    var f *os.File = nil
    return f  // Returns non-nil interface!
}

w := returnsWriter()
w == nil  // false
```

## Interface Compile-Time Check

Verify type implements interface at compile time:

```go
var _ io.Reader = (*MyReader)(nil)
var _ io.Writer = (*MyWriter)(nil)
```

## Small Interfaces

Prefer small, focused interfaces:

```go
// Good - small, composable
type Reader interface {
    Read(p []byte) (n int, err error)
}

// Avoid - large, hard to implement
type FileSystem interface {
    Open(name string) (File, error)
    Create(name string) (File, error)
    Remove(name string) error
    Rename(old, new string) error
    Stat(name string) (FileInfo, error)
    // ... many more
}
```

Small interfaces are easier to implement, mock, and compose.

## Accept Interfaces, Return Structs

General guideline:
- Functions should accept interfaces (flexible)
- Functions should return concrete types (informative)

```go
// Good
func Process(r io.Reader) error           // Accepts interface
func NewClient(addr string) *Client       // Returns concrete

// Avoid
func Process(data *bytes.Buffer) error    // Too specific
func NewClient(addr string) Client        // Interface return
```
