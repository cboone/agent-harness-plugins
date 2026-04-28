# main.rs Template (With Clap)

Create `src/main.rs` with the following content.

Replace `PROJECT-NAME` and `PROJECT-DESCRIPTION` with the actual values.

```rust
use clap::Parser;

/// PROJECT-DESCRIPTION
#[derive(Parser)]
#[command(name = "PROJECT-NAME", version, about)]
struct Args {
    /// Enable verbose output
    #[arg(short, long)]
    verbose: bool,
}

fn main() {
    let args = Args::parse();

    if args.verbose {
        println!("Verbose mode enabled");
    }

    println!("Hello, world!");
}
```

## Notes

- Uses `clap`'s derive API for declarative argument parsing.
- The `#[command]` attribute sets the binary name, pulls version from `Cargo.toml`, and uses the doc comment as the `--help` description.
- Add subcommands by creating additional structs with `#[derive(clap::Subcommand)]` and adding a `#[command(subcommand)]` field to `Args`.
- The `version` attribute in `#[command]` uses `env!("CARGO_PKG_VERSION")` automatically.
