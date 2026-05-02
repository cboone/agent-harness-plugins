
# Metaprogramming

Guide to Lean 4 metaprogramming: macros, custom tactics, syntax extensions, and elaboration.

## Table of Contents

- [Overview](#overview)
- [Monad hierarchy](#monad-hierarchy)
- [Syntax and quotations](#syntax-and-quotations)
- [Macros](#macros)
- [Custom notation](#custom-notation)
- [Elaboration](#elaboration)
- [Writing custom tactics](#writing-custom-tactics)
- [Practical examples](#practical-examples)

## Overview

Lean 4 is implemented largely in Lean itself, which means metaprogramming uses the same language as regular programming. The key distinction is between:

- **Object level**: the Lean code being processed (your definitions, theorems, types)
- **Meta level**: the code that manipulates object-level code (macros, tactics, elaborators)

Three major use cases for metaprogramming:

1. **Custom notation**: extend Lean's syntax for domain-specific needs
2. **Domain-specific languages**: build parsers and interpreters within Lean
3. **Tactics**: automate proof steps

## Monad Hierarchy

Lean's metaprogramming monads form a hierarchy, each adding capabilities:

```text
CoreM           -- core infrastructure (environment, options, logging)
  ↓
MetaM           -- metavariable context, type checking, unification
  ↓
TermElabM       -- term elaboration (parsing expressions into terms)
  ↓
TacticM         -- tactic state (goal list management)
```

| Monad       | Key Capabilities                                            |
| ----------- | ----------------------------------------------------------- |
| `CoreM`     | Environment access, options, messages, name generation      |
| `MetaM`     | Create/assign metavariables, `isDefEq`, `inferType`, `whnf` |
| `TermElabM` | Elaborate syntax to expressions, handle pending goals       |
| `TacticM`   | Access and modify the goal list, focus goals                |

Each monad in the hierarchy can use all operations from the monads above it. A `TacticM` computation can call `MetaM` functions directly.

## Syntax and Quotations

### Quoting syntax

Use backtick-prefixed quotes to construct syntax trees:

```lean
-- Construct syntax for the expression "1 + 2"
`(1 + 2)

-- Construct syntax with anti-quotations (splicing in values)
def mkAddExpr (a b : Syntax) : MacroM Syntax :=
  `($a + $b)

-- Splice arrays with $[...]*
def mkSum (terms : Array Syntax) : MacroM Syntax :=
  `($(terms[0]!) $(terms[1:].toArray.map (fun t => `(+ $t))*)
```

### Pattern matching on syntax

```lean
-- Match syntax patterns
def isPlus : Syntax → Bool
  | `($_ + $_) => true
  | _ => false
```

### Syntax categories

Lean organizes syntax into categories:

| Category  | Description            | Examples                   |
| --------- | ---------------------- | -------------------------- |
| `term`    | Expressions            | `1 + 2`, `fun x => x`      |
| `command` | Top-level declarations | `def`, `theorem`, `#check` |
| `tactic`  | Proof tactics          | `simp`, `exact`, `apply`   |
| `attr`    | Attributes             | `@[simp]`, `@[ext]`        |

## Macros

Macros are syntax-to-syntax transformations. They run before elaboration and are the simplest form of metaprogramming.

### Defining macros

```lean
-- Simple macro: translate custom syntax to existing syntax
macro "assert! " cond:term : command =>
  `(#guard $cond)

-- Macro with multiple syntax pieces
macro "repeat " n:num " times " body:doSeq : doElem =>
  `(doElem| for _ in List.range $n do $body)
```

### Macro rules

```lean
-- Define syntax first, then provide expansion rules
syntax "myIf " term " then " term " else " term : term

macro_rules
  | `(myIf $cond then $t else $f) => `(if $cond then $t else $f)
```

### Hygiene

Macros in Lean 4 are hygienic by default: names introduced by the macro do not clash with names in the surrounding code. Use `Lean.Macro.mkFreshId` if you need unique names.

## Custom Notation

### Basic notation

```lean
-- Infix notation
infixl:65 " +ₘ " => MyType.add

-- Prefix notation
prefix:100 "√" => Real.sqrt

-- Postfix notation
postfix:max "!" => Nat.factorial
```

### Scoped notation

Use `scoped` to limit notation to when the namespace is opened:

```lean
namespace MatrixOps

scoped notation:50 A " ⬝ " B => Matrix.mul A B
scoped notation:max A "ᵀ" => Matrix.transpose A

end MatrixOps

-- Only available when `open MatrixOps`
```

### Notation with precedence

Precedence levels control parsing priority. Higher numbers bind tighter.

| Level | Typical use                           |
| ----- | ------------------------------------- |
| 10-20 | Logical connectives                   |
| 50    | Comparison operators                  |
| 65    | Addition                              |
| 70    | Multiplication                        |
| 100+  | Unary operators, function application |

## Elaboration

Elaboration is the process of converting parsed syntax into fully typed Lean expressions.

### Term elaborators

```lean
-- Custom term elaborator
@[term_elab myCustomSyntax]
def elabMyCustom : TermElab := fun stx expectedType? => do
  -- stx is the parsed syntax
  -- expectedType? is the expected type (if known from context)
  let inner ← Lean.Elab.Term.elabTerm stx[1] expectedType?
  return inner
```

### Command elaborators

```lean
-- Custom top-level command
syntax (name := myCommand) "myCmd " ident : command

@[command_elab myCommand]
def elabMyCommand : CommandElab := fun stx => do
  let name := stx[1].getId
  Lean.logInfo m!"Processing: {name}"
```

## Writing Custom Tactics

All tactics have type `TacticM Unit` and work by modifying the goal list.

### Basic tactic structure

```lean
-- A tactic that closes the goal if it is `True`
elab "my_trivial" : tactic => do
  let goal ← Lean.Elab.Tactic.getMainGoal
  let goalType ← goal.getType
  if goalType.isConstOf ``True then
    goal.assign (Lean.mkConst ``True.intro)
  else
    Lean.Meta.throwTacticEx `my_trivial goal
      m!"expected True, got {goalType}"
```

### Using `liftMetaTactic`

Convert a `MetaM` function that transforms a goal into a tactic:

```lean
-- liftMetaTactic1: transforms one goal into one new goal
elab "my_intro " name:ident : tactic =>
  Lean.Elab.Tactic.liftMetaTactic1 fun goal => do
    let (_, newGoal) ← goal.intro name.getId
    return newGoal
```

### Combining existing tactics

```lean
-- Run existing tactics programmatically
elab "my_tactic" : tactic => do
  Lean.Elab.Tactic.evalTactic (← `(tactic| simp; ring))
```

### Accessing goal state

```lean
elab "show_goals" : tactic => do
  let goals ← Lean.Elab.Tactic.getGoals
  for goal in goals do
    let goalType ← goal.getType
    Lean.logInfo m!"Goal: {goalType}"
```

## Practical Examples

### A `trace` macro for debugging

```lean
/-- Log an expression and its value during elaboration. -/
macro "trace! " e:term : term => `(dbg_trace s!"{$(Lean.quote (toString e))} = {$e}"; $e)
```

### An `#assert` command

```lean
/-- Compile-time assertion that a proposition holds. -/
elab "#assert " prop:term : command => do
  let propExpr ← Lean.Elab.Command.liftTermElabM do
    Lean.Elab.Term.elabTerm prop (some (Lean.mkConst ``Bool))
  let val ← Lean.Elab.Command.liftTermElabM do
    Lean.Meta.reduce propExpr
  match val with
  | .lit (.natVal 1) => pure ()  -- true
  | _ => throwError "Assertion failed: {prop}"
```

### A tactic that tries multiple approaches

```lean
/-- Try `simp`, then `omega`, then `decide`. -/
elab "auto" : tactic => do
  let tactics := #[
    ← `(tactic| simp),
    ← `(tactic| omega),
    ← `(tactic| decide)
  ]
  for t in tactics do
    try
      Lean.Elab.Tactic.evalTactic t
      return
    catch _ => pure ()
  Lean.Elab.Tactic.throwNoGoalsToBeSolved
```

## Further Reading

- [Metaprogramming in Lean 4](https://leanprover-community.github.io/lean4-metaprogramming-book/) (comprehensive book)
- [Metaprogramming for Dummies](https://github.com/leanprover-community/mathlib4/wiki/Metaprogramming-for-dummies) (beginner guide)
- [Lean 4 source code](https://github.com/leanprover/lean4) for real-world examples of elaborators and tactics
