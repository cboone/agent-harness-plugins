#!/usr/bin/env bash
# Static guard input; never executed.
printf diagnostic >& /dev/null # error-output-allow: intentional presence probe
