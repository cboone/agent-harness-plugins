# Rust toolchain audit

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

## Bare pins allow one non-empty line with surrounding whitespace

```scrut
$ "${RUST_AUDIT_CASE_BIN}" bare
rows=1
Rust|rustc|1.76.0|1.90.0|rust-toolchain
```

## The legacy filename also supports TOML

```scrut
$ "${RUST_AUDIT_CASE_BIN}" toml
rows=1
Rust|rustc|1.76.0|1.90.0|rust-toolchain
```

## The modern filename retains TOML support

```scrut
$ "${RUST_AUDIT_CASE_BIN}" modern
rows=1
Rust|rustc|1.76.0|1.90.0|rust-toolchain.toml
```

## The legacy filename takes precedence

```scrut
$ "${RUST_AUDIT_CASE_BIN}" precedence
rows=1
Rust|rustc|1.76.0|1.90.0|rust-toolchain
```

## An empty legacy file does not expose a shadowed modern pin

```scrut
$ "${RUST_AUDIT_CASE_BIN}" empty
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Missing files produce no drift

```scrut
$ "${RUST_AUDIT_CASE_BIN}" missing
rows=0
```

## Moving channels are skipped in both formats

```scrut
$ "${RUST_AUDIT_CASE_BIN}" moving
rust-toolchain stable rows=0
bare stable rows=0
rust-toolchain beta rows=0
bare beta rows=0
rust-toolchain nightly rows=0
bare nightly rows=0
rust-toolchain.toml stable rows=0
rust-toolchain.toml beta rows=0
rust-toolchain.toml nightly rows=0
```

## TOML literal strings work under the legacy filename

```scrut
$ "${RUST_AUDIT_CASE_BIN}" literal
rows=1
Rust|rustc|1.76.0|1.90.0|rust-toolchain
```

## TOML literal strings work under the modern filename

```scrut
$ "${RUST_AUDIT_CASE_BIN}" modern-literal
rows=1
Rust|rustc|1.76.0|1.90.0|rust-toolchain.toml
```

## Quoted TOML keys require manual review

```scrut
$ "${RUST_AUDIT_CASE_BIN}" quoted-key
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Triple-quoted TOML values require manual review

```scrut
$ "${RUST_AUDIT_CASE_BIN}" triple-quoted
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Malformed legacy channels require manual review

```scrut
$ "${RUST_AUDIT_CASE_BIN}" malformed
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Malformed modern channels require manual review

```scrut
$ "${RUST_AUDIT_CASE_BIN}" malformed-modern
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain.toml
```

## Mixed-double declarations require review in rust-toolchain

```scrut
$ "${RUST_AUDIT_CASE_BIN}" mixed-double
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Mixed-double declarations require review in rust-toolchain.toml

```scrut
$ "${RUST_AUDIT_CASE_BIN}" mixed-double modern
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain.toml
```

## Mixed-single declarations require review in rust-toolchain

```scrut
$ "${RUST_AUDIT_CASE_BIN}" mixed-single
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Mixed-single declarations require review in rust-toolchain.toml

```scrut
$ "${RUST_AUDIT_CASE_BIN}" mixed-single modern
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain.toml
```

## Multiline declarations require review in rust-toolchain

```scrut
$ "${RUST_AUDIT_CASE_BIN}" multiline
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Multiline declarations require review in rust-toolchain.toml

```scrut
$ "${RUST_AUDIT_CASE_BIN}" multiline modern
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain.toml
```

## Duplicate declarations require review in rust-toolchain

```scrut
$ "${RUST_AUDIT_CASE_BIN}" duplicate
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Duplicate declarations require review in rust-toolchain.toml

```scrut
$ "${RUST_AUDIT_CASE_BIN}" duplicate modern
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain.toml
```

## Invalid-line declarations require review in rust-toolchain

```scrut
$ "${RUST_AUDIT_CASE_BIN}" invalid-line
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Invalid-line declarations require review in rust-toolchain.toml

```scrut
$ "${RUST_AUDIT_CASE_BIN}" invalid-line modern
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain.toml
```

## Simple fields and comments remain readable

```scrut
$ "${RUST_AUDIT_CASE_BIN}" simple-fields
rows=1
Rust|rustc|1.76.0|1.90.0|rust-toolchain
```

## Additional bare channel lines require manual review

```scrut
$ "${RUST_AUDIT_CASE_BIN}" bare-extra
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Duplicate non-channel keys require review in rust-toolchain

```scrut
$ "${RUST_AUDIT_CASE_BIN}" duplicate-field
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Duplicate non-channel keys require review in rust-toolchain.toml

```scrut
$ "${RUST_AUDIT_CASE_BIN}" duplicate-field modern
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain.toml
```

## Escape values require review in rust-toolchain

```scrut
$ "${RUST_AUDIT_CASE_BIN}" escape
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Escape values require review in rust-toolchain.toml

```scrut
$ "${RUST_AUDIT_CASE_BIN}" escape modern
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain.toml
```

## Control-double values require review in rust-toolchain

```scrut
$ "${RUST_AUDIT_CASE_BIN}" control-double
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Control-double values require review in rust-toolchain.toml

```scrut
$ "${RUST_AUDIT_CASE_BIN}" control-double modern
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain.toml
```

## Control-single values require review in rust-toolchain

```scrut
$ "${RUST_AUDIT_CASE_BIN}" control-single
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain
```

## Control-single values require review in rust-toolchain.toml

```scrut
$ "${RUST_AUDIT_CASE_BIN}" control-single modern
rows=1
Rust|unreadable toolchain pin|unreadable|manual review|rust-toolchain.toml
```

## Literal strings preserve backslashes

```scrut
$ "${RUST_AUDIT_CASE_BIN}" literal-backslash
rows=1
Rust|rustc|1.76.0|1.90.0|rust-toolchain
```
