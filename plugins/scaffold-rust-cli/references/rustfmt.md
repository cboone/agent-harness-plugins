# rustfmt.toml Template

Create `rustfmt.toml` in the project root with the following content.

```toml
edition = "2024"
max_width = 100
use_small_heuristics = "Default"
```

## Notes

- `edition` must match the edition in `Cargo.toml` so rustfmt parses syntax correctly.
- `max_width = 100` allows slightly longer lines than the default 100 (which is already the default, but explicit is better).
- `use_small_heuristics = "Default"` lets rustfmt use sensible defaults for things like function call width and struct literal width.
- This file applies to the entire workspace. No per-crate config is needed.
