#!/usr/bin/env bash
# Static guard input; never executed.
some-command 2>/dev/null # ordinary comment \
true # error-output-allow: separate probe
