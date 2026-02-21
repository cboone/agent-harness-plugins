# README Template

Generate `README.md` in the project root.

Replace these placeholders:

- `PLUGIN-NAME`: the plugin name in kebab-case (e.g., `tmux-my-plugin`)
- `PLUGIN-TITLE`: the plugin name in title case (e.g., `Tmux My Plugin`)
- `PLUGIN-DESCRIPTION`: the short description
- `GITHUB-USERNAME`: the user's GitHub username
- `OPTIONS-TABLE`: a Markdown table of configurable options (see below)

````markdown
# PLUGIN-TITLE

PLUGIN-DESCRIPTION

## Install

### TPM Redux (recommended)

Add this line to your `tmux.conf`:

```bash
set -g @plugin 'GITHUB-USERNAME/PLUGIN-NAME'
```

Then press `prefix` + `I` to install.

Requires [TPM Redux](https://github.com/tmux-plugins/tpm). Install:

```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
```

### Manual

Clone the repo:

```bash
git clone https://github.com/GITHUB-USERNAME/PLUGIN-NAME ~/.tmux/plugins/PLUGIN-NAME
```

Add this line to your `tmux.conf`:

```bash
run-shell ~/.tmux/plugins/PLUGIN-NAME/PLUGIN-NAME.tmux
```

Then reload your tmux config (e.g., `tmux source-file ~/.tmux.conf` or `tmux source-file ~/.config/tmux/tmux.conf`).

### TPM (deprecated)

> [!WARNING]
> The [original TPM](https://github.com/tmux-plugins/tpm/tree/master) is no longer maintained.
> Consider switching to [TPM Redux](https://github.com/tmux-plugins/tpm).

Add this line to your `tmux.conf`:

```bash
set -g @plugin 'GITHUB-USERNAME/PLUGIN-NAME'
```

Then press `prefix` + `I` to install.

## Configuration

OPTIONS-TABLE

## License

[MIT](./LICENSE)
````

## Options Table

Generate a Markdown table with one row per configurable option:

```markdown
| Option                | Default   | Description                |
| --------------------- | --------- | -------------------------- |
| `@PLUGIN-NAME-option` | `default` | What this option controls. |
```

If the user did not specify any options, generate a single example option:

```markdown
| Option                 | Default | Description                                            |
| ---------------------- | ------- | ------------------------------------------------------ |
| `@PLUGIN-NAME-enabled` | `on`    | Enable or disable the plugin. Set to `off` to disable. |
```

## Notes

- The three install sections (TPM Redux, Manual, TPM deprecated) match the pattern used in existing tmux plugins.
- Manual install uses `~/.tmux/plugins/`, matching the directory TPM Redux uses by default.
- The TPM deprecated section includes a warning admonition directing users to TPM Redux.
