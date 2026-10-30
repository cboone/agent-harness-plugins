#!/usr/bin/env bash
# Static guard input; never executed.
printf diagnostic 2>/dev/null \\
true # error-output-allow: separate probe
