# 10 — Experiments and results (E5, E6)

**Sources:**
- Generated summaries: `experiments/results/E5_summary.md`, `experiments/results/E6_summary.md` (via `scripts/e5_collect.py`).
- Wiring decomposition: `results/E*/select_wiring.jsonl`.
- Post-PnR validation: `results/E*/post_pnr_validation.jsonl`.
- Build records: `results/E*/build_n*.json`.

**Scope:** every number is **NEW-OBS** under the evaluator of 08: SKY130 HD, ORFS, placement freedom, only used connections routed. Decisions follow 09, including Amendments A1 and A2.

## 1. Builds and independent validation

| Exp | Design | Weight-independent modules (area µm², pre-placement delay) | Full-fabric cell area µm² | Negators (full) | Pre-PnR sim vs numpy | Mutation caught |
|---|---|---|---|---|---|---|
| E5 (bit-parallel, n = 32) | g1 | NEG_W8 90 (0.99 ns); TREE_L32_W8 8,967 (5.57 ns) | 289,958 | 32 | ✓ 64 vectors | ✓ |
| | ubp3 | NEG_W10 116 (1.45); GEN3 1,931 (3.59); GEN2 384; TREE_L11 3,246 (4.33) | 139,262 | 134 | ✓ | ✓ |
| | ubp4 | NEG_W10 116; GEN4 7,564 (4.65); TREE_L8 2,248 (3.69) | 169,813 | 320 | ✓ | ✓ |
| E6 (bit-serial, n = 64) | g1 | SNEG 76; STREE_L64 5,145 | 334,184 | 64 | ✓ 12 words, cycle-accurate | ✓ |
| | ubp3 | SNEG 76; SGEN3 980; STREE_L22 1,802 | 156,941 | 274 | ✓ | ✓ |
| | ubp4 | SNEG 76; SGEN4 3,671; STREE_L16 1,261 | 188,444 | 640 | ✓ | ✓ |

**E5 pre-placement logic path** (OpenSTA): g1 6.57 ns; ubp3 9.37 ns; ubp4 9.79 ns.

**E6 latency / throughput:** g1 7 cycles; ubp3 and ubp4 8 cycles. All three produce one word every 14 cycles.

**W-independence invariant** (A2): for every run used below, the negator count equals the closed form, and ORFS's synthesized area equals Yosys `stat` of the full netlist.

## 2. E6 — bit-serial (H1.2), n = m = 64, real 3.0 ns clock with CTS, equal throughput

| Design | U % | DRC | Setup / hold WS (ns) | Min period (ns) | Routed WL (µm) | Select WL (µm) | Post-PnR sim |
|---|---|---|---|---|---|---|---|
| g1 | 60 | 0 | +0.80 / +0.10 | 2.20 | 725,378 | 312,815 | ✓ |
| g1 | **75** | 0 | +0.78 / +0.08 | 2.22 | 727,322 | 298,053 | ✓ |
| ubp3 | 60 | 0 | +1.04 / +0.10 | 1.96 | 374,411 | 57,217 | ✓ |
| ubp3 | **75** | 0 | +0.92 / +0.07 | 2.08 | 366,569 | 51,555 | ✓ |
| ubp4 | 60 | 0 | +0.94 / +0.09 | 2.06 | 388,242 | 38,864 | ✓ |
| ubp4 | 75 | 0 | +0.85 / +0.16 | 2.16 | 382,172 | 40,482 | ✓ |

**Decision (pre-registered, A1/A2 basis):**
- U_max = 75 for both g1 and ubp3.
- Routed area: g1 445,579 vs ubp3 209,255 µm².
- **Ratio 2.13×.** Sensitivity: 2.17× on final cells, 2.11× on final cells minus ties.
- **A6 MET; K6 not triggered.**
- ubp4: U_max = 75, routed area 251,259 µm² → g1/ubp4 = 1.77×.

