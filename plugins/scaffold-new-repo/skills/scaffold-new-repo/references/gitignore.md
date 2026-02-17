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
```

## Ruby

```gitignore
# Common
.DS_Store
.env
.claude/settings.local.json

# Ruby
*.code-workspace
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
