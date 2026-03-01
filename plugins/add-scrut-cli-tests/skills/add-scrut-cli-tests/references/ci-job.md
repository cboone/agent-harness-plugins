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

    LANGUAGE_SETUP_STEPS

    - name: Install scrut
      env:
        GH_TOKEN: ${{ github.token }}
      run: |
        mkdir -p "${HOME}/.local/bin"
        echo "${HOME}/.local/bin" >> "${GITHUB_PATH}"
        gh release download SCRUT_VERSION --repo facebookincubator/scrut --pattern 'scrut-SCRUT_VERSION-SCRUT_PLATFORM.tar.gz' --dir /tmp
        tar -xzf /tmp/scrut-SCRUT_VERSION-SCRUT_PLATFORM.tar.gz -C /tmp
        cp /tmp/scrut-SCRUT_PLATFORM/scrut "${HOME}/.local/bin/"

    - name: Run scrut CLI tests
      run: make test-scrut
```

## Placeholders

| Placeholder            | Description                                                         | Example                         |
| ---------------------- | ------------------------------------------------------------------- | ------------------------------- |
| `RUNNER_OS`            | GitHub Actions runner OS                                            | `macos-latest`, `ubuntu-latest` |
| `LANGUAGE_SETUP_STEPS` | Language setup steps copied from the project's existing CI workflow | (see Notes)                     |
| `SCRUT_VERSION`        | Pinned scrut release tag                                            | `v0.4.3`                        |
| `SCRUT_PLATFORM`       | Platform identifier from scrut release assets                       | `macos-aarch64`, `linux-x86_64` |

## Notes

- `LANGUAGE_SETUP_STEPS` should be copied from the project's existing CI workflow. Common examples:
  - **Go**: `actions/setup-go@v6` with `go-version` and caching settings matching the existing workflow
  - **Swift**: Swift is preinstalled on macOS runners; for Ubuntu runners, use a Swift setup action or install step
  - **Rust**: `dtolnay/rust-toolchain` with the appropriate toolchain version
  - **Python**: `actions/setup-python@v5` with `python-version` matching the existing workflow
  - **Ruby**: `ruby/setup-ruby@v1` with `ruby-version` matching the existing workflow
  - **Shell**: no language setup step needed; remove the placeholder entirely
- Copy the language setup verbatim from the existing CI workflow to ensure version consistency and caching configuration are preserved.
- Scrut is installed via `gh release download` from `facebookincubator/scrut`. The upstream install script is not used because its `get_latest_version()` function hardcodes `ukautz/scrut`, and it installs to a directory not in `PATH` on GitHub Actions runners.
- The `SCRUT_VERSION` tag pins the download to a specific release for reproducible builds. Check [scrut releases](https://github.com/facebookincubator/scrut/releases) for available versions.
- Scrut does not currently publish checksums or signatures with its releases, so integrity verification is not yet possible. If checksums become available in the future, add a verification step after the download.
- The `SCRUT_PLATFORM` value must match the runner OS: use `macos-aarch64` for `macos-latest` and `linux-x86_64` for `ubuntu-latest`.
- The job relies on `make test-scrut`, which handles building the binary (if applicable) and running tests.
- Match the `runs-on` value and language setup steps to the project's existing CI configuration.
- Place this job alongside other test jobs in the workflow. If the workflow uses job dependencies, this job typically depends on the lint job (if any).
