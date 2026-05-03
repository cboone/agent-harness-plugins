# Scaffold Rust CLI

Scaffold a complete Rust CLI project with Cargo, cargo-deny, cargo-nextest, git-cliff, GitHub Actions CI/CD, and Makefile.

**Type:** Command
**Trigger:** `/scaffold-rust-cli`

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Scaffold Rust CLI** from the available plugins.

## What It Does

Generates the full boilerplate for a new Rust CLI project: `Cargo.toml`, `src/main.rs`, `rust-toolchain.toml`, `rustfmt.toml`, `deny.toml`, `typos.toml`, `cliff.toml`, `Makefile`, `.gitignore`, CI and release workflows, `LICENSE`, `README`, `CHANGELOG`, and directory stubs. Supports optional clap argument parsing and macOS-only project configuration.

## Usage

```text
/scaffold-rust-cli
```

The command prompts for project name, description, and optional features during setup.

## Examples

- "scaffold rust cli": starts the interactive scaffolding process
- "new rust cli": same behavior
- "start a rust cli project": same behavior

## See Also

- [Scaffold New Repo](../scaffold-new-repo/README.md): language-agnostic repo boilerplate (included automatically)
- [Setup Installers](../setup-installers/README.md): set up Homebrew formula and shell install script after scaffolding
- [All plugins](../../../../README.md)
