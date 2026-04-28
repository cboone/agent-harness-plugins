# .gitignore Template

Use this template for the project `.gitignore`. Replace `PROJECT-NAME` with the actual binary name.

```gitignore
# Binary
/PROJECT-NAME
/bin/
/dist/

# Binaries for programs and plugins
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary, built with `go test -c`
*.test

# Code coverage profiles and other test artifacts
*.out
coverage.*
*.coverprofile

# Go workspace files
go.work
go.work.sum

# Environment
.env

# Dependency directories
# vendor/
```

## Notes

- The binary name at the top prevents accidentally committing a built binary in the project root
- `bin/` matches the Makefile output directory
- `dist/` is created by GoReleaser during release builds
- `go.work` and `go.work.sum` are workspace files for multi-module setups (not committed)
- `.env` prevents accidentally committing secrets
