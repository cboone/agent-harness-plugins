# Source Canaries

Reading a file's own source as text, so a declaration nothing can check as behaviour can still be checked as spelling.

## When this is the right instrument

All three conditions, together:

- **The failure mode is a weakening rather than a break.** A releasing store simplified to relaxed, a constructor swapped for its sibling in one of the spellings that compiles, two correct lines put in the wrong order. Each compiles, and each passes a suite that never exercises the concurrency.
- **The instrument that would catch it is unavailable.** It needs a platform this machine cannot be, or hardware nobody has, or it does not exist.
- **The correct spelling is short and stable.** A canary over code that is legitimately edited every week is noise.

The motivating measurement: replacing one releasing store with a relaxed one passed all 139 tests of the module it was in. The suite could not discriminate a correct ordering from an incorrect one, and reading the module was the only check that existed. The realistic failure is not a wrong design but someone simplifying an atomic, watching the suite pass, and shipping it.

### The constructor case, which is about plants rather than canaries

The first condition above lists a constructor swap, and the plant table below records that the direct substitution **does not compile**: a container-level initializer must be evaluable at compile time, and the sibling constructor calls into the platform, so the type system refuses it outright.

**That refusal is about one spelling and not about the defect.** The restructure that reaches the same place, an undefined initializer plus a runtime setup call, compiles cleanly, passes the suite, and is exactly what the canary catches, through an assertion that the term appears zero times. So the canary does guard the constructor change.

Concluding otherwise from the first spelling would have discarded a working guard, which is the plant-table rule applied to a canary: try the second spelling before deciding a defect cannot be written.

## What it is

Embed the file's own source at compile time, cut it at the test section so the canary cannot read its own string literals, and assert that specific statement lines are stated as written.

```zig
/// Everything above the tests banner, so a canary cannot read its own string
/// literals and count them as code.
pub fn implementation(source: []const u8) []const u8 {
    const marker = "\n// Tests\n";
    return source[0 .. std.mem.indexOf(u8, source, marker) orelse source.len];
}
```

Each call site does the embedding itself, because the path resolves relative to the importing file. A file with no banner is returned whole, which is correct for one whose tests live elsewhere.

**That fallback is itself a vacuity hazard, and it is worth a control.** The `orelse` cannot tell an intentionally banner-less file from one whose banner was renamed or removed. Where the tests are co-located, the second case silently widens the canary's scope to include the test section, so the assertions start reading the canary's own string literals and can report a result about the canary text rather than about the implementation. Assert the marker's presence separately in any file whose tests sit below it, so a renamed banner fails loudly instead of quietly changing what is being measured.

## Three primitives, and why all three

| Primitive      | Question it answers                                             |
| -------------- | --------------------------------------------------------------- |
| `stated`       | How many statement lines are **exactly** this line              |
| `mentions`     | How many statement lines **contain** this substring             |
| `statedBefore` | Is each line stated once, and does the first precede the second |

**An exact-match count alone leaves a hole.** A file that states every line asked of it and also quietly acquired a sixth operation somewhere else satisfies every exact-match check. Only a containing count refuses it:

```zig
test "mentions counts lines rather than occurrences, and catches an operation nothing asked about" {
    const code =
        \\const at = self.cursor.load(.acquire);
        \\self.cursor.store(at, .release);
        \\const sneaky = self.cursor.load(.monotonic);
    ;
    // Every line a caller pinned is present, and there is one more.
    try testing.expectEqual(1, stated(code, "const at = self.cursor.load(.acquire);"));
    try testing.expectEqual(1, stated(code, "self.cursor.store(at, .release);"));
    try testing.expectEqual(3, mentions(code, "self.cursor."));
}
```

**Neither count can see order.** Where a consumer copies a payload before releasing the slot, reversing those two lines lets the producer overwrite what the consumer is still reading. Both lines are individually correct, so both counts are identical either way, and the test that justifies the third primitive asserts exactly that:

```zig
// Both counts are identical either way, which is why this helper exists.
try testing.expectEqual(stated(right, first), stated(wrong, first));
try testing.expectEqual(stated(right, second), stated(wrong, second));
```

Make the order predicate false when either line is absent or stated more than once, because "before" means nothing about a line stated twice.

## Two matching properties that are answers, not choices

Both were flaws in the first implementation.

**Match a statement trimmed**, ignoring indentation. The original formatted a match string with exactly eight leading spaces, so moving a statement into a conditional block failed the canary with no semantic change at all. Trimmed, re-indentation is a wash.

**Treat a line whose trimmed text begins with a comment marker as not a statement.** The original counted a bare identifier over text that included the doc comments above the test banner, so a new comment naming the identifier broke the count. It is also what makes an assertion like `mentions(code, "Threaded.init") == 0` expressible at all, in a file whose own docstring names that term twice in order to forbid it.

```zig
fn next(self: *Statements) ?[]const u8 {
    while (self.lines.next()) |line| {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (trimmed.len == 0) continue;
        if (std.mem.startsWith(u8, trimmed, "//")) continue;
        return trimmed;
    }
    return null;
}
```

State the residual rather than hiding it: **a trailing comment is still part of its statement line.** Stripping from the first comment marker would misread a string literal containing one, and the alternative to both is a tokenizer. Record whether any guarded file has a trailing comment, so the limit is a known fact rather than a surprise.

## A passing canary means unchanged, not correct

Say so in the module's own documentation, because the difference is the whole basis for trusting it:

