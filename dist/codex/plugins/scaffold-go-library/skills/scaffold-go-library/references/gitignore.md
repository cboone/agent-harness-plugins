# .gitignore Template

Use this template for `.gitignore`. No replacements needed.

```text
# If you prefer the allow list template instead of the deny list, see community template:
# https://github.com/github/gitignore/blob/main/community/Golang/Go.AllowList.gitignore
#
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
profile.cov

# Dependency directories (remove the comment below to include it)
# vendor/

# Go workspace file
go.work
go.work.sum

# goreleaser output
dist/

# env file
.env

# Editor/IDE
# .idea/
# .vscode/
```

## Notes

- No binary name entry -- libraries produce no binary
- No `bin/` directory -- libraries have no build output directory
- Coverage artifacts are ignored to keep the repo clean
- If a `.gitignore` already exists, merge these entries rather than overwriting
