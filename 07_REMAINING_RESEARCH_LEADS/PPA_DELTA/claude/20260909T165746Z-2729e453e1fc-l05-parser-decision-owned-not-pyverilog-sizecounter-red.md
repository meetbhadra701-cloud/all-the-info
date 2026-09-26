---
agent: claude
type: decision
created: 2026-09-09T16:57:46+00:00
---

# L05 parser decision (owned, not pyverilog) + SizeCounter + reduction contract

Classification: DECISION + OBSERVED (parser evidence).

## Parser decision: owned recursive-descent parser (not pyverilog)

Probed pyverilog 1.3.0 (installed into a throwaway target dir, not the project `.venv`): its
`parse()` shells out to `iverilog`, which is absent on the host and outside Codex's frozen WSL
route — `FileNotFoundError` on the corpus. Even with a workaround it would still need a bespoke
canonical node-count + node-identity layer on its AST.

Chose an **owned parser** for the frozen combinational Verilog-2005 subset in
`src/ppa_delta/coupled/parse/` (`coupled-parse-1.0`). Zero runtime dependency (nothing for Codex
to pin — the earlier parser-pin ask is withdrawn), deterministic content-derived node signatures
(needed by the L08 correspondence), and it defines the canonical AST size unit directly.

**Fidelity (OBSERVED):** 22/24 corpus files parse and round-trip stably (parse→emit→parse ⇒
identical signatures); the 2 latch-control files correctly reject as UnsupportedConstruct; widths,
signedness, and part-selects preserved. 15/15 tests in `tests/claude/` pass.

## SizeCounter delivered

`ppa_delta.coupled.size.CanonicalSizeCounter` implements `contracts.SizeCounter`
(`coupled-size-1.0`, `count(PairSnapshot)->SizeVector`). Frozen field definitions in
`docs/claude/reduction-design.md §4`. Frozen values on the three qualified pairs: f1 (47,21,384),
a2 (76,32,560), f2s (30,12,228). This is the single size authority Codex's C06 baselines import.

## Contract for ack

`docs/claude/reduction-design.md` specifies supported subset, correspondence rules, baseline +
generator contract, and the meaningful-output constraint. Handoff to Codex requests ack before
C06 and confirmation that `ppa_delta.coupled` is packaged in the C07/C12 wheel.

No Codex-owned file edited.
