# cliff.toml Template

Create `cliff.toml` in the project root with the following content.

```toml
[changelog]
header = """
# Changelog

All notable changes to this project will be documented in this file.\n
"""
body = """
{% if version %}\
    ## [{{ version | trim_start_matches(pat="v") }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
    ## [Unreleased]
{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}
    ### {{ group | upper_first }}
    {% for commit in commits %}
        - {{ commit.message | upper_first }}\
          {% if commit.breaking %} (**BREAKING**){% endif %}\
    {% endfor %}
{% endfor %}\n
"""
trim = true

[git]
conventional_commits = true
filter_unconventional = true
commit_parsers = [
  { message = "^feat", group = "Features" },
  { message = "^fix", group = "Bug fixes" },
  { message = "^doc", group = "Documentation" },
  { message = "^perf", group = "Performance" },
  { message = "^refactor", group = "Refactoring" },
  { message = "^style", group = "Style" },
  { message = "^test", group = "Testing" },
  { message = "^chore", group = "Miscellaneous" },
  { message = "^ci", group = "CI" },
  { message = "^deps", group = "Dependencies" },
]
```

## Notes

- `git-cliff` generates changelogs from conventional commit messages. This is the Rust ecosystem's equivalent of GoReleaser's changelog feature.
- The `[changelog]` section defines the output format using Tera templates.
- The `[git]` section configures conventional commit parsing. Commits that do not match any parser are filtered out by `filter_unconventional = true`.
- Commit groups (Features, Bug fixes, etc.) are sorted alphabetically in the output.
- Run `git cliff -o CHANGELOG.md` to generate the changelog, or use `make changelog`.
- Install git-cliff with `cargo install git-cliff` or via your system package manager.
