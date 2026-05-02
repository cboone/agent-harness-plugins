
# General Programming

Lean 4 as a general-purpose functional programming language, covering type classes, monads, pattern matching, dependent types, and project management.

## Table of Contents

- [Type classes and instances](#type-classes-and-instances)
- [Monads and do notation](#monads-and-do-notation)
- [Pattern matching](#pattern-matching)
- [Inductive types](#inductive-types)
- [Dependent types](#dependent-types)
- [IO and effects](#io-and-effects)
- [Project management with Lake](#project-management-with-lake)

## Type Classes and Instances

Type classes are Lean's mechanism for ad hoc polymorphism (similar to Haskell's type classes or Rust's traits).

### Defining type classes

```lean
class Printable (α : Type) where
  toString : α → String

class Container (c : Type → Type) where
  empty : c α
  insert : α → c α → c α
  member : [BEq α] → α → c α → Bool
```

### Providing instances

```lean
instance : Printable Nat where
  toString n := s!"{n}"

instance : Printable Bool where
  toString
    | true => "true"
    | false => "false"
```

### Using type classes

```lean
-- Type class constraint with square brackets
def display [Printable α] (x : α) : String :=
  Printable.toString x

-- Multiple constraints
def findAndPrint [BEq α] [Printable α] (x : α) (xs : List α) : String :=
  if xs.contains x then s!"Found: {Printable.toString x}"
  else "Not found"
```

### Deriving instances

Use `deriving` to auto-generate standard instances:

```lean
structure Point where
  x : Float
  y : Float
  deriving Repr, BEq, Inhabited
```

Common derivable classes: `Repr`, `BEq`, `Hashable`, `Inhabited`, `DecidableEq`, `Ord`.

## Monads and Do Notation

Lean 4 uses monads extensively for effects, and `do` notation provides imperative-style syntax.

### Do notation basics

```lean
def greet (name : String) : IO Unit := do
  let greeting := s!"Hello, {name}!"
  IO.println greeting

def readAndProcess : IO String := do
  IO.println "Enter your name:"
  let name ← IO.getStdin >>= (·.getLine)
  let trimmed := name.trim
  return s!"Welcome, {trimmed}"
```

### Mutable variables with `do`

```lean
def sumList (xs : List Nat) : Nat := Id.run do
  let mut total := 0
  for x in xs do
    total := total + x
  return total
```

### Common monads

| Monad       | Purpose                                        |
| ----------- | ---------------------------------------------- |
| `IO`        | Side effects (files, network, etc.)            |
| `Option`    | Computations that may fail silently            |
| `Except ε`  | Computations that may fail with error type `ε` |
| `StateM σ`  | Stateful computation with state type `σ`       |
| `ReaderM ρ` | Read-only environment of type `ρ`              |
| `Id`        | Pure computation (use with `Id.run`)           |

### Monad transformers

Compose effects by stacking transformers:

```lean
-- State + IO
def statefulIO : StateT Nat IO Unit := do
  let n ← get
  IO.println s!"Current state: {n}"
  set (n + 1)

-- Reader + Except
abbrev AppM := ReaderT Config (Except AppError)

def getConfigValue (key : String) : AppM String := do
  let config ← read
  match config.get key with
  | some v => pure v
  | none => throw (.missingKey key)
```

## Pattern Matching

### Basic `match` expressions

```lean
def describe : Nat → String
  | 0 => "zero"
  | 1 => "one"
  | n => s!"many ({n})"

-- With multiple arguments
def compare : Nat → Nat → String
  | 0, 0 => "both zero"
  | 0, _ => "first is zero"
  | _, 0 => "second is zero"
  | _, _ => "both nonzero"
```

### Guards and nested patterns

```lean
def classify (n : Int) : String :=
  match n with
  | 0 => "zero"
  | n => if n > 0 then "positive" else "negative"

-- Nested patterns
def headOfHead : List (List α) → Option α
  | (x :: _) :: _ => some x
  | _ => none
```

### `let` pattern matching

```lean
def swap (p : α × β) : β × α :=
  let (a, b) := p
  (b, a)
```

## Inductive Types

### Simple enumerations

```lean
inductive Color where
  | red
  | green
  | blue
  deriving Repr, BEq
```

### Parameterized types

```lean
inductive Tree (α : Type) where
  | leaf : Tree α
  | node : Tree α → α → Tree α → Tree α
  deriving Repr
```

### Recursive functions over inductive types

```lean
def Tree.size : Tree α → Nat
  | .leaf => 0
  | .node l _ r => 1 + l.size + r.size

def Tree.map (f : α → β) : Tree α → Tree β
  | .leaf => .leaf
  | .node l v r => .node (l.map f) (f v) (r.map f)
```

### Mutual induction

```lean
mutual
  inductive Expr where
    | lit : Nat → Expr
    | add : Expr → Expr → Expr
    | block : Stmt → Expr → Expr

  inductive Stmt where
    | assign : String → Expr → Stmt
    | seq : Stmt → Stmt → Stmt
end
```

## Dependent Types

Lean's type system allows types to depend on values, enabling precise specifications.

### Vectors (length-indexed lists)

```lean
inductive Vec (α : Type) : Nat → Type where
  | nil : Vec α 0
  | cons : α → Vec α n → Vec α (n + 1)

-- The type guarantees we never access an empty vector
def Vec.head : Vec α (n + 1) → α
  | .cons x _ => x
```

### Subtypes

```lean
-- A natural number that is positive
def PosNat := { n : Nat // n > 0 }

def safeDivide (a : Nat) (b : PosNat) : Nat :=
  a / b.val
```

### Propositions as types

```lean
-- The type itself encodes the proof obligation
def safeIndex (xs : List α) (i : Nat) (h : i < xs.length) : α :=
  xs[i]
```

## IO and Effects

### Basic IO

```lean
def main : IO Unit := do
  let args ← IO.getArgs
  match args with
  | [] => IO.println "No arguments provided"
  | _ => for arg in args do
    IO.println s!"Argument: {arg}"
```

### File operations

```lean
def readFile (path : String) : IO String := do
  let contents ← IO.FS.readFile path
  return contents

def writeFile (path : String) (content : String) : IO Unit := do
  IO.FS.writeFile path content
```

### Error handling in IO

```lean
def safeRead (path : String) : IO (Option String) := do
  try
    let contents ← IO.FS.readFile path
    return some contents
  catch _ =>
    return none
```

## Project Management with Lake

### Creating projects

```bash
# Create a new project (creates directory)
lake new my-project

# Do NOT use lake init (does not create directory, common gotcha)
```

### lakefile.lean structure

```lean
import Lake
open Lake DSL

package myProject where
  leanOptions := #[
    ⟨`autoImplicit, false⟩  -- recommended: disable auto-implicit
  ]

@[default_target]
lean_lib MyProject where
  srcDir := "src"

lean_exe myApp where
  root := `Main
```

### Adding dependencies

```lean
require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "main"

require aesop from git
  "https://github.com/leanprover-community/aesop" @ "main"
```

### Common Lake commands

| Command               | Purpose                                |
| --------------------- | -------------------------------------- |
| `lake build`          | Build the project                      |
| `lake exe myApp`      | Run an executable target               |
| `lake update`         | Update dependencies                    |
| `lake clean`          | Remove build artifacts                 |
| `lake env printPaths` | Show include paths (useful for editor) |

Mathlib build policy: in a fresh clone or worktree, do not use `lake build` as the bootstrap step. Run the project's documented bootstrap script first so `lake exe cache get` downloads Mathlib's prebuilt artifacts. If Mathlib's build artifacts are missing, rerun the bootstrap script rather than letting Lake compile Mathlib from source. The invoking project's CLAUDE.md names the specific bootstrap script and the expected artifact path.

### Recommended project settings

Disable `autoImplicit` to catch undeclared variable errors early:

```lean
set_option autoImplicit false
```

This is especially important in library code where implicit variables can silently change the meaning of a declaration.
