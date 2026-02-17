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
*.pem
*.key
*.p12
credentials.json
token.json
.npmrc

# JavaScript
node_modules/
*.tgz
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
*.pem
*.key
*.p12
credentials.json
token.json
config/master.key
config/credentials/*.key

# Ruby
*.code-workspace
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
- `.env.*` catches variants like `.env.local`, `.env.production`, `.env.staging`, etc.
- JavaScript adds `.npmrc` because it can contain registry auth tokens.
- Ruby adds `config/master.key` and `config/credentials/*.key` for Rails encrypted credentials.
- Go CLI includes `bin/` and `dist/` for build outputs; Go library omits them.
