#!/usr/bin/env bash
# Static guard input; never executed.
printf "literal # data" \
  diagnostic 2>/dev/null # error-output-allow: intentional presence probe
