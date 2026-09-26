# Reduction semantics and baseline/generator contract (L05)

Owner: Claude · Task L05 · 2026-09-09 · Classification: DESIGN + OBSERVED (parser evidence).
Status: proposed for Codex acknowledgement before C06. No unresolved interface change should
remain after this doc is acked.

## 0. Scope

Defines, for the frozen combinational two-state Verilog-2005 subset: the parse/emit
representation, the supported source-AST operations, the correspondence rules used by the coupled
reducer (L08/L09), the canonical size definition (shared by Codex's C06 baselines), and the
meaningful-output constraint. It does **not** implement the reducer (that is L08/L09) — it fixes
the contract those tasks and the baselines build on.

## 1. Parser decision — owned recursive-descent parser (not pyverilog)

**Evidence (2026-09-09).** pyverilog 1.3.0 installs, but its `parse()` shells out to `iverilog`
for preprocessing; `iverilog` is absent on the host and is **not** part of Codex's frozen WSL
route (Yosys/EQY only). A probe raised `FileNotFoundError` on the corpus. Even with a pure-Python
preprocessor workaround, its AST taxonomy would still require a bespoke canonical node-count and
a stable node-identity layer on top.

**Decision.** Own the parser for the frozen subset in `src/ppa_delta/coupled/parse/`
(`PARSER_VERSION = "coupled-parse-1.0"`). Rationale: zero external/runtime dependency (nothing
for Codex to pin), full control of the canonical node taxonomy that *defines* the size unit, and
deterministic content-derived node signatures that the L08 correspondence needs. The manual's
fallback clause ("implement an owned recursive-descent parser … if round-trip loses width/sign
information") is taken deliberately, not as a last resort.

**Fidelity evidence.** 22/24 corpus source files parse and are **round-trip stable**
(`parse → emit → parse` yields identical subtree signatures); the 2 latch-control files are
correctly rejected as `UnsupportedConstruct`. Widths, signedness, and part-selects are preserved
(tests in `tests/claude/test_parse_roundtrip.py`). Regex is used only for tokenizing, never as the
semantic parser (spec §2).

## 2. Supported subset (v1) and rejected constructs

Supported: one `module`; ANSI ports (`input`/`output`, optional `signed`, optional `[msb:lsb]`);
continuous `wire` declarations with optional initializer; continuous `assign`; expressions over
identifiers, sized/unsized two-state numeric literals, unary `~ - +`, `* / %`, `+ -`,
`< > <= >=`, `== !=`, `&`, `|`, `?:`, index `x[i]`, part-select `x[m:l]`, and concatenation.

Rejected: `reg`/`always`/`initial`, `posedge`/`negedge`, `inout`/`tri`/`logic`, X/Z literals
(precise `UnsupportedConstruct`); and `$`-system functions such as `$signed()`/`$unsigned()`
(the `signed` declaration keyword IS supported, `$signed()` calls are not — a v1 subset limit
confirmed by L06; a `$` raises `ParseError`, which the evaluator surfaces as COMPILE_ERROR).
Anything otherwise unrecognized raises `ParseError`. This is the
parser-level supported-subset gate; it is consistent with — not a replacement for — the
evaluator's own UNSUPPORTED classification (Codex's oracle remains authoritative for
equivalence/area).

## 3. Canonical AST node — the shared size unit

The AST is a single generic `Node(kind, attrs, children)` (`parse/nodes.py`). Three frozen,
deterministic operations:

- `node_count()` — total nodes in a subtree; the **canonical AST size unit**.
- `signature()` — SHA-256 over `(kind, attrs, child signatures)`; identical subtrees share it.
- emission (`parse/emit.py`) — precedence-aware, comment/whitespace-free, one canonical text.

## 4. SizeCounter contract (shared with Codex C06)

`ppa_delta.coupled.size.CanonicalSizeCounter` implements `contracts.SizeCounter`
(`version = "coupled-size-1.0"`, `count(pair: PairSnapshot) -> SizeVector`). Import path for the
baselines: `from ppa_delta.coupled.size import CanonicalSizeCounter` (or the module-level
`DEFAULT` / `count_pair`). Frozen definitions of the `SizeVector` fields:

| field | definition |
|---|---|
| `before_ast` / `after_ast` | total canonical nodes per side (sum over that side's source files) |
| `pair_ast` (primary) | `before_ast + after_ast` |
| `changed_nodes` (tie-break) | multiset symmetric-difference cardinality of subtree signatures between the two sides — identical subtrees cancel; smaller ⇒ the two equivalent programs are structurally closer |
| `bytes` (final tie-break) | UTF-8 length of the canonical re-emission of both sides |

Objective is lexicographic `(pair_ast, changed_nodes, bytes)`, "smaller is strictly better"
(spec §7). Comments/whitespace are excluded by construction. Frozen values on the three qualified
pairs: f1 `(47,21,384)`, a2 `(76,32,560)`, f2s `(30,12,228)`.

**Baselines and coupled reducer MUST use this counter** — no competing count (spec §5, §7).

## 5. Correspondence rules for the coupled reducer (L08/L09 preview, for ack now)

- Parse both sides to canonical ASTs. Establish a **conservative** structural correspondence:
  two subtrees correspond only if they are demonstrably the same structure (equal signature) or
  occupy the same declared role (same port/wire name and width/signedness), else they stay
  **unmatched and unchanged**. A matched pair may be edited only by a coordinated transformation
  that updates both sides identically.
- Build definition/use dependency groups (a `wire`/port defines a name; expressions use names).
  An edit that removes a definition must remove, in the same group, every use — so no candidate
  ever leaves a dangling reference (enforced structurally, then re-checked by the oracle).
- Node identity is `signature()` + child path, never Python object identity — deterministic and
  replayable (spec §"deterministic IDs derived from source/candidate structure").
- The generator's structural matching is a *proposal heuristic only*; functional validity is
  decided solely by Codex's oracle (formal + area). Matching is never treated as proof.

## 6. Baseline contract (Codex C06) and generator contract (Codex C08/C09)

- **Edit-only baseline:** ordered edit groups defined against the original *before* side; apply
  subsets to reconstruct the other side; ordinary delta-debugging partition/complement search
  while the oracle stays INTERESTING; edits are the coordinated node-group removals/substitutions
  in §5. Deterministic ordering by `(child path, signature)`.
- **Independent-side baseline:** the same primitive simplifications applied to one side at a time.
- **Shared invariants for all methods:** the §4 counter, Codex's `Budget` counters, the same
  fresh-final-verification, and always writing a **new** immutable candidate directory
  (`Candidate.candidate_hash == snapshot.pair_hash`, per contracts).
- **Primitive operations (v1):** remove matched unused declarations; remove corresponding output
  cones while retaining a meaningful output (§7); replace corresponding subexpressions with
  same-width operands/constants where allowed; simplify matched conditional branches; remove edit
  groups with dependency closure. Rebuild and reparse after each transformation; never cut tokens
  or mutate literal widths by accident.

## 7. Meaningful-output constraint

A reduced pair must retain at least one output that is nonconstant and input-dependent
(`meaningful_outputs` in the manifest; enforced by the oracle's nonconstant-output guard). The
generator will never propose a candidate whose retained outputs are all constant or wire-only;
such a candidate is degenerate and must be discarded before evaluation.

## 8. Tiny expected-output fixtures (frozen)

Locked in `tests/claude/`:
- `and2`: `module top(input a, input b, output y); assign y = a & b; endmodule` →
  canonical `"module top(input a, input b, output y);\n  assign y = a & b;\nendmodule\n"`,
  `node_count == 11`.
- `signedmul` (8×8 signed → 16): `node_count == 11`, signedness/width preserved.
- Round-trip golden over the whole corpus; latch/always/edge/X-Z rejection.

## 9. What I ask Codex to acknowledge (acceptance)

1. **No new runtime dependency** for parsing — nothing to pin (the earlier "add parser pins"
   request is withdrawn). Please confirm the `ppa_delta.coupled` package is included when the
   wheel is rebuilt for C07/C12 (currently importable via the editable install).
2. The **SizeCounter import path + frozen field definitions (§4)** are the single size authority
   the C06 baselines will import.
3. The **baseline/generator contract (§5–§7)** has no unresolved interface change blocking C06.

No Codex-owned file was edited by me. Reply by handoff with ack or any interface concern.
