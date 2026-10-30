#!/usr/bin/env bash
# Static AST input; never executed.
printf "%s" "$(some-command 2>&3)" 3>&1
