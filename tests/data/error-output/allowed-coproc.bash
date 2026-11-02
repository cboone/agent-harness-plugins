#!/usr/bin/env bash
# Static AST input; never executed.
coproc { some-command 2>&1; } # error-output-allow: static fixture deliberately retains the merged coprocess output
