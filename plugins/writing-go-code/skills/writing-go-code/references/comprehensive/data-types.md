# Data Types and Allocation

## new vs make

**`new(T)`** - Allocates zeroed memory, returns `*T`:
```go
p := new(Config)  // *Config, all fields zero-valued
```

**`make(T, args)`** - Initializes slices, maps, channels only:
```go
s := make([]int, 10)        // []int, length 10, capacity 10
s := make([]int, 0, 100)    // []int, length 0, capacity 100
m := make(map[string]int)   // map, initialized and ready
ch := make(chan int, 10)    // buffered channel, capacity 10
```

## Zero Values

Design types so zero values are useful:

```go
// Good - zero value is valid empty buffer
type Buffer struct {
    data []byte
}

// sync.Mutex zero value is unlocked mutex
var mu sync.Mutex  // Ready to use

// bytes.Buffer zero value is empty, ready buffer
var buf bytes.Buffer
buf.WriteString("hello")
```

## Arrays vs Slices

**Arrays** are values (copied on assignment):
```go
var a [3]int          // Array of 3 ints
b := a                // Copies entire array
func f(arr [3]int)    // Receives copy
```

**Slices** are references (preferred for most uses):
```go
var s []int           // Nil slice
s := make([]int, 10)  // Slice of 10 ints
t := s                // Same underlying array
func f(s []int)       // Receives slice header (ptr, len, cap)
```

## Slice Declaration

Prefer nil slice:
```go
// Good - nil slice
var items []string
items = append(items, "one")

// Avoid unless JSON encoding requires []
items := []string{}
```

## Composite Literals

**With field names** (preferred - resilient to field reordering):
```go
return &Config{
    Host:    "localhost",
    Port:    8080,
    Timeout: 30 * time.Second,
}
```

**Without field names** (fragile):
```go
// Breaks if fields reordered
return &Config{"localhost", 8080, 30 * time.Second}
```

**Empty literal equals new:**
```go
cfg := &Config{}    // Same as new(Config)
```

## Maps

**Declaration and initialization:**
```go
// Nil map - reads return zero value, writes panic
var m map[string]int

// Initialized map
m := make(map[string]int)
m := map[string]int{
    "one": 1,
    "two": 2,
}
```

**Comma-ok idiom** - distinguish missing from zero:
```go
// Bad - can't tell if key missing or value is 0
count := m["key"]

// Good - explicit check
count, ok := m["key"]
if !ok {
    // key doesn't exist
}

// Or inline
if count, ok := m["key"]; ok {
    // key exists
}
```

**Delete:**
```go
delete(m, "key")  // Safe even if key doesn't exist
```

## Slicing

```go
s := []int{0, 1, 2, 3, 4}
s[1:3]   // [1, 2]
s[:3]    // [0, 1, 2]
s[2:]    // [2, 3, 4]
s[:]     // [0, 1, 2, 3, 4] (copy of slice header)
```

**Slicing shares underlying array:**
```go
a := []int{1, 2, 3, 4, 5}
b := a[1:3]  // [2, 3]
b[0] = 99    // a is now [1, 99, 3, 4, 5]
```

## Append

Always reassign result:
```go
s = append(s, item)
s = append(s, items...)  // Append another slice
```

## Two-Dimensional Slices

**Variable row lengths:**
```go
rows := make([][]int, height)
for i := range rows {
    rows[i] = make([]int, width)
}
```

**Single allocation (fixed dimensions):**
```go
rows := make([][]int, height)
data := make([]int, height*width)
for i := range rows {
    rows[i] = data[i*width : (i+1)*width]
}
```

## Copying Structs

**Safe to copy** - simple value types:
```go
type Point struct {
    X, Y int
}
p1 := Point{1, 2}
p2 := p1  // OK - independent copy
```

**Don't copy** - types with pointer methods or sync primitives:
```go
type Counter struct {
    mu    sync.Mutex
    count int
}
// c1 := c2  // Bad - copies mutex

// Pass by pointer instead
func increment(c *Counter) {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}
```

## Type Conversions

Explicit conversions required:
```go
var i int = 42
var f float64 = float64(i)
var u uint = uint(f)
```

Between defined types:
```go
type Celsius float64
type Fahrenheit float64

var c Celsius = 100
var f Fahrenheit = Fahrenheit(c*9/5 + 32)
```
