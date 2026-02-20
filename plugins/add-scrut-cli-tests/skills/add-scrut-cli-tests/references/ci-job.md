# CI Job

GitHub Actions job template for running scrut CLI tests.

## Template

```yaml
test-scrut:
  name: Test CLI (Scrut)
  runs-on: RUNNER_OS
  steps:
    - name: Checkout code
      uses: actions/checkout@v6

    - name: Set up Go
      uses: actions/setup-go@v6
      with:
        cache: true
        go-version: "GO_VERSION"

    - name: Install scrut
      env:
        GH_TOKEN: ${{ github.token }}
      run: |
        mkdir -p "${HOME}/.local/bin"
        echo "${HOME}/.local/bin" >> "${GITHUB_PATH}"
        gh release download --repo facebookincubator/scrut --pattern 'scrut-*-SCRUT_PLATFORM.tar.gz' --dir /tmp
        tar -xzf /tmp/scrut-*-SCRUT_PLATFORM.tar.gz -C /tmp
        cp /tmp/scrut-SCRUT_PLATFORM/scrut "${HOME}/.local/bin/"

    - name: Run scrut CLI tests
      run: make test-scrut
```

## Placeholders

| Placeholder      | Description                                  | Example                         |
| ---------------- | -------------------------------------------- | ------------------------------- |
| `RUNNER_OS`      | GitHub Actions runner OS                     | `macos-latest`, `ubuntu-latest` |
| `GO_VERSION`     | Go version matching the rest of the workflow | `1.25`                          |
| `SCRUT_PLATFORM` | Platform identifier from scrut release assets | `macos-aarch64`, `linux-x86_64` |

## Notes

- Scrut is installed via `gh release download` from `facebookincubator/scrut`. The upstream install script is not used because its `get_latest_version()` function hardcodes `ukautz/scrut`, and it installs to a directory not in `PATH` on GitHub Actions runners.
- The `SCRUT_PLATFORM` value must match the runner OS: use `macos-aarch64` for `macos-latest` and `linux-x86_64` for `ubuntu-latest`.
- The job relies on `make test-scrut`, which handles building the binary and running tests.
- Match the `go-version` and `runs-on` values to the project's existing CI configuration.
- Place this job alongside other test jobs in the workflow. If the workflow uses job dependencies, this job typically depends on the lint job (if any).
