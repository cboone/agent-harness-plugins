# Hadolint

Dockerfile linter that validates Dockerfile best practices and inline bash via ShellCheck.

## When to Offer

When `Dockerfile`, `*.dockerfile`, or `docker-compose.yml` is detected.

## Install

```bash
# Homebrew (recommended)
brew install hadolint

# Docker (alternative, no local install)
docker run --rm -i hadolint/hadolint < Dockerfile
```

## Config

Create `.hadolint.yaml` in the project root:

```yaml
ignored:
  # DL3008: Pin versions in apt-get install
  - DL3008
  # DL3018: Pin versions in apk add
  - DL3018

trustedRegistries:
  - docker.io
  - gcr.io
  - ghcr.io
```

## Commands

```bash
# Lint the default Dockerfile
hadolint Dockerfile

# Lint a specific Dockerfile
hadolint path/to/Dockerfile

# Lint with specific ignored rules
hadolint --ignore DL3008 Dockerfile
```

## Notes

- Hadolint checks both Dockerfile instructions and inline shell commands (via ShellCheck integration).
- `DL3008` and `DL3018` (pin versions in package installs) are commonly ignored in development Dockerfiles but should be enabled for production images.
- `trustedRegistries` restricts which registries are allowed in `FROM` instructions. Adapt to the project's registry policy.
- Hadolint has no auto-fix mode. All issues must be resolved manually.
- The config file is optional. Hadolint works out of the box with sensible defaults.
