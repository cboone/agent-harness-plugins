# Naming Conventions

## Package Names

- **Lowercase, single-word**: No underscores, no mixedCaps
- **Short and concise**: Everyone types it; `bufio` not `bufferedIO`
- **Base of source directory**: `encoding/base64` imports as `base64`
- **Avoid meaningless names**: `util`, `common`, `misc`, `api`, `types`, `interfaces`
- **No stuttering**: Contents use package name as context

  ```go
  // Good: bufio.Reader
  // Bad: bufio.BufReader
  ```

## Exported vs Unexported

- **Uppercase first letter**: Exported (visible outside package)
- **Lowercase first letter**: Unexported (package-private)
- **MixedCaps for multi-word**: `ServeHTTP`, `parseRequest`
- **Never underscores**: Exception: generated code, test files, OS/cgo libraries

## Initialisms

Maintain consistent case throughout:

- `URL` or `url`, never `Url`
- `HTTP` or `http`, never `Http`
- `ID` or `id`, never `Id`
- `API` or `api`, never `Api`

Examples:

```go
ServeHTTP       // not ServeHttp
XMLHTTPRequest  // not XmlHttpRequest or XMLHttpRequest
userID          // not userId
appID           // not appId
```

## Variables

**Length proportional to scope:**

- Loop index: `i`, `j`
- Reader: `r`
- Buffer: `b`, `buf`
- Method receiver: 1-2 letters (`c` for `Client`)
- Larger scope: more descriptive (`lineCount` not `c`)

**Avoid type in name:**

```go
// Good
var users []User
var count int

// Bad
var userSlice []User
var countInt int
```

## Receivers

- **Short**: 1-2 letters reflecting type (`c` or `cl` for `Client`)
- **Consistent**: Same name across all methods of type
- **Not generic**: Never `this`, `self`, `me`

```go
// Good
func (c *Client) Connect() error
func (c *Client) Disconnect() error

// Bad
func (client *Client) Connect() error
func (self *Client) Disconnect() error
```

## Getters and Setters

- **No "Get" prefix** for getters: `Owner()` not `GetOwner()`
- **"Set" prefix** for setters: `SetOwner()`
- Use action verbs for expensive operations: `Compute`, `Fetch`, `Load`

```go
// Good
func (o *Object) Owner() string
func (o *Object) SetOwner(owner string)

// Bad
func (o *Object) GetOwner() string
```

## Interfaces

- **Single-method**: Add `-er` suffix: `Reader`, `Writer`, `Closer`, `Formatter`
- **Multi-method**: Descriptive noun: `FileSystem`, `Handler`
- **Canonical names**: Don't reuse `Read`, `Write`, `Close` unless semantically identical

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}

type ReadWriter interface {
    Reader
    Writer
}
```

## Constructors

- **Single type**: Use `New()`: `ring.New()`
- **Multiple types**: Use `NewTypeName()`: `list.NewElement()`
- Factory functions return interface when implementation is hidden

```go
// Package has one main type
func New() *Ring

// Package has multiple types
func NewReader(r io.Reader) *Reader
func NewWriter(w io.Writer) *Writer
```

## Constants

- **MixedCaps**: Same as variables, never `SCREAMING_SNAKE_CASE`
- **Name by role, not value**: `MaxRetries` not `Three`

```go
// Good
const MaxConnections = 100
const defaultTimeout = 30 * time.Second

// Bad
const MAX_CONNECTIONS = 100
const DEFAULT_TIMEOUT = 30
```
