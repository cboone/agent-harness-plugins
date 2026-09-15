# src/root.zig Template

Create `src/root.zig` with the following content.

Replace `PROJECT-NAME` with the project name and `PACKAGE-NAME` with the underscored package name.

This is the library module: the code that does the work, with no process around it. `src/main.zig` imports it, and so does any downstream package that depends on this one.

```zig
//! Library root for PROJECT-NAME.
//!
//! This is the module `src/main.zig` imports and the module a downstream
//! package receives from `b.dependency("PACKAGE-NAME", .{}).module("PACKAGE-NAME")`.
//! Only declarations reachable from this file are visible to either, so
//! anything meant to be public must be re-exported here.

const std = @import("std");
const Io = std.Io;

/// Writes a greeting for `name` to `writer`.
///
/// Taking an `Io.Writer` rather than reaching for stdout is what makes this
/// testable without a process around it: the test below hands it a fixed
/// buffer instead.
pub fn greet(writer: *Io.Writer, name: []const u8) Io.Writer.Error!void {
    try writer.print("Hello, {s}!\n", .{name});
}

test greet {
    var buffer: [64]u8 = undefined;
    var writer: Io.Writer = .fixed(&buffer);
    try greet(&writer, "world");
    try std.testing.expectEqualStrings("Hello, world!\n", writer.buffered());
}
```

## Notes

- `greet` is a placeholder. Replace it with the project's actual entry points, keeping the shape: take a writer, return an error union, stay free of process state.
- Accepting `*Io.Writer` rather than writing to stdout is what makes the test possible. `Io.Writer.fixed` wraps a stack buffer and `writer.buffered()` returns what was written, which replaces the `std.io.fixedBufferStream` idiom that Zig 0.16 removed.
- A test must never write to real stdout. Under `zig build test` the test binary's stdout is the build runner's IPC channel, and printing to it corrupts the protocol. Writing into a buffer, as here, is the habit to keep. stderr is safe and is reported as diagnostic output.
- Only declarations reachable from this file are visible to consumers, so a new source file under `src/` needs a `pub const` re-export here before anything can import it.
- `test greet` uses the declaration name rather than a string, which ties the test to the function in the test binary's output.
