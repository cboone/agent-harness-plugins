# .goreleaser.yml Template

Use this template for GoReleaser configuration when adding release automation to an existing Go CLI project. Replace `PROJECT-NAME`, `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the actual values.

```yaml
version: 2

builds:
  - main: .
    binary: PROJECT-NAME
    env:
      - CGO_ENABLED=0
    goos:
      - linux
      - darwin
      - windows
    goarch:
      - amd64
      - arm64
    ldflags:
      - -s -w
      - -X main.version={{.Version}}

archives:
  - formats:
      - tar.gz
    format_overrides:
      - goos: windows
        formats:
          - zip
    name_template: "{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}"

checksum:
  name_template: checksums.txt

release:
  prerelease: auto

changelog:
  groups:
    - title: Features
      regexp: '^.*?feat(\(.+\))?\!?:.+$'
      order: 0
    - title: Bug Fixes
      regexp: '^.*?fix(\(.+\))?\!?:.+$'
      order: 1
    - title: Performance
      regexp: '^.*?perf(\(.+\))?\!?:.+$'
      order: 2
    - title: Refactoring
      regexp: '^.*?refactor(\(.+\))?\!?:.+$'
      order: 3
    - title: Documentation
      regexp: '^.*?docs(\(.+\))?\!?:.+$'
      order: 4
    - title: Build
      regexp: '^.*?(build|ci)(\(.+\))?\!?:.+$'
      order: 5
    - title: Other
      order: 999
  filters:
    exclude:
      - "^chore:"
      - "^test:"
      - "^style:"

brews:
  - repository:
      owner: GITHUB-USERNAME
      name: homebrew-tap
      token: "{{ .Env.HOMEBREW_TAP_TOKEN }}"
    directory: Formula
    homepage: "https://github.com/GITHUB-USERNAME/PROJECT-NAME"
    description: "PROJECT-DESCRIPTION"
    license: MIT
    test: |
      assert_match version.to_s, shell_output("#{bin}/PROJECT-NAME --version")
```

## Notes

- Uses GoReleaser v2 config format (`version: 2`)
- `CGO_ENABLED=0` produces static binaries (no C library dependency)
- `-s -w` in ldflags strips debug info and symbol tables (smaller binary)
- `-X main.version={{.Version}}` injects the release version at build time; adjust the path if the version variable lives in a different package (e.g., `-X github.com/USER/REPO/cmd.version={{.Version}}`)
- Builds for Linux, macOS, and Windows on both amd64 and arm64 by default; see `conditional-features.md` for macOS-only projects
- Windows archives use zip; everything else uses tar.gz
- `prerelease: auto` marks pre-release tags (e.g., `v1.0.0-rc1`) correctly on GitHub
- Changelog uses **conventional commit grouping** instead of simple sort-and-filter, organizing entries under headings (Features, Bug Fixes, Refactoring, etc.) for clearer release notes
- The `Other` group with `order: 999` acts as a catch-all for commits that do not match any specific type
- Commits prefixed with `chore:`, `test:`, or `style:` are excluded from the changelog entirely
- Homebrew tap publishes to `GITHUB-USERNAME/homebrew-tap` using `HOMEBREW_TAP_TOKEN` (a PAT with repo scope on the homebrew-tap repository)
- The `{{` and `}}` delimiters are GoReleaser template syntax, not Go templates
