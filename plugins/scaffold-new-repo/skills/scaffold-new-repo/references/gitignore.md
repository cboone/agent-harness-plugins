# .gitignore Templates

Choose the template matching the project type. Every template includes the common entries at the top.

## Common (included in all templates)

```gitignore
# System
.DS_Store

# Agent config
.claude/settings.local.json

# Secrets
.env
.env.*
!.env.example
!.env.sample
*.pem
*.key
*.p12
credentials.json
token.json
```

## Go CLI

```gitignore
# System
.DS_Store

# Agent config
.claude/settings.local.json

# Secrets
.env
.env.*
!.env.example
!.env.sample
*.pem
*.key
*.p12
credentials.json
token.json

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
# System
.DS_Store

# Agent config
.claude/settings.local.json

# Secrets
.env
.env.*
!.env.example
!.env.sample
*.pem
*.key
*.p12
credentials.json
token.json

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
# System
.DS_Store

# Agent config
.claude/settings.local.json

# Secrets
.env
.env.*
!.env.example
!.env.sample
*.pem
*.key
*.p12
credentials.json
token.json
```

## JavaScript

```gitignore
# System
.DS_Store

# Agent config
.claude/settings.local.json

# Secrets
.env
.env.*
!.env.example
!.env.sample
*.pem
*.key
*.p12
credentials.json
token.json
.npmrc

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
# System
.DS_Store

# Agent config
.claude/settings.local.json

# Secrets
.env
.env.*
!.env.example
!.env.sample
*.pem
*.key
*.p12
credentials.json
token.json
config/master.key
config/credentials/*.key

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
# System
.DS_Store

# Agent config
.claude/settings.local.json

# Secrets
.env
.env.*
!.env.example
!.env.sample
*.pem
*.key
*.p12
credentials.json
token.json
```

## Notes

- Templates are intentionally minimal -- add project-specific entries as needed.
- The common entries appear in every template and should not be removed.
- The secrets block covers environment files, cryptographic keys, and service credentials.
- `.env.*` catches variants like `.env.local`, `.env.production`, `.env.staging`, etc. The `!.env.example` and `!.env.sample` negations allow committing safe template env files.
- JavaScript adds `.npmrc` because it can contain registry auth tokens.
- Ruby adds `config/master.key` and `config/credentials/*.key` for Rails encrypted credentials.
- Go CLI includes `bin/` and `dist/` for build outputs; Go library omits them.
- For project types not listed above, the skill attempts to fetch a template from GitHub's gitignore repository.
