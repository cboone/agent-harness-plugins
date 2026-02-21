# Python

## Tools

- **Ruff**: Extremely fast Python linter and formatter. Replaces black, isort, flake8, pyflakes, pycodestyle, and more. Written in Rust.

## Detection

Python projects are detected by:

- `pyproject.toml`
- `setup.py`, `setup.cfg`
- `requirements.txt`
- `Pipfile`
- `.venv/`, `venv/` directories

## Install

```bash
# uv (preferred)
uv add --dev ruff

# uv pip (alternative, when not using a uv project)
uv pip install ruff
```

## Config

Add to `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py313"
line-length = 88

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "SIM", # flake8-simplify
    "RUF", # ruff-specific rules
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

## Makefile Targets

```makefile
.PHONY: lint format

lint: ## Run ruff linter
	ruff check .

format: ## Format Python code
	ruff format .
	ruff check --fix .
```

## Notes

- Ruff is a single tool that replaces an entire ecosystem (black, isort, flake8, and dozens of flake8 plugins).
- The `select` list above is a sensible starting set. Ruff supports 800+ rules from 50+ plugins.
- `ruff check --fix` applies safe auto-fixes. `ruff format` handles code formatting.
- Always use `uv` to install. Use `uv add --dev` for uv-managed projects, or `uv pip install` otherwise.
- Ruff reads config from `pyproject.toml`, `ruff.toml`, or `.ruff.toml`.
