# Cargo.toml Template

Create `Cargo.toml` in the project root with the following content.

Replace `PROJECT-NAME`, `PROJECT-DESCRIPTION`, `GITHUB-USERNAME`, and `COPYRIGHT-HOLDER` with the actual values.

```toml
[package]
name = "PROJECT-NAME"
version = "0.1.0"
edition = "2024"
description = "PROJECT-DESCRIPTION"
license = "MIT"
repository = "https://github.com/GITHUB-USERNAME/PROJECT-NAME"
authors = ["COPYRIGHT-HOLDER"]
categories = ["command-line-utilities"]
keywords = []

[dependencies]
```

## Notes

- `edition = "2024"` uses the latest Rust edition. Requires a recent stable toolchain (the generated `rust-toolchain.toml` handles this).
- `categories` is set to `["command-line-utilities"]` for CLI projects. Update if the project fits additional crates.io categories.
- `keywords` starts empty. Add up to 5 keywords relevant to the project for crates.io discoverability.
- The `[dependencies]` section starts empty. If clap was selected, add `clap = { version = "4", features = ["derive"] }`.
