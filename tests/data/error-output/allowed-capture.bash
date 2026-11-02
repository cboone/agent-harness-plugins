#!/usr/bin/env bash
# Static guard input; never executed.
output="$(printf diagnostic 2>&1)" # error-output-allow: custom replay protocol reports child errors
