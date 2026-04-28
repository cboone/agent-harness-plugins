# .goreleaser.yml Template

Use this template for GoReleaser configuration. Replace `PROJECT-NAME`, `PROJECT-DESCRIPTION`, and `GITHUB-USERNAME` with the actual values.

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

homebrew_casks:
  - binaries:
      - PROJECT-NAME
    repository:
      owner: GITHUB-USERNAME
      name: homebrew-tap
      token: "{{ .Env.HOMEBREW_TAP_TOKEN }}"
    homepage: "https://github.com/GITHUB-USERNAME/PROJECT-NAME"
    description: "PROJECT-DESCRIPTION"
    license: MIT
    hooks:
      post:
        install: |
          system_command "/usr/bin/xattr", args: ["-dr", "com.apple.quarantine", "#{staged_path}/PROJECT-NAME"]
```

## Notes

- Uses GoReleaser v2 config format (`version: 2`)
- `CGO_ENABLED=0` produces static binaries (no C library dependency)
- `-s -w` in ldflags strips debug info and symbol tables (smaller binary)
- `-X main.version={{.Version}}` injects the release version at build time
- Builds for Linux, macOS, and Windows on both amd64 and arm64
- Windows archives use zip; everything else uses tar.gz
- Uses `homebrew_casks:` (GoReleaser v2.10+) instead of the deprecated `brews:`. Casks are the correct artifact type for pre-compiled binaries distributed via GoReleaser
- The `directory` field defaults to `Casks` and is omitted; do not set it to `Formula`
- `binaries:` lists binary names to install, replacing the formula `install:` block
- Casks do not support `test:` blocks; version testing is handled differently in the Homebrew cask ecosystem
- The quarantine removal hook prevents "App is damaged" Gatekeeper errors on macOS for unsigned binaries. The `hooks.post.install` field is a string (not a list)
- Homebrew tap publishes to `GITHUB-USERNAME/homebrew-tap` using `HOMEBREW_TAP_TOKEN` (see "Reference: HOMEBREW_TAP_TOKEN Setup" for creation and configuration)
- `prerelease: auto` marks pre-release tags (e.g., `v1.0.0-rc1`) correctly on GitHub
- The `{{` and `}}` delimiters are GoReleaser template syntax, not Go templates
