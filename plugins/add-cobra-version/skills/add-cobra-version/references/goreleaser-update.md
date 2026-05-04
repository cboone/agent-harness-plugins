# .goreleaser.yml ldflags Update

GoReleaser injects build metadata into the binary via the `builds[].ldflags` list. This skill needs all three `-X main.*` entries to be present.

## Target State

Find the build entry in `.goreleaser.yml` (or `.goreleaser.yaml`) and ensure its `ldflags` list contains:

```yaml
builds:
  - main: .
    binary: PROJECT-NAME
    ldflags:
      - -s -w
      - -X main.version={{.Version}}
      - -X main.commit={{.ShortCommit}}
      - -X main.date={{.Date}}
```

`-s -w` is optional but customary (strips debug info and the symbol table for smaller binaries); preserve it if it is already present.

## Edit Strategy

1. Locate the `ldflags:` list under the relevant build entry. Most projects have a single build entry; if there are several, update each one.
1. Read the existing list. For each of the three required `-X` entries, check whether it is present (look for the substring `main.version=`, `main.commit=`, and `main.date=` so values that already use a different template variable are still recognized).
1. Append only the entries that are missing. Preserve the order of existing entries; new entries can be appended after the last existing line so diffs stay minimal.
1. Do not change unrelated ldflags. In particular, leave `-s -w`, build tag flags, and any user-specific `-X` entries intact.

If `-X main.version=...` is absent (rare; this skill targets projects that already have at least the basic version setup), add it alongside the others. The final order should be `version`, `commit`, `date` for readability.

## GoReleaser Template Variables

Use these GoReleaser template variables exactly as shown:

| Variable           | Replaced with                                                 |
| ------------------ | ------------------------------------------------------------- |
| `{{.Version}}`     | The semver tag without the leading `v` (for example `1.2.3`). |
| `{{.ShortCommit}}` | Seven-character abbreviated commit SHA.                       |
| `{{.Date}}`        | Build start time, RFC 3339 / ISO 8601.                        |

The `{{` and `}}` delimiters are Go template syntax; do not quote the entries. YAML allows them unquoted because they do not begin with a YAML metacharacter.

## Notes

- If the project does not yet have a `.goreleaser.yml` or `.goreleaser.yaml`, this step is skipped. Suggest `/add-goreleaser-homebrew` to add one.
- Some projects use `id:` or multiple build entries to produce variant binaries. Apply the ldflags update to every build entry that maps to the main binary.
- Snapshot builds (`goreleaser release --snapshot`) substitute the same templates and produce a working `version` like `0.0.0-next-SNAPSHOT-abc1234`. The metadata in the binary will reflect the snapshot values, which is the expected behavior for local validation.
