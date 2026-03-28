# rust-toolchain.toml Template

Create `rust-toolchain.toml` in the project root with the following content.

```toml
[toolchain]
channel = "stable"
components = ["clippy", "rustfmt"]
```

## Notes

- Pins the project to the stable Rust toolchain, ensuring consistent behavior across developers and CI.
- Including `clippy` and `rustfmt` as components ensures they are installed automatically when anyone clones the project and runs `rustup`.
- To pin to a specific Rust version (e.g., for MSRV), change `channel` to a version string like `"1.85.0"`.
