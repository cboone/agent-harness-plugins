#!/usr/bin/env bash
# Static AST input; never executed.
{ some-command 2>&3; } 3>&1 1>/dev/null
