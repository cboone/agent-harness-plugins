# Error output guard

The fixture copies static samples into an isolated repository tree. Samples never
run. Each rejection must come from the error-output rule, and reasoned probes and
stdout-only queries remain accepted.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

## Allowed probe

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allowed-probe
All Git consumers reset their fixture environment.
```

## Allowed capture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allowed-capture
All Git consumers reset their fixture environment.
```

## Allowed continued

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allowed-continued
All Git consumers reset their fixture environment.
```

## Live stderr

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" live-stderr
All Git consumers reset their fixture environment.
```

## Discard

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" discard
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Append discard

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" append-discard
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Combined discard

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" combined-discard
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Capture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" capture
tests/fixtures/output-sample: use capture_child for retained diagnostics
[1]
```

## File capture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" file-capture
tests/fixtures/output-sample: use capture_child for retained diagnostics
[1]
```

## Continued discard

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" continued-discard
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Multiline capture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" multiline-capture
tests/fixtures/output-sample: use capture_child for retained diagnostics
[1]
```

## Empty reason

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" empty-reason
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Next line reason

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" next-line-reason
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Shipped discard

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" discard shipped
plugins/workmux/scripts/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Shipped capture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" capture shipped
plugins/workmux/scripts/output-sample: use capture_child for retained diagnostics
[1]
```

## Tooling discard

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" discard tooling
bin/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Tooling capture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" capture tooling
bin/output-sample: use capture_child for retained diagnostics
[1]
```

## Shorthand discard

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" shorthand-discard
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Shorthand capture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" shorthand-capture
tests/fixtures/output-sample: use capture_child for retained diagnostics
[1]
```

## Split discard token

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" split-discard-token
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Split capture token

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" split-capture-token
tests/fixtures/output-sample: shfmt cannot parse shell input; a named parse exception needs a reason
[1]
```

## Blank boundary

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" blank-boundary
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Comment boundary

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" comment-boundary
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Comment backslash

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" comment-backslash
tests/fixtures/output-sample: shfmt AST is unsafe for this shell input; a named parse exception needs a reason
[1]
```

## Even backslashes

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" even-backslashes
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## Numeric shorthand file

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" numeric-shorthand-file
tests/fixtures/output-sample: use capture_child for retained diagnostics
[1]
```

## Allowed shorthand

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allowed-shorthand
All Git consumers reset their fixture environment.
```

## Live descriptor

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" live-descriptor
All Git consumers reset their fixture environment.
```

## Allowed hash text

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allowed-hash-text
All Git consumers reset their fixture environment.
```

## Pending at eof

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" pending-at-eof
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST quoted hash token split in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" quoted-hash-token-split
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST stderr output close in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" stderr-output-close
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST stderr input close in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" stderr-input-close
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST quoted hash token split in scrut

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" quoted-hash-token-split scrut
tests/scrut/output-sample.md#block-2: retain child errors or add # error-output-allow: reason
[1]
```

## AST stderr output close in scrut

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" stderr-output-close scrut
tests/scrut/output-sample.md#block-2: retain child errors or add # error-output-allow: reason
[1]
```

## AST stderr input close in scrut

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" stderr-input-close scrut
tests/scrut/output-sample.md#block-2: retain child errors or add # error-output-allow: reason
[1]
```

## AST move stderr output in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" move-stderr-output
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST move stderr input in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" move-stderr-input
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST move stderr self in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" move-stderr-self
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST quoted fake reason in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" quoted-fake-reason
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST nested redirect word in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-redirect-word
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST embedded string in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" embedded-string
All Git consumers reset their fixture environment.
```

## AST scope embedded in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" scope-embedded
embedded literal is explicitly listed outside AST coverage
```

## AST live merge in scrut

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" live-merge scrut
All Git consumers reset their fixture environment.
```

## AST live merge in scrut-stderr

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" live-merge scrut-stderr
tests/scrut/output-sample.md#block-2: use capture_child for retained diagnostics
[1]
```

## AST allowed close in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allowed-close
All Git consumers reset their fixture environment.
```

