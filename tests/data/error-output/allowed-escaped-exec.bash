#!/usr/bin/env bash
# Static AST input; never executed.
\exec 1>/dev/null; some-command 2>&1 # error-output-allow: static fixture deliberately redirects the diagnostic stream