**Also observed:**
- **Timing:** the UBP designs meet the same 3.0 ns clock with more slack. Minimum period 2.08 vs 2.22 ns at U = 75.
- **Throughput:** identical. Latency is +1 cycle.
- **Wiring:** UBP's routed wirelength is 1.98× lower. **Its select (via-programmed) wiring is 5.8× lower**, because each row has ⌈n/g⌉ = 22 leaves instead of 64.
- **Wiring UBP has and g1 lacks:** W-independent generator→negator "fabric" wiring, 21k µm (6% of UBP total).

## 3. E5 — bit-parallel (H1.1), n = m = 32, relaxed 20 ns clock (A1), natural delay reported

| Design | U % | Outcome | Natural delay (ns) | Routed WL (µm) | Select WL (µm) | Post-PnR sim |
|---|---|---|---|---|---|---|
| g1 | 60 | DRC 0 | 11.87 | 1,122,157 | 536,031 | ✓ |
| g1 | **75** | DRC 0 | 11.64 | 1,059,947 | 479,020 | ✓ |
| ubp3 | **60** | DRC 0 | 13.01 | 685,880 | 339,655 | ✓ |
| ubp3 | 75 | **global-route congestion failure** (GRT-0116: 24 overflow edges, met2/met4) | — | — | — | — |
| ubp4 | 60 | «E5_UBP4_60» | | | | |
| ubp4 | 75 | **global-route congestion failure** (GRT-0116) | — | — | — | — |

**Decision (pre-registered, A1/A2 basis):** U_max: g1 = 75, ubp3 = 60 → routed area g1 386,611 vs ubp3 232,103 µm² → **ratio 1.666×** (sensitivity: final-cell basis 1.71×, final-minus-ties basis 1.59×) → **A5 MET, K5 not triggered** — by a margin of 0.17 on the pre-registered basis (0.09 tie-corrected). At equal utilization (U = 60) the ratio is 2.08×; the difference is the utilization step lost to select-bus congestion. Natural delay at U_max: ubp3 13.01 ns vs g1 11.64 ns (1.12×).

**Also observed:**
- **Delay:** bit-parallel UBP3 is **10% slower** post-route (13.01 vs 11.87 ns). That is much less than the 1.43× pre-placement estimate: wire delay in the 2.1× larger g1 fabric absorbs most of the generator's logic depth.
- **Select wiring:** UBP3's is 1.58× lower than g1's, far less than the 5.5–5.8× of the bit-serial designs. Each UBP3 line is a 10-bit bus from a generator; each g1 line is 8 bits.
- **Routability:** UBP3 and UBP4 fail global routing at U = 75 while g1 routes. **The bit-parallel select buses do cost one utilization step.** This is the physical signature of the wiring risk named in 04/06.

## 4. What changed between the superseded pruned runs and the corrected runs (A2)

| Run (U = 60) | Pruned synthesized area | Full-fabric area | Pruned result | Corrected result |
|---|---|---|---|---|
| E5 ubp3 | 133,704 | 139,262 | DRC 0; delay 11.86 ns; WL 639,683 | DRC 0; delay 13.01 ns; WL 685,880 |
| E6 ubp3 | 154,532 | 156,941 | DRC 0; period 2.25 ns | DRC 0; period 1.96 ns |
| E6 ubp4 | 154,658 | 188,444 | DRC 0; period 2.11 ns | DRC 0; period 2.06 ns |

The pruned runs overstated the E5 ubp3 ratio (2.17× instead of 2.08× at equal U) and made its delay look equal to g1's. They are kept in `results/E*/pruned_A1_runs/` and never used for decisions.

## 5. Negative controls and checks

- **Mutation control** (one weight's polarity flipped in the reference) was detected in **every** pre-PnR and post-PnR simulation.
- **Parser check:** the wiring decomposition totals equal ORFS's `detailedroute__route__wirelength` exactly in every run (e.g. 725,378 / 388,242 / 1,122,157 µm).
- **Failures are reported as failures:** a failed global route is a routability limit at that utilization under this flow. It is not a proof that no placement could route.
