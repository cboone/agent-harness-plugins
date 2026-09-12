# build.zig.zon Template

Create `build.zig.zon` in the project root with the following content.

Replace `PACKAGE-NAME` with the underscored package name and `ZIG-VERSION` with the normalized Zig version.

Emit the file exactly as shown, **without** a `.fingerprint` field. The compiler generates that value and prints it on the first build; the "Verify the Build and Fill In the Fingerprint" step writes it back.

```zig
.{
    .name = .PACKAGE-NAME,
    .version = "0.1.0",
    .minimum_zig_version = "ZIG-VERSION",
    .dependencies = .{},
    .paths = .{
        "build.zig",
        "build.zig.zon",
        "src",
        "LICENSE",
    },
}
```

After the first `zig build`, the file gains one line between `.version` and `.minimum_zig_version`:

```zig
    .fingerprint = 0xd7ba43a4d5bc8918, // Changing this has security and trust implications.
```

## Notes

- `.name` is an enum literal and must be a valid bare Zig identifier. A hyphenated name fails with `error: name must be a valid bare zig identifier`, and quoting it as `.@"my-tool"` does not help. Use underscores here; the binary name in `build.zig` keeps its hyphens.
- `.fingerprint` is half of the package's globally unique identifier, paired with `.name`. It is generated once and then never changes. Copying one from another project claims that project's identity, which is why the trailing comment exists: it makes any later edit to the field visible in review.
- `.minimum_zig_version` is the project's single Zig version pin. The CI and release workflows both read this file rather than restating the version, so there is only one string to keep current. Despite the field name, `mlugg/setup-zig` installs exactly this version.
- `.dependencies` is left empty. Adding a dependency writes a multihash into this file, which gitleaks reads as a credential; `set-up-secret-scanning` covers the allowlist entry once the project has one.
- `.paths` determines which files are included in the hash a downstream consumer computes. `LICENSE` is listed, so generate it before the first build.
- `.version` is the project's own SemVer, separate from the Zig version. `build.zig` reads it through `@import("build.zig.zon")` so `--version` cannot drift from the manifest.
