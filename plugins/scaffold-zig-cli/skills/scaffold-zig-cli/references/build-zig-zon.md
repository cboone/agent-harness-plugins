# build.zig.zon Template

Create `build.zig.zon` in the project root with the following content.

Replace `PACKAGE-NAME` with the underscored package name and `ZIG-VERSION` with the detected Zig version, exactly as printed.

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

The first `zig build` fails and prints a suggested fingerprint. It does not edit the manifest: nothing writes this line but the skill, copying the value out of that diagnostic as step 21 describes. Add it between `.version` and `.minimum_zig_version`, indented like its neighbours:

```zig
    .fingerprint = 0xd7ba43a4d5bc8918, // Changing this has security and trust implications.
```

## Notes

- `.name` is an enum literal and must be a bare Zig identifier that is not a reserved word: it matches `[A-Za-z_][A-Za-z0-9_]*` and is none of Zig's keywords. Use underscores here; the binary name in `build.zig` keeps its hyphens. Three ways this goes wrong, all rejected: a hyphen (`my-tool`) and a leading digit (`123_tool`) both fail to parse as an enum literal, and a keyword (`test`, `error`, `fn`) does too. Quoting rescues none of them, because `.@"my-tool"` fails with `error: name must be a valid bare zig identifier`.
- `.fingerprint` is half of the package's globally unique identifier, paired with `.name`. It is generated once and then stays put for as long as the package is the same package. Copying one from another project claims that project's identity, which is why the trailing comment exists: it makes any later edit to the field visible in review.
- Forking or renaming does change the identity, and that is the one case where regenerating is right. The high half is derived from `.name`, so a renamed package fails with `invalid fingerprint: 0x...; if this is a new or forked package, use this value: 0x...`. Delete the field, run `zig build`, and take the value the compiler reports, exactly as at scaffold time. Upstream's own guidance is that a fork which keeps the original fingerprint while the original is still maintained is a hostile fork.
- `.minimum_zig_version` is the project's single Zig version pin. The CI and release workflows both read this file rather than restating the version, so there is only one string to keep current. Despite the field name, `mlugg/setup-zig` installs exactly this version.
- `.dependencies` is left empty. Adding a dependency writes a multihash into this file, which gitleaks reads as a credential; `set-up-secret-scanning` covers the allowlist entry once the project has one.
- `.paths` determines which files are included in the hash a downstream consumer computes. `LICENSE` is listed, so generate it before the first build.
- `.version` is the project's own SemVer, separate from the Zig version. `build.zig` reads it through `@import("build.zig.zon")` so `--version` cannot drift from the manifest.
