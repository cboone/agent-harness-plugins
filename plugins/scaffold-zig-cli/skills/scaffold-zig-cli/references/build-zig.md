# build.zig Template

Create `build.zig` in the project root with the following content.

Replace `PROJECT-NAME` with the project name (kebab-case, used as the binary name) and `PACKAGE-NAME` with the underscored package name (used as the module name).

```zig
const std = @import("std");

// The manifest is the single source of truth for the version, so `--version`
// and `build.zig.zon` cannot drift apart.
const manifest = @import("build.zig.zon");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const build_options = b.addOptions();
    build_options.addOption([:0]const u8, "version", manifest.version);

    // The package's public module, and also the root module of a test binary.
    // The root module of a Compile step must carry a resolved target, and
    // carrying `optimize` too keeps `zig build test -Doptimize=ReleaseFast`
    // from running these tests in Debug while the executable's run in the
    // requested mode.
    const mod = b.addModule("PACKAGE-NAME", .{
        .root_source_file = b.path("src/root.zig"),
        .target = target,
        .optimize = optimize,
    });

    const exe = b.addExecutable(.{
        .name = "PROJECT-NAME",
        .root_module = b.createModule(.{
            .root_source_file = b.path("src/main.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                // Imported as "lib" rather than under the package name. The
                // executable's import names share one namespace with
                // "build_options" below, so deriving this one from the
                // package name would collide for a package called
                // `build_options`. The public name downstream consumers see
                // is the one given to b.addModule above, and is unaffected.
                .{ .name = "lib", .module = mod },
            },
        }),
    });
    exe.root_module.addOptions("build_options", build_options);
    b.installArtifact(exe);

    const run_cmd = b.addRunArtifact(exe);
    run_cmd.step.dependOn(b.getInstallStep());
    if (b.args) |args| run_cmd.addArgs(args);
    const run_step = b.step("run", "Build and run PROJECT-NAME");
    run_step.dependOn(&run_cmd.step);

    // A test binary covers exactly one module, so the library and the CLI each
    // need their own.
    const mod_tests = b.addTest(.{ .root_module = mod });
    const exe_tests = b.addTest(.{ .root_module = exe.root_module });

    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&b.addRunArtifact(mod_tests).step);
    test_step.dependOn(&b.addRunArtifact(exe_tests).step);

    // One path list for every local entry point: `zig build fmt`, `zig build
    // fmt-check`, and the Makefile's `fmt` and `format` targets, which call
    // those steps. `zig fmt` formats ZON as well, so the manifest is named
    // explicitly. CI does not read this list; see the note below.
    const fmt_paths: []const []const u8 = &.{ "build.zig", "build.zig.zon", "src" };

    const fmt_step = b.step("fmt", "Format all Zig and ZON source in place");
    fmt_step.dependOn(&b.addFmt(.{ .paths = fmt_paths }).step);

    const fmt_check_step = b.step("fmt-check", "Fail if any source is unformatted");
    fmt_check_step.dependOn(&b.addFmt(.{ .paths = fmt_paths, .check = true }).step);
}
```

## Notes

- `@import("build.zig.zon")` gives the build script the parsed manifest, so `manifest.version` feeds `--version` through `b.addOptions()`. Without it a project has two places to bump the version and they drift on the first release.
- `b.addModule` exposes `src/root.zig` to downstream packages as well as to the executable. Passing `optimize` is deliberate: it is optional there, and the upstream `zig init` template omits it, which silently pins the library tests to Debug. A root module with no resolved `target` panics outright.
- A Zig test binary covers exactly one module, which is why there are two `addTest` calls. Dropping either one stops compiling those tests without failing.
- The `fmt` and `fmt-check` steps keep one path list in the build script. `zig fmt --check src/ build.zig`, the invocation most projects reach for, silently never checks `build.zig.zon`.
- **CI does not use this list.** The generated workflow calls `cboone/gh-actions`' `run-zig-ci.yml`, whose format job runs that very `zig fmt --check src/ build.zig` and exposes no input for the paths, so the manifest goes unchecked there. Local and CI formatting are therefore not equivalent, and local is the stricter of the two: `make check` catches an unformatted `build.zig.zon` and a green CI run does not mean there isn't one. The two do not have parity, and this list does not establish any.
- `run_cmd.step.dependOn(b.getInstallStep())` makes `zig build run` execute the installed binary rather than one in the cache directory, so the run matches what a user would get.
