# Upgrade Sources

Resolve latest versions from authoritative sources and record the source used for every candidate. Prefer machine-readable registry or release metadata over scraping human-readable pages.

## Source Selection

| Ecosystem or surface     | Authoritative sources                                                           | Typical lookup method                                           | Confidence notes                                                                   |
| ------------------------ | ------------------------------------------------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| npm and Corepack         | npm registry, package manager metadata, Corepack                                | `npm view`, registry JSON, `corepack use`                       | Highest when registry metadata and lockfile update agree.                          |
| Python                   | PyPI JSON API, uv or pip resolver output, project lockfile                      | `uv lock --upgrade-package`, PyPI JSON, `pip index versions`    | Prefer uv for uv-managed projects and package manager output for lockfile changes. |
| Go modules and tools     | Go module proxy, module tags, GitHub releases for install tools                 | `go list -m -u -json`, `go install` dry run, GitHub API         | Check module path replacements and major-version suffixes.                         |
| Rust crates              | crates.io index, `cargo update`, `cargo metadata`                               | `cargo update -p`, crates.io API                                | Distinguish library compatibility constraints from binary application pins.        |
| Ruby                     | RubyGems API, Bundler resolver                                                  | `bundle update <gem>`, RubyGems versions API                    | Bundler output is preferred when a `Gemfile.lock` exists.                          |
| Swift packages           | Git tags from package remotes, `Package.resolved`                               | `swift package update`, GitHub tags                             | SemVer tags are conventional, but validate package resolution.                     |
| PHP Composer             | Packagist API, Composer resolver                                                | `composer outdated`, `composer update vendor/package`           | Composer constraints may be public library API promises.                           |
| GitHub Actions           | GitHub releases, tags, commit API, action metadata                              | GitHub API, `gh release view`, `gh api repos/.../commits/<ref>` | SHA pins need the version comment or commit ancestry to assess drift.              |
| Reusable workflows       | GitHub releases, tags, workflow repository release notes                        | GitHub API, repository tags                                     | Treat workflow input changes as API changes.                                       |
| Container images         | Docker Hub, GHCR, registry manifest APIs, image labels                          | Registry API, `docker buildx imagetools inspect`                | Tags can be mutable; digest comparison improves confidence.                        |
| Language runtimes        | Official release indexes and toolchain channels                                 | Node.js index, Python downloads, Go downloads, Rust channels    | Runtime upgrades require repo-specific validation beyond version lookup.           |
| Zig and niche toolchains | Official release JSON, project release pages, package manager metadata          | Publisher API or release index                                  | Confidence depends on whether the publisher exposes stable machine-readable data.  |
| Schema URLs              | Schema publisher versioned URLs, Schema Store catalog, project release metadata | Publisher catalog or repository tags                            | Some schemas expose only moving URLs. Mark those as unpinnable, not missing.       |
| Marketplace/plugin data  | Marketplace manifest, local plugin manifests, release tags                      | `jq`, local manifest reads, repository releases                 | Recompute derived catalog state after changing individual plugin versions.         |
| Release tools            | Tool release pages, package registries, action releases                         | GitHub releases, package registry APIs                          | Validate generated release config with the tool's own check or dry-run.            |
| Unclassified literals    | The publisher identified from surrounding context                               | Context-specific                                                | Keep confidence low until the upstream owner is known.                             |

## Lookup Policy

1. Record the exact audit date from `date`.
1. Resolve upstream from the closest owner of the version surface.
1. Use the repository's native package manager when it owns lockfile changes.
1. Prefer official APIs and registry metadata over blog posts, search results, or mirrors.
1. Check changelogs and migration notes for major, runtime, toolchain, and reusable workflow upgrades.
1. If the source of truth cannot be identified, keep the candidate and mark source `Unknown`.
1. If the source is unreachable, keep the candidate and mark status `Blocked`.

## Confidence Labels

| Confidence | Use when                                                                                            |
| ---------- | --------------------------------------------------------------------------------------------------- |
| High       | Official registry or release metadata identifies the latest version and the package manager agrees. |
| Medium     | Official tags or releases exist, but changelog, resolver, or lockfile confirmation is incomplete.   |
| Low        | The candidate is inferred from context, a moving channel, a mutable tag, or incomplete metadata.    |
| Unknown    | No authoritative source could be resolved.                                                          |

## Applying Sources to Edits

- Use package manager commands for dependencies and lockfiles.
- Use targeted structured edits for workflow refs, runtime files, schema URLs, marketplace metadata, and release config.
- Preserve existing held-major or held-channel policy unless the user explicitly selects a major or channel migration.
- Never downgrade a SHA, digest, or exact pin to a mutable tag while upgrading.
- Keep a blocked candidate in the summary with the source attempted and the next information needed.
