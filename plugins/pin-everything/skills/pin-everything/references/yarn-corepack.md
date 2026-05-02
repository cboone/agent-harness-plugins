# Yarn (Corepack) and `.yarnrc.yml` Hardening

How to integrity-pin Yarn via Corepack, make `.yarnrc.yml` security defaults explicit, and detect harmful Corepack-migration side effects.

## Why Integrity-Pin Yarn

`package.json`'s `"packageManager": "yarn@4.14.1"` field tells Corepack which Yarn to use, but the version alone is not enough — Corepack will fetch the matching tarball from `repo.yarnpkg.com` at install time. If that tarball has been tampered with (or if the registry is compromised), every developer and every CI run silently picks up the malicious binary.

The `+sha512.<hash>` suffix turns the field into a cryptographic commitment to a specific tarball: `"packageManager": "yarn@4.14.1+sha512.64df448055..."`. Corepack verifies the downloaded tarball's hash against the suffix and refuses to activate if they don't match. Tampering becomes detectable.

## Computing the SHA-512 Hash

### Preferred: Let Corepack Compute It

```bash
corepack use yarn@4.14.1
jq -r '.packageManager' package.json
# → yarn@4.14.1+sha512.64df448055b2d37ba269d7db535a469b8da93f8ef1140c25fd7a83c00a8fbaacb214ca0e02553b92a2c54cef78bb67d0b4817fab02001df0e24fac0faccc3b42
```

`corepack use` downloads the requested Yarn version, computes the integrity hash, and writes the suffixed form into `packageManager` — all in one command. This is the path Yarn's documentation recommends. The closely-named `corepack prepare yarn@X.Y.Z --activate` only prepares and activates the binary globally; it does not modify `package.json`, so it will not produce the integrity-pinned field on its own.

### Fallback: Compute by Hand

If Corepack isn't available, fetch the tarball and compute SHA-512 directly. Use `shasum -a 512` for portability: it's preinstalled on macOS and most Linux distributions, while `sha512sum` (GNU coreutils) is Linux-only and absent from a stock macOS install.

```bash
VERSION=4.14.1
HASH=$(
  curl -fsSL "https://repo.yarnpkg.com/${VERSION}/packages/yarnpkg-cli/bin/yarn.js" \
    | shasum -a 512 \
    | awk '{print $1}'
)
```

Then update `package.json`:

```bash
jq --arg pm "yarn@${VERSION}+sha512.${HASH}" '.packageManager = $pm' package.json > package.json.tmp \
  && mv package.json.tmp package.json
```

### Verification

After writing the suffixed `packageManager` field:

```bash
corepack enable
yarn --version  # must print the pinned version
```

If the hash is wrong, Corepack errors out with a mismatch message instead of running.

## `.yarnrc.yml` Security-Strict Defaults

Yarn 2+ reads `.yarnrc.yml` for configuration. Several settings have permissive defaults that a future Corepack migration (or a misguided "one-time fix") can flip on:

```yaml
enableScripts: false
enableTelemetry: false
defaultSemverRangePrefix: ""
```

| Setting                    | Default | Pin to  | Why                                                                                                                                            |
| -------------------------- | ------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `enableScripts`            | `true`  | `false` | Blocks arbitrary `postinstall` scripts. Most supply-chain attacks against npm-style ecosystems run during install hooks; this disables them.   |
| `enableTelemetry`          | `true`  | `false` | Yarn phones home with anonymized usage data by default. Disable as a matter of policy.                                                         |
| `defaultSemverRangePrefix` | `^`     | `""`    | When `yarn add <pkg>` writes a new dependency, the empty prefix produces an exact pin instead of a caret range — keeps step 6 from regressing. |

Make these explicit even if they happen to match the default — explicit config survives `yarn set version`, Corepack migrations, and version bumps. Implicit defaults can change.

## Harmful Corepack-Migration Additions

Some Corepack workflows add settings that weaken security. Detect and revert these:

| Setting                                      | Harm                                                                                        | Revert                                            |
| -------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| `approvedGitRepositories: ["**"]`            | Whitelists arbitrary git sources for `yarn add <git-url>`, bypassing the registry entirely. | Remove the line or restrict to specific repos     |
| `enableScripts: true`                        | Re-enables postinstall scripts.                                                             | Set to `false`                                    |
| `npmAlwaysAuth: true` (with public packages) | Forces auth on public registry requests, often masking misconfigured tokens.                | Remove unless you actually use a private registry |

Read `.yarnrc.yml` and warn the user before removing entries that look intentional (e.g. a private registry config).

## When the User Opts Out of Corepack

If the project uses npm or pnpm (not Yarn), step 5 of the skill is a no-op — no `packageManager` field, no `.yarnrc.yml`. Skip both.

For pnpm specifically, the `packageManager` field still applies (`"packageManager": "pnpm@9.X.Y"`) and Corepack supports it the same way. Use the same `corepack prepare pnpm@X.Y.Z --activate` flow to add the SHA-512 suffix.

For npm, there is no equivalent integrity-pin mechanism in `package.json`; rely on `package-lock.json` (which contains per-package integrity hashes) and `npm ci` in CI to enforce them.
