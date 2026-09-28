# Experiments (phase B8)

Every experiment was pre-registered in `../04_CHEAP_EVALUATORS.md` Part 1 (commit `967661a`) before it ran. Results are in `../04_CHEAP_EVALUATORS.md` Part 2.

Run directories (`runs/`) hold regenerable ORFS databases and are not committed. Everything regenerates from the scripts.

| Folder | Candidate | Scripts | Results |
|---|---|---|---|
| `xacc/` | XACC (+ XABFT as C2) | `formats.py` (E1a width bound); `order_invariance.py` (E1b, decisive premise check); `posthoc_dynamic_range.py` (post hoc, not decisive); `rtl/xacc_pe.v` (4 PEs + readout); `aigsim.py` (bit-parallel AIGER simulator); `verify_pe.py` (goldens + mutation controls); `physical.py` (E2 ORFS + extraction + 3-corner STA + post-route verification + decision); `loop_paths.tcl` (accumulator-loop slack diagnostic) | `results/` |
| `mr_signoff/` | MR-SIGNOFF | `mr_signoff.py` (MR0–MR2 on two routed designs) | `results/d1.json`, `results/d2.json` |
| `lincec/` | LIN-CEC screen | `crc_screen.py` (ABC `cec` / `&cec`); `linear_check.json` (n+1-simulation GF(2) check) | `results.json`, `linear_check.json` |

**Reproduction.** Run from each folder. They need docker with `openroad/orfs:latest` and, for sign-off, the SKY130 corner cache (`python3 -m harness.sky130 fetch`, `SUPPORTING_ARTIFACTS/research_harness`).

```
cd xacc && python3 formats.py && python3 order_invariance.py && python3 verify_pe.py && python3 physical.py run && python3 physical.py decide
cd ../mr_signoff && python3 mr_signoff.py d1 && python3 mr_signoff.py d2      # d2 needs runs/gcd (ORFS gcd build, see script)
cd ../lincec && python3 crc_screen.py
```
