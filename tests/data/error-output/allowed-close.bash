#!/usr/bin/env bash
# Static guard input; never executed.
some-command 2>&- # error-output-allow: static fixture intentionally closes stderr