## AST malformed shell in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" malformed-shell
tests/fixtures/output-sample: shfmt cannot parse shell input; a named parse exception needs a reason
[1]
```

## AST malformed shell in scrut

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" malformed-shell scrut
tests/scrut/output-sample.md#block-2: shfmt cannot parse shell input; a named parse exception needs a reason
[1]
```

## AST allow parse in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allow-parse
All Git consumers reset their fixture environment.
```

## AST allow parse in scrut

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allow-parse scrut
All Git consumers reset their fixture environment.
```

## AST stale parse in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" stale-parse
tests/fixtures/output-sample: parse exception is unused; shell input parses successfully
[1]
```

## AST empty policy reason in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" empty-policy-reason 2>&1
error-output policy must contain unique names and nonempty reasons
[1]
```

## AST non bash in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" non-bash
tests/fixtures/output-sample.py: non-Bash source needs a named exclusion with a reason
[1]
```

## AST allow non bash in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allow-non-bash
All Git consumers reset their fixture environment.
```

## AST scope non bash in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" scope-non-bash
tests/fixtures/output-sample.py: Static fixture input is intentionally outside AST coverage and is never executed.
```

## AST cross block in fixture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" cross-block
shfmt AST unit boundaries or structure are invalid; no shell units accepted
[1]
```

## AST named continued-comment exception

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allow-comment
All Git consumers reset their fixture environment.
```

## AST leading zero discard

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" leading-zero-discard
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST leading zero close

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" leading-zero-close
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST leading zero move

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" leading-zero-move
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST escaped stderr move

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" escaped-stderr-move
tests/fixtures/output-sample: retain child errors or add # error-output-allow: reason
[1]
```

## AST pipe both

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" pipe-both
tests/fixtures/output-sample: use capture_child for retained diagnostics
[1]
```

## Non-Bash fixture without a shebang is not silently omitted

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" non-bash-js
tests/fixtures/output-sample.js: non-Bash source needs a named exclusion with a reason
[1]
```

## Named non-Bash fixture without a shebang is explicit

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allow-js
All Git consumers reset their fixture environment.
```

## Inherited zero discard

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-zero-discard scrut
tests/scrut/output-sample.md#block-2: retain child errors or add # error-output-allow: reason
[1]
```

## Inherited inout discard

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-inout-discard scrut
tests/scrut/output-sample.md#block-2: retain child errors or add # error-output-allow: reason
[1]
```

## Inherited closed stdout

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-closed-stdout scrut
tests/scrut/output-sample.md#block-2: retain child errors or add # error-output-allow: reason
[1]
```

## Inherited null alias

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-null-alias scrut
tests/scrut/output-sample.md#block-2: retain child errors or add # error-output-allow: reason
[1]
```

## Inherited file capture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-file-capture scrut
tests/scrut/output-sample.md#block-2: use capture_child for retained diagnostics
[1]
```

## Inherited saved stdout

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-saved-stdout scrut
All Git consumers reset their fixture environment.
```

## Inherited live self

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-live-self scrut
All Git consumers reset their fixture environment.
```

## Inherited live stderr

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-live-stderr scrut
All Git consumers reset their fixture environment.
```

## Inherited moved stdout

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-moved-stdout scrut
All Git consumers reset their fixture environment.
```

## Inherited zero pipeline

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-zero-pipeline scrut
tests/scrut/output-sample.md#block-2: retain child errors or add # error-output-allow: reason
[1]
```

## Inherited function alias

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-function-alias scrut
tests/scrut/output-sample.md#block-2: use capture_child for retained diagnostics
[1]
```

## Inherited substitution alias

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" nested-substitution-alias scrut
tests/scrut/output-sample.md#block-2: use capture_child for retained diagnostics
[1]
```

## Exec stdout capture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" exec-stdout-capture scrut
tests/scrut/output-sample.md#block-2: unresolved stream context (exec redirection); add # error-output-allow: reason
[1]
```

## An allowed exec does not exempt a later stderr merge

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allowed-exec-unreasoned-merge scrut
tests/scrut/output-sample.md#block-2: use capture_child for retained diagnostics
[1]
```

## Both the exec and later stderr merge have reasons

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allowed-exec-reasoned-merge scrut
All Git consumers reset their fixture environment.
```

