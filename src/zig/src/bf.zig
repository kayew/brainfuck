const std = @import("std");
const print = std.debug.print;
const Allocator = std.mem.Allocator;

pub const bf = struct {
    const Self = @This();
    tape: []u8,
    tape_ptr: usize,
    pgrm_ptr: usize,
    allocator: Allocator,

    pub fn init(allocator: Allocator, mem_size: usize) !Self {
        const tape = try allocator.alloc(u8, mem_size);
        var self = Self{
            .allocator = allocator,
            .tape = tape,
            .tape_ptr = 0,
            .pgrm_ptr = 0,
        };
        self.clear_tape();
        return self;
    }

    pub fn deinit(self: *Self) void {
        self.allocator.free(self.tape);
    }

    fn clear_tape(self: *Self) void {
        for (self.tape) |*cell| {
            cell.* = 0;
        }
    }

    fn cleanup(self: *Self, pgrm: []const u8) ![]u8 {
        var new_pgrm = try self.allocator.alloc(u8, pgrm.len);
        var i: usize = 0;
        for (pgrm) |char| {
            switch (char) {
                '>', '<', '+', '-', '[', ']', ',', '.' => {
                    new_pgrm[i] = char;
                    i += 1;
                },
                else => {},
            }
        }
        return new_pgrm;
    }

    pub fn run(self: *Self, pgrm: []const u8) !void {
        var code = try self.cleanup(pgrm);
        defer self.allocator.free(code);
        while (self.pgrm_ptr < pgrm.len) {
            const opcode = code[self.pgrm_ptr];
            switch (opcode) {
                '>' => {
                    if (self.tape_ptr == self.tape.len - 1) return undefined;
                    self.tape_ptr += 1;
                },
                '<' => {
                    if (self.tape_ptr == 0) return undefined;
                    self.tape_ptr -= 1;
                },
                '+' => {
                    self.tape[self.tape_ptr] +%= 1;
                },
                '-' => {
                    self.tape[self.tape_ptr] -%= 1;
                },
                '.' => {
                    const stdout = std.io.getStdOut().writer();
                    stdout.print("{c}", .{self.tape[self.tape_ptr]}) catch |err| return err;
                },
                ',' => {
                    const stdin = std.io.getStdIn().reader();
                    self.tape[self.tape_ptr] = stdin.readByte() catch |err| return err;
                },
                // https://github.com/daneelsan/brainfuckz/blob/main/src/brain.zig#L116-L150
                '[' => {
                    if (self.tape[self.tape_ptr] == 0) {
                        var depth: usize = 1;
                        var ip = self.pgrm_ptr;
                        while (depth != 0) {
                            if (ip == code.len - 1) return undefined;
                            ip += 1;
                            switch (code[ip]) {
                                '[' => depth += 1,
                                ']' => depth -= 1,
                                else => {},
                            }
                        }
                    }
                },
                ']' => {
                    if (self.tape[self.tape_ptr] != 0) {
                        var depth: usize = 1;
                        var ip = self.pgrm_ptr;
                        while (depth != 0) {
                            if (ip == 0) return undefined;
                            ip -= 1;

                            switch (code[ip]) {
                                '[' => depth -= 1,
                                ']' => depth += 1,
                                else => {},
                            }
                        }
                    }
                },
                else => {},
            }
            self.pgrm_ptr += 1;
        }
    }
};

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    if (args.len == 2) {
        const file = try std.fs.cwd().openFile(args[1], .{});
        defer file.close();

        const code = try file.readToEndAlloc(allocator, std.math.maxInt(usize));
        defer allocator.free(code);

        var computer = try bf.init(allocator, 1024);
        defer computer.deinit();
        try computer.run(code);
    } else {
        print("Usage: {s} <program>", .{args[0]});
        return;
    }
}

test "bf" {
    const allocator = std.testing.allocator;
    var computer = try bf.init(allocator, "+[-->-[>>+>-----<<]<--<---]>-.>>>+.>>..+++[.>]<<<<.+++.------.<<-.>>>>+.");
    computer.run() catch unreachable;
}
