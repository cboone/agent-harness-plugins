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
        SCRUT_RELEASE_REPO: facebookincubator/scrut
      run: |
        curl --proto '=https' --tlsv1.2 -sSf https://facebookincubator.github.io/scrut/install.sh | sh

    - name: Run scrut CLI tests
      run: make test-scrut
```

## Placeholders

| Placeholder  | Description                                  | Example                         |
| ------------ | -------------------------------------------- | ------------------------------- |
| `RUNNER_OS`  | GitHub Actions runner OS                     | `macos-latest`, `ubuntu-latest` |
| `GO_VERSION` | Go version matching the rest of the workflow | `1.25`                          |

## Notes

- Scrut is installed via its official install script, which downloads a pre-built binary. No Rust toolchain is required.
- `SCRUT_RELEASE_REPO` must be set to `facebookincubator/scrut` because the install script defaults to `ukautz/scrut`, which has release tags that break the download URL.
- The job relies on `make test-scrut`, which handles building the binary and running tests.
- Match the `go-version` and `runs-on` values to the project's existing CI configuration.
- Place this job alongside other test jobs in the workflow. If the workflow uses job dependencies, this job typically depends on the lint job (if any).
