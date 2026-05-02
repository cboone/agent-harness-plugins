# .goreleaser.yml Template

Use this template for `.goreleaser.yml`. Replace `PROJECT-NAME`, `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the actual values.

````yaml
# goreleaser configuration for PROJECT-NAME
# https://goreleaser.com

version: 2

# PROJECT-NAME is a library, not a binary
builds:
  - skip: true

changelog:
  sort: asc
  groups:
    - title: Features
      regexp: '^.*?feat(\([[:word:]]+\))??!?:.+$'
      order: 0
    - title: Bug Fixes
      regexp: '^.*?fix(\([[:word:]]+\))??!?:.+$'
      order: 1
    - title: Documentation
      regexp: '^.*?docs(\([[:word:]]+\))??!?:.+$'
      order: 2
    - title: Performance
      regexp: '^.*?perf(\([[:word:]]+\))??!?:.+$'
      order: 3
    - title: Refactoring
      regexp: '^.*?refactor(\([[:word:]]+\))??!?:.+$'
      order: 4
    - title: Tests
      regexp: '^.*?test(\([[:word:]]+\))??!?:.+$'
      order: 5
    - title: Build
      regexp: '^.*?(build|ci)(\([[:word:]]+\))??!?:.+$'
      order: 6
    - title: Other
      order: 999
  filters:
    exclude:
      - "^chore:"
      - "^style:"

release:
  header: |
    ## PROJECT-NAME {{ .Tag }}

    PROJECT-DESCRIPTION

    ### Installation

    ```bash
    go get github.com/GITHUB-USERNAME/PROJECT-NAME@{{ .Tag }}
    ```
  footer: |
    **Full Changelog**: https://github.com/GITHUB-USERNAME/PROJECT-NAME/compare/{{ .PreviousTag }}...{{ .Tag }}
````

## Notes

- `builds: [{skip: true}]` tells GoReleaser this is a library with no binary to compile
- The changelog groups commits by conventional commit type for organized release notes
- `chore:` and `style:` commits are excluded from the changelog
- The release header includes a `go get` installation command with the specific tag
- No Homebrew section -- libraries are installed via `go get`, not Homebrew
- The footer links to the full diff between tags on GitHub
