#!/usr/bin/env bash
# Static AST input; never executed.
{ f() { some-command 2>&3; }; } 3>&1
