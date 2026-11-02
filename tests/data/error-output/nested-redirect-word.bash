#!/usr/bin/env bash
# Static guard input; never executed.
printf sample > "$(some-command 2>/dev/null)"
