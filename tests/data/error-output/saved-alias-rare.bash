#!/usr/bin/env bash
# Static AST input; never executed.
{ exec 3>/dev/null; some-command 2>&3; } 3>&1
