#!/usr/bin/env bash
# Static AST input; never executed.
exec > /dev/null # error-output-allow: static fixture deliberately redirects stdout away from snapshots
some-command 2>&1 # error-output-allow: static fixture deliberately redirects the diagnostic stream
