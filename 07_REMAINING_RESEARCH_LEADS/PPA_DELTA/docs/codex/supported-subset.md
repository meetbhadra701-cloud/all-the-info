# Supported Verilog and semantic subset

PPA-Delta v0.1.0 accepts one synthesizable combinational Verilog-2005 top module
per side. Both sides must declare the same explicit port interface and at least
one meaningful output that remains input-dependent after mapping.

## Accepted source forms

- ANSI `input` and `output` ports, with optional `signed` and constant
  `[msb:lsb]` widths;
- one name per continuous `wire` declaration, optionally initialized;
- continuous `assign` statements;
- identifiers and two-state numeric literals;
- unary `~`, `-`, and `+`;
- binary `*`, `/`, `%`, `+`, `-`, comparisons, equality, logical
  `&&`/`||`, and bitwise `&`/`^`/`|` with Verilog precedence;
- ternary `?:`, bit indexing, constant part-selects, and concatenation.

Widths and signedness are represented explicitly. The canonical parser and
emitter version is `coupled-parse-1.0`; pair size is the deterministic
`coupled-size-1.0` AST count rather than text lines or tokens.

## Rejected or unsupported

- `reg`, `always`, `initial`, event controls, `posedge`/`negedge`, latches,
  flip-flops, clocks, and all sequential behavior;
- memories, blackboxes, hierarchy that has not been flattened, multiple tops,
  and module instances;
- `inout`, `tri`, `logic`, multiple drivers, undriven signals, and
  combinational loops;
- delays, X/Z literals, four-state assumptions, and new input assumptions;
- system functions such as `$signed()` and `$unsigned()` (signed declarations
  themselves are supported);
- comma-separated wire declarations and any construct outside the grammar.

Unsupported semantics fail closed as `UNSUPPORTED`, `COMPILE_ERROR`, or another
non-interesting evaluator status. Parser acceptance is not proof: the oracle
still checks the elaborated interface, combinational structure, formal EQY PASS,
complete standard-cell mapping, finite positive areas, and the meaningful-output
guard.

## Metric boundary

The sole v1 metric is mapped standard-cell area using the frozen Nangate45
Liberty file. The file has no declared physical area unit, so results are
reported only as `Nangate45_library_area_unit`. Cell counts are diagnostics, not
a replacement metric. No timing, power, floorplanning, routing, process-corner,
or silicon claim is made.
