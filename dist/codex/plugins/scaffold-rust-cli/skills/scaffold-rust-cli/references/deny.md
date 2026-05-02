# deny.toml Template

Create `deny.toml` in the project root with the following content.

```toml
[advisories]
vulnerability = "deny"
unmaintained = "warn"

[licenses]
unlicensed = "deny"
allow = [
  "MIT",
  "Apache-2.0",
  "BSD-2-Clause",
  "BSD-3-Clause",
  "ISC",
  "Unicode-3.0",
]

[bans]
multiple-versions = "warn"
wildcards = "allow"

[sources]
unknown-registry = "deny"
unknown-git = "deny"
```

## Notes

- `cargo-deny` checks dependency licenses, known vulnerabilities, duplicate crates, and registry sources.
- The `[advisories]` section denies known vulnerabilities and warns on unmaintained crates.
- The `[licenses]` allowlist covers the vast majority of Rust ecosystem crates. Add additional licenses as needed when `cargo deny check` flags a dependency.
- `[bans]` warns on multiple versions of the same crate (diamond dependencies) but does not block the build.
- `[sources]` blocks dependencies from unknown registries or git repositories, which is a supply chain security measure.
- Run `cargo deny check` locally or in CI. The CI template includes a dedicated `deny` job.
