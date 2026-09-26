# L06 — Adversarial evaluator audit

Owner: Claude · Task L06 · 2026-09-09 · Classification: OBSERVED (real EDA via the public
`ppa-delta evaluate` v1.0 interface). Matrix: `benchmarks/adversarial/l06-matrix.json`. Raw runs:
`runs/claude/l06-adversarial-20260909T181524Z/`.

## Goal

Try to make the hardened C05 oracle emit a **false INTERESTING** or promote an UNKNOWN/invalid
metric. Six adversarial cases were driven through the public interface only — no competing oracle.

## Result: the oracle failed closed on every case. No false INTERESTING.

| case | attack | expected | observed | interesting? |
|---|---|---|---|---|
| `adv-ineq-biggap` | inequivalent AND large area gap (`a&b` vs `a*b+a`) | reject | **INEQUIVALENT** (formal FAIL) | no |
| `adv-signed-trap` | signed vs unsigned multiply (differ for negatives) | reject | **INEQUIVALENT** (formal FAIL) | no |
| `adv-iface-width-mismatch` | manifest says width 8, RTL is 4-bit | reject | **UNSUPPORTED** | no |
| `adv-path-traversal` | `files_before: ["../ctrl-ident/before.v"]` | reject | **setup rejected**: "path traversal is prohibited" | no |
| `adv-undriven-x` | undriven wire → X in two-state subset | reject | **UNSUPPORTED** | no |
| `adv-source-bloat-equal-area` | more source nodes, identical mapped area | not interesting | **NOT_INTERESTING** (equal area) | no |

The crown-jewel case (`adv-ineq-biggap`) is the important one: a genuine area regression that is
**not** equivalence-preserving is correctly rejected by formal FAIL, never promoted. Path
traversal is explicitly blocked before any file is read. Source bloat confirms the predicate is
driven by mapped area, not source size.

`benchmarks/adversarial/expectations.json` + `l06-matrix.json` + the generator make this
reproducible; `tests/claude/test_adversarial_expectations.py` locks "no adversarial case is
INTERESTING" and each fail-closed class as a regression guard.

## Defects found in C05: none.

No adversarial input produced a false INTERESTING or an invalid-metric promotion. C05 hardening
holds against this suite. (Codex's own C05 cache-identity and stale/malformed controls are not
re-implemented here; this audit is the independent adversarial layer over the public interface.)

## One observation (not a defect) for the record and a minor Codex note

`adv-signed-trap` was first written with `$signed()`. The evaluator returned COMPILE_ERROR with
`size_counter_error: "unexpected character '$'"` — i.e. the failure came from **Claude's own
SizeCounter parser**, which does not accept `$`-system functions, not from Yosys. Two honest
consequences:

1. **Documented parser-subset limit:** `$signed()`/`$unsigned()` system-function calls are outside
   the v1 owned-parser subset (the `signed` declaration keyword IS supported — see the reworked
   case, which uses `wire signed` and reaches the formal engine → INEQUIVALENT). Added to the
   reduction-design supported/rejected list.
2. **Minor observability suggestion to Codex (non-blocking):** a `size_counter_error` (a
   Claude-lane parser-subset gap) is currently surfaced as `COMPILE_ERROR`, which reads as a Yosys
   compile failure. Distinguishing "size-counter/parse-subset rejection" from a real Yosys
   COMPILE_ERROR in the status/logs would make triage clearer. Both are fail-closed, so this is an
   observability nicety, not a correctness issue.
