# .gitignore Templates

Choose the template matching the project type. Every template includes the common entries at the top.

## Common (included in all templates)

```gitignore
.DS_Store
.env
.claude/settings.local.json
```

## Go CLI

```gitignore
# Common
.DS_Store
.env
.claude/settings.local.json

# Go
*.exe
*.test
*.out
coverage.*
go.work
go.work.sum
bin/
dist/
```

## Go Library

```gitignore
# Common
.DS_Store
.env
.claude/settings.local.json

# Go
*.exe
*.test
*.out
coverage.*
go.work
go.work.sum
```

## Shell

```gitignore
# Common
.DS_Store
.env
.claude/settings.local.json
```

## JavaScript

```gitignore
# Common
.DS_Store
.env
.claude/settings.local.json

# JavaScript
node_modules/
*.tgz
*.tsbuildinfo
coverage/
dist/
.next/
.nuxt/
*.log
```

## Ruby

```gitignore
# Common
.DS_Store
.env
.claude/settings.local.json

# Ruby
*.gem
*.rbc
.bundle/
vendor/bundle
pkg/
coverage/
spec/reports/
.byebug_history
```

## Pascal

```gitignore
# Common
.DS_Store
.env
.claude/settings.local.json

# Pascal
*.o
*.ppu
*.compiled
*.exe
*.dll
*.so
lib/
backup/
*.lps
*.bak
```

## Python

```gitignore
# Common
.DS_Store
.env
.claude/settings.local.json

# Python
__pycache__/
*.pyc
*.pyo
.venv/
dist/
build/
*.egg-info/
.pytest_cache/
*.egg
.coverage
htmlcov/
```

## Rust

```gitignore
# Common
.DS_Store
.env
.claude/settings.local.json

# Rust
target/
*.pdb
**/*.rs.bk
```

## Swift

```gitignore
# Common
.DS_Store
.env
.claude/settings.local.json

# Swift
xcuserdata/
.build/
*.ipa
*.dSYM.zip
*.dSYM
Carthage/Build/
Package.resolved
```

## Generic

```gitignore
# Common
.DS_Store
.env
.claude/settings.local.json
```

## Notes

- Templates are intentionally minimal -- add project-specific entries as needed.
- The common entries appear in every template and should not be removed.
- Go CLI includes `bin/` and `dist/` for build outputs; Go library omits them.
- For project types not listed above, the skill attempts to fetch a template from GitHub's gitignore repository.
