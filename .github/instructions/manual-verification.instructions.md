---
applyTo: "plugins/write-manual-verification-plan/**/*.md"
---

# Manual verification review instructions

- **The macOS system grep supports `--line-buffered`.** Do not identify this option as GNU-only or replace a documented macOS filter on that premise. Validate portability findings against the target binary; `/usr/bin/grep --line-buffered --version` and a matching-input check establish support.
