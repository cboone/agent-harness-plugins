# src/main.zig Template

Create `src/main.zig` with the following content.

Replace `PROJECT-NAME` with the project name and `PACKAGE-NAME` with the underscored package name.

This is the CLI entry point: argument handling and nothing else, so the logic in `src/root.zig` stays testable.

```zig
//! Command-line entry point.
//!
//! Argument handling lives here and nothing else does, so that the logic in
//! `src/root.zig` stays testable without a process around it.

const std = @import("std");
const Io = std.Io;

const build_options = @import("build_options");
const PACKAGE-NAME = @import("PACKAGE-NAME");

const usage =
    \\Usage: PROJECT-NAME [options] [name]...
    \\
    \\Options:
    \\  -h, --help     Print this help and exit
    \\  -V, --version  Print the version and exit
    \\
;

/// What one command-line argument asks for. Split out from `main` so the flag
/// table can be tested without spawning the binary.
const Arg = enum { help, version, unknown_option, operand };

fn classify(arg: []const u8) Arg {
    if (std.mem.eql(u8, arg, "-h") or std.mem.eql(u8, arg, "--help")) return .help;
    if (std.mem.eql(u8, arg, "-V") or std.mem.eql(u8, arg, "--version")) return .version;
    if (std.mem.startsWith(u8, arg, "-")) return .unknown_option;
    return .operand;
}

/// Returning `u8` rather than calling `std.process.exit` is deliberate: `exit`
/// does not return, so it would skip the buffered writer's flush.
pub fn main(init: std.process.Init) !u8 {
    // The arena lives as long as the process and the runtime releases it, so
    // the argument slice needs no explicit cleanup.
    const arena = init.arena.allocator();
    const io = init.io;
    const args = try init.minimal.args.toSlice(arena);

    var stdout_buffer: [4096]u8 = undefined;
    var stdout_writer = Io.File.stdout().writer(io, &stdout_buffer);
    const stdout = &stdout_writer.interface;

    // An empty Windows command line yields no arguments at all, so the length
    // is checked before slicing past the program name.
    if (args.len < 2) {
        try stdout.writeAll(usage);
        try stdout.flush();
        return 0;
    }

    for (args[1..]) |arg| switch (classify(arg)) {
        .help => {
            try stdout.writeAll(usage);
            try stdout.flush();
            return 0;
        },
        .version => {
            try stdout.print("PROJECT-NAME {s}\n", .{build_options.version});
            try stdout.flush();
            return 0;
        },
        .unknown_option => {
            // Flush first: whatever earlier arguments printed should land on
            // stdout before the diagnostic lands on stderr.
            try stdout.flush();
            std.log.err("unrecognized option: '{s}'", .{arg});
            try Io.File.stderr().writeStreamingAll(io, usage);
            return 2;
        },
        .operand => try PACKAGE-NAME.greet(stdout, arg),
    };

    try stdout.flush();
    return 0;
}

test classify {
    try std.testing.expectEqual(Arg.help, classify("-h"));
    try std.testing.expectEqual(Arg.help, classify("--help"));
    try std.testing.expectEqual(Arg.version, classify("-V"));
    try std.testing.expectEqual(Arg.version, classify("--version"));
    try std.testing.expectEqual(Arg.unknown_option, classify("--nope"));
    try std.testing.expectEqual(Arg.operand, classify("world"));
}
```

## Notes

- `pub fn main(init: std.process.Init) !u8` is the Zig 0.16 form. A zero-parameter `main` still compiles but receives no `Io` and no arguments, and 0.16 removed the free functions that used to supply argv, so a CLI has no way back to them.
- Argv comes from `init.minimal.args.toSlice(arena)`, never `init.minimal.args.iterate()`. The iterator is a `@compileError` on Windows and WASI, so `iterate()` fails the cross-compile job on the first push. `toSlice` builds for every release target.
- `std.process.Init` rather than `std.process.Init.Minimal`: the full form hands over the `Io` instance and an arena already built by the runtime. `Minimal` carries only the environment and arguments, leaving the allocator and `Io` to construct by hand.
- Returning `u8` instead of calling `std.process.exit` matters because `exit` goes straight to the syscall and discards anything still sitting in the stdout buffer. Every exit path here flushes first.
- Stdout is buffered through `Io.File.stdout().writer(io, &buf)`, and writes go to its `.interface`. `std.fs.File` no longer exists in 0.16.
- `classify` is a separate function so the flag table is unit-testable without spawning the binary, which is also what keeps the test from touching stdout.
- An unknown option exits 2 with a clean stdout and the diagnostic on stderr. If the project later adds snapshot tests, that exit code becomes a recorded expectation, so change it deliberately rather than by accident.