## Builtin exec stdout capture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" builtin-exec-stdout-capture scrut
tests/scrut/output-sample.md#block-2: unresolved stream context (exec redirection); add # error-output-allow: reason
[1]
```

## Command exec stdout capture

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" command-exec-stdout-capture scrut
tests/scrut/output-sample.md#block-2: unresolved stream context (exec redirection); add # error-output-allow: reason
[1]
```

## Assignment redirects do not persist as exec redirects

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" assignment-stdout-query scrut
All Git consumers reset their fixture environment.
```

## Named parse exception rejects crash

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" parser-crash 2>&1 # error-output-allow: snapshot asserts the unexpected parser diagnostic and failure status
tests/fixtures/output-sample: unexpected shfmt failure (status 139) while checking a parse exception
stub parser crash
[1]
```

## Named parse exception rejects terminated

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" parser-terminated 2>&1 # error-output-allow: snapshot asserts the unexpected parser diagnostic and failure status
tests/fixtures/output-sample: unexpected shfmt failure (status 143) while checking a parse exception
stub parser termination
[1]
```

## Named parse exception rejects io

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" parser-io 2>&1 # error-output-allow: snapshot asserts the unexpected parser diagnostic and failure status
tests/fixtures/output-sample: unexpected shfmt failure (status 1) while checking a parse exception
stub parser input I/O failure
[1]
```

## Named parse exception rejects empty

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" parser-empty 2>&1 # error-output-allow: snapshot asserts the unexpected parser diagnostic and failure status
tests/fixtures/output-sample: unexpected shfmt failure (status 1) while checking a parse exception
[1]
```

## Named parse exception rejects invalid ast

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" parser-invalid-ast 2>&1 # error-output-allow: snapshot asserts the unexpected parser diagnostic and failure status
tests/fixtures/output-sample: shfmt returned an invalid AST while checking a parse exception
[1]
```

## Rare context escaped exec rare

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" escaped-exec-rare scrut
tests/scrut/output-sample.md#block-2: unresolved stream context (escaped or quoted exec); add # error-output-allow: reason
[1]
```

## Rare context quoted exec rare

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" quoted-exec-rare scrut
tests/scrut/output-sample.md#block-2: unresolved stream context (exec redirection); add # error-output-allow: reason
[1]
```

## Rare context ansi exec rare

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" ansi-exec-rare scrut
tests/scrut/output-sample.md#block-2: unresolved stream context (escaped or quoted exec); add # error-output-allow: reason
[1]
```

## Rare context coproc rare

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" coproc-rare scrut
tests/scrut/output-sample.md#block-2: unresolved stream context (coproc); add # error-output-allow: reason
[1]
```

## Rare context named coproc rare

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" named-coproc-rare scrut
tests/scrut/output-sample.md#block-2: unresolved stream context (coproc); add # error-output-allow: reason
[1]
```

## Rare context saved alias rare

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" saved-alias-rare scrut
tests/scrut/output-sample.md#block-2: unresolved stream context (exec redirection); add # error-output-allow: reason
[1]
```

## Rare context composed exec rare

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" composed-exec-rare scrut
tests/scrut/output-sample.md#block-2: unresolved stream context (exec redirection); add # error-output-allow: reason
[1]
```

## Rare context ordinary variable query

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" ordinary-variable-query scrut
All Git consumers reset their fixture environment.
```

## Rare context ordinary variable merge

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" ordinary-variable-merge scrut
All Git consumers reset their fixture environment.
```

## Rare context quoted command query

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" quoted-command-query scrut
All Git consumers reset their fixture environment.
```

## Rare context exec query

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" exec-query scrut
All Git consumers reset their fixture environment.
```

## Rare context allowed escaped exec

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allowed-escaped-exec scrut
All Git consumers reset their fixture environment.
```

## Rare context allowed coproc

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" allowed-coproc scrut
All Git consumers reset their fixture environment.
```

## Input-open failure cannot reuse a syntax diagnostic

```scrut
$ "${ERROR_OUTPUT_GUARD_BIN}" parser-input-open
missing-input failures are not syntax exceptions
```
