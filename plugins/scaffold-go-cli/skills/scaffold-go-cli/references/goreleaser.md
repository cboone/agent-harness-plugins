# .goreleaser.yml Template

Use this template for GoReleaser configuration. Replace `PROJECT-NAME` and `PROJECT-DESCRIPTION` with the actual values.

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
  sort: asc
  filters:
    exclude:
      - "^docs:"
      - "^test:"
      - "^chore:"

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
- `-X main.version={{.Version}}` injects the release version at build time
- Builds for Linux, macOS, and Windows on both amd64 and arm64
- Windows archives use zip; everything else uses tar.gz
- Homebrew tap publishes to `GITHUB-USERNAME/homebrew-tap` using `HOMEBREW_TAP_TOKEN`
- `prerelease: auto` marks pre-release tags (e.g., `v1.0.0-rc1`) correctly on GitHub
- The `{{` and `}}` delimiters are GoReleaser template syntax, not Go templates