> These read the source as text and prove nothing about behaviour. A passing canary means the lines are unchanged, not that they are correct. A global find-and-replace rewrites the string literals here along with the code they name, which is accepted: the canary is deliberately the faster of the two checks rather than the harder to fool.

The defeat is real and was demonstrated: a careless in-place regex substitution rewrote the assertion along with the code and the suite stayed green. So a canary is never the only guard for a claim that matters. It is the one that runs on every machine in a fraction of a second, paired with a slower instrument that catches what a text assertion cannot.

The two checks are complementary rather than redundant, and neither alone is enough. That is the same conclusion the instrument matrix reaches by a different route. See `./references/instrument-blindness.md`.

## Guard the guard

A canary helper that five checks rest on is a place where one bug becomes five silent passes. Assert every property the helper claims, and assert both flaws it exists to fix as absences rather than describing them in prose:

```zig
// This module is itself the thing five canaries rest on, so a bug here is five
// checks silently passing. Each property the module claims is asserted, and the
// two flaws it exists to fix are asserted as absences rather than described.
```

Name each test as the claim it makes: "a statement matches trimmed, so indentation is not part of the claim", "comments are not statements, which is the second flaw fixed", "the order predicate refuses an absent or repeated line rather than guessing".

## Plant against a canary, including the controls

A canary is a check, so it gets a plant table like any other. Two tables, in fact.

**Plants that must fire.** One row per pinned statement, with the site and what actually happened:

| Plant                                                   | Result                                      |
| ------------------------------------------------------- | ------------------------------------------- |
| The single-threaded constructor swapped for its sibling | **Compile error**, not a test failure       |
| The same, restructured into a runtime setup call        | Both tests, at two named lines              |
| A releasing store relaxed, one of two                   | One named line, the count of 2 falling to 1 |
| Two correct lines swapped                               | One named line, the order predicate alone   |
| A flag split into two words                             | One named line                              |

Note what the first row establishes: the plant the issue asked for could not be applied, and a second spelling of the same defect had to be found before the canary could be exercised at all. Record both.

**Controls that must stay green.** These are what prove the two matching properties are live:

| Control                                                              | Result                                   |
| -------------------------------------------------------------------- | ---------------------------------------- |
| A statement re-indented into a conditional block, no semantic change | Green. The indentation flaw is gone      |
| A doc comment naming the pinned identifier, added above the banner   | Green. The comment-counting flaw is gone |

And commit the canary before planting against it, so reverting the plant reverts the plant and not the check.

## What a real canary looks like

Written as a table of refusals rather than a list of assertions, so each line says what it is for:

The `...` below stands for a type annotation elided for width. `stated` is an exact match, so a real canary spells the line out in full, character for character, and one of these copied literally would fail against correct code.

| Assertion                                                          | What it refuses                               |
| ------------------------------------------------------------------ | --------------------------------------------- |
| `stated(code, "const backend_init: ... = .init_single_threaded;")` | The constructor changing                      |
| `stated(code, "var backend: ... = backend_init;")`                 | The instance being initialized some other way |
| `mentions(code, "Threaded.init") == 0`                             | The restructure into a runtime setup          |
| `mentions(code, "std.Io.Threaded") == 2`                           | A second instance arriving beside the first   |
| `stated(code, "return backend.io();")`                             | A different instance being handed back        |
| `mentions(code, "backend =") == 0`                                 | The restructure, from the assignment side     |

The pair of counts at rows three and four is the pattern worth copying: one refuses a specific wrong spelling, the other refuses an extra occurrence of the right one.

## Portable forms

The mechanism needs compile-time file reading to be free, but the idea does not.

| Form                                    | Where it fits                                                               |
| --------------------------------------- | --------------------------------------------------------------------------- |
| A test that reads its own source file   | Any language with file I/O in tests. Costs a read per run, which is nothing |
| A custom lint rule                      | Where the project already runs a linter with a plugin API                   |
| A golden file of extracted declarations | Where a tool can emit the declarations and the diff is reviewed             |
| A CI grep over the built artifact       | Last resort, and note the limit below                                       |

The CI grep has a failure this practice has already recorded: nothing links the needle to the declaration, so a rename makes the assertion vacuous and green at the same moment, and a positive control that only proves the artifact is readable does not help. See `./references/vacuous-passes.md`.

Whichever form, keep the comment-line exclusion: a doc comment that names the identifier must not be able to satisfy or break a count. The **rule** ports; the implementation shown above does not, because it tests for `//` and nothing else. Substitute your language's own comment syntax, and remember that several have more than one: `#` in Python, Ruby and shell, `--` in Lua and SQL, `;` in Lisp and assembly, `%` in Erlang and TeX, and `/* ... */` block comments alongside `//` in most of the C family. A canary copied across languages with the marker unchanged counts comment lines as statements, which can make it pass or fail for a reason that has nothing to do with the code.

**The trimming rule does not port, and porting it blindly is a way to build a canary that accepts the defect.** Matching trimmed is correct where indentation carries no meaning, which is what makes re-indenting into a conditional a wash in a brace-delimited language. In Python, or any other syntax where indentation is the block structure, moving a statement into or out of an `if` changes behaviour while leaving the trimmed line identical, so a trimmed match accepts exactly the edit a canary exists to refuse. There the indentation is part of the claim: match the line with its leading whitespace, or pin the enclosing block as well as the statement, and say in the canary's own comment which you chose and why.

The general form of that: **trim what the language says is insignificant, and no more.** Work out which of the two properties is answering a real flaw in your language before copying both.
