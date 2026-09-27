# 16 — Gate 2: fixed-base physical programmability

**Labels:**
- **MEASURED:** our flow (Yosys/ABC, OpenROAD/OpenSTA, ORFS on SKY130 HD, image 69df744e2b5c).
- **MODELED:** placement-parasitic timing.
- **DERIVED:** exact counts and formulas.
- **INFERRED / UNVERIFIED:** as stated.

**Question.** Does the UBP advantage survive when the silicon below the programmable boundary is fixed and must serve every W?

Everything in E5, E6 and G3 was hardwired: the layout saw W. The thesis claims a **weight-independent, via/metal-programmable** fabric.

## 1. The fixed base (Regime V, as pre-registered in 09_PREREGISTRATION.md)

| Element | Implementation |
|---|---|
| Base | Every cell plus all base wiring on **met1–met3** (`MAX_ROUTING_LAYER met3`). Identical for every W. |
| Programmable boundary | **met4–met5** plus a master swap between identical-footprint via-site masters. |
| Via site (one per leaf) | `VSITE_BUF` / `VSITE_ZERO` / `VSITE_ONE`: 4 placement sites wide. Pin Z (li1) drives the leaf; pin **A is on met4** and has no net in the base. OBS covers met1–met3. |
| Line tap (one per line polarity) | `LTAP`: 8 sites. Pin A (met1) is driven by the line in the base; pin **Z is on met4** and has no net in the base. |
| Program(W) | For each used line, one net {LTAP.Z, VSITE.A of every selecting leaf}, routed on met4–met5 only. Zero leaves are swapped to `VSITE_ZERO`; P2's constant bits to `VSITE_ONE`. No cell is moved, added or removed. |
| Placement | **W-blind.** The base netlist contains no W-dependent connection, and every programmable cell is `dont_touch` during the base flow. |
| Power | met1 follow-pin rails only (D-G2.2); IR drop out of scope. |
| Designs | **B** = UBP3-serial (the thesis). **A** = g1-serial (E6 baseline). **P2** = pipelined bit-plane popcount, the strongest per-input competitor in G3. |
| Base synthesized cell area (µm²) | B 169,952 (1,408 sites, 548 taps); P2 274,662 (4,096 sites, 128 taps, 384 constant sites); A 356,417 (4,096 sites, 128 taps) |
| Test matrices | W1, W2 random (p0 = 0.4); W3 sparse (p0 = 0.8); W4 dense (p0 = 0.1); W5 adversarial (identical rows, maximum fan-out); W14 = the E6/G3 matrix (pre-PnR checks). |
| Real weights | Not obtainable: HuggingFace is blocked in this environment. **Gap.** |

## 2. Results under the pre-registered protocol (generic ORFS placement)

### 2.1 Bases (MEASURED)

| Design | U % | Base DRC (met1–met3) | Final setup / hold WS at 3.0 ns (ns) |
|---|---|---|---|
| B | 60 / 45 / 30 / 15 / 8 | 0 / 0 / 0 / 0 / 0 | +1.05 / +1.03 / +1.08 / +0.83 / +0.55 (hold all > 0) |
| P2 | 60 / 45 | 0 / 0 | −0.26 / −0.17 (a base control broadcast to 64 rows; W-independent) |
| A | 60 | 0 | +0.88 |

### 2.2 Programmable routing, GRT on met4–met5 (MEASURED)

Cells give total overflow (met4 + met5); 0 means the program routes. Full records: `experiments/results/G2/g2_grt_screen.jsonl`.

| Design | U % | W1 | W2 | W3 | W4 | W5 |
|---|---|---|---|---|---|---|
| B | 60 | 14,159 | 14,304 | 2,106 | 9,913 | 0 |
| B | 45 | 14,719 | 14,755 | 1,849 | 9,790 | 0 |
| B | 30 | 16,621 | 16,562 | 112 | 10,075 | 0 |
| B | 15 | 12,291 | 12,263 | 0 | 3,134 | 0 |
| B | 8 | 2,619 | 2,139 | 0 | 0 | 0 |
| P2 | 60 | 466 | 415 | 0 | 3,962 | 0 |
| P2 | 45 | 0 | 0 | 0 | 519 | 0 |
| A | 60 | 0 | 0 | 0 | 108 | 0 |

**B's random matrices (W1, W2) do not route at any utilization down to 8%**, which is a 7.5× larger die than its hardwired E6 layout. Both per-input fabrics route W1, W2, W3 and W5; only the dense W4 overflows, marginally.

### 2.3 Detailed routing of the programmable nets (MEASURED)

At U60 no design's W1 program converges. The per-input designs do not pass detailed routing either.

| Design | W1 DRT violations |
|---|---|
| A | 12,727 → 10,665 after 6 iterations; 8,814 are met4 net-to-net shorts, 262 involve pins (`g1s/diag_w1_u60_drc.rpt`) |
| P2 | 24,818 → 23,178 |
| B | 66,520 → 121,693, diverging |

SKY130's only programmable layers are met4 (0.92 µm pitch) and met5 (3.4 µm pitch, 0.8 µm via4). GRT under-counts how little room they leave. This is a testbed limit that hits every design, and B hardest.

### 2.4 Timing (MODELED: placement parasitics, complete W1-programmed netlist, 3.0 ns clock, U60)

| Design | Worst setup WS | Worst setup WS through programmable nets | Hold WS |
|---|---|---|---|
| B | +0.86 | +1.05 | +0.05 |
| P2 | −1.89 | −0.72 | +0.33 |
| A | +0.41 | +0.41 | −0.01 |

B's few-sink lines are fast. P2's worst path is the W-independent control broadcast; its 38-sink die-spanning lines are also slow (−0.72). **K2c does not fire.**

### 2.5 Functional and integrity checks (MEASURED)

- **Function:** the complete programmed netlist (fixed base + W program), written by OpenROAD after the program was applied and simulated by our cycle-accurate simulator, **matches numpy W@x with the mutation control detected**:
  - B W1 (latency 8), P2 W1 (latency 12) and A W1 (latency 7), at U60;
  - W14 pre-PnR for all three.
  - Records: `results/G2/g2_verification.jsonl`.
- **No lower-layer change:** in a written program DEF (A W1), the 128 programmable nets use only met4 (27,882 segments) and met5 (4,744), and no base net is re-routed.
- **Base integrity:** every base ODB is byte-identical before and after all program runs (`results/G2/base_odb_sha256_before_programs.txt`). **K2d does not fire.**

### 2.6 Pre-registered classification

**K2b fires:** W1 and W2 fail for B at every utilization, while A routes them at U60 and P2 at U45 (GRT level). → **Substantially weakened.**

On the pre-registered protocol, B's fixed-base A×T is unbounded: it has no routable utilization for random W. Even granting B that 8% routed, and its best period, the numbers are:

| | Calculation | A×T |
|---|---|---|
| B at 8% | (169,952 / 0.08) × 14 × 1.95 ns (the R2 period rule applied to B's U60 base: 3.0 − min(base WS +1.05, programmable-path WS +1.05)) | ≥ 58.0e6 |
| A at U60 | (356,417 / 0.60) × 14 × 2.59 ns (3.0 − min(+0.88, +0.41)) | 21.5e6 |

B would be ≥ 2.7× **worse** than A. A's W4 still overflows by 108 at U60, so A's figure is itself slightly optimistic.

## 3. Diagnosis: what failed, and is it intrinsic?

**Overflow maps (MEASURED; GRT congestion reports):**
- **B at 8%:** 2,476 of 2,484 overflowing GCells lie in one vertical stripe through the middle of the die.
- **Where the taps sit:** the generic placer cannot see the programmable nets, so it places every line tap next to the line generators. In A, all 128 taps sit in an 80 × 190 µm patch at one die edge.
- **B's lines:** its 499 used lines all leave that one patch. The horizontal programmable capacity across the patch (met5, 3.4 µm pitch) grows only with the die side, so shrinking utilization barely helps.

**The line count is intrinsic (DERIVED):**
- B needs (3³ − 1)/2 = 13 patterns × 2 polarities = **26 lines per 3 inputs**. A per-input fabric needs **6**.
- That is 548 vs 128 programmable lines. Every one must be reachable from all 64 rows, because the base cannot know which rows will select it.
- In the hardwired E6/G3 layouts, W-aware placement put each line's driver next to its 2–3 users. That is where E6's 5.8× select-wiring saving came from. A fixed base cannot do this.

**The cluster is not intrinsic:** a base designer can lay the base out as a regular crossbar without knowing W. That is the bounded revision R2 (§4), pre-registered before any R2 data.

## 4. R2 — structured (crossbar) W-blind base (the one bounded revision; pre-registered in 09 before any R2 data)

**What changes and what doesn't:**
- The base netlists, cells, programs, layers and tools are unchanged.
- Only the programmable-pin cells get a fixed, W-blind placement before global placement (`scripts/g2_struct.py`, ORFS `POST_PDN_TCL`):
  - one vertical band per line group (22 for B, 64 for P2 and A);
  - each band's 64 via sites at the band centre, one per row;
  - each band's line taps beside them, spread evenly over the core height.
- These cells are FIRM. Everything else is placed by ORFS from base connectivity.

### 4.1 Bases, and programmable routing at GRT level (MEASURED)

Base DRC is on met1–met3. The last five columns give met4/met5 usage, then total overflow, for each program.

| Design | U % | Base DRC | Base setup / hold WS (ns) | W1 | W2 | W3 | W4 | W5 |
|---|---|---|---|---|---|---|---|---|
| B | 60 | 0 | +0.96 / +0.03 | 52% / 14% · 0 | 51% / 14% · 0 | 24% / 5% · 0 | 43% / 11% · 0 | 4% / 0% · 0 |
| B | 52 | 0 | +0.99 / +0.09 | 47% / 12% · 0 | 47% / 12% · 0 | 22% / 4% · 0 | 38% / 10% · 0 | 4% / 0% · 0 |
| B | 45 | 0 | +0.97 / +0.05 | 43% / 10% · 0 | 43% / 10% · 0 | 20% / 4% · 0 | 35% / 8% · 0 | 3% / 0% · 0 |
| P2 | 60 | 0 | −0.65 / −0.01 | 18% / 1% · 0 | 19% / 1% · 0 | 15% / 1% · 0 | 19% / 2% · 0 | 6% / 0% · 0 |
| A | 60 | 0 | +0.79 / +0.09 | 15% / 0% · 0 | 15% / 0% · 0 | 12% / 0% · 0 | 16% / 0% · 0 | 5% / 0% · 0 |
| P2 | 67 | 0 | −1.10 / +0.03 | 20% / 2% · 0 | 20% / 2% · 0 | 16% / 1% · 0 | 21% / 2% · 0 | 7% / 0% · 0 |
| A | 75 | 0 | +0.85 / +0.07 | 18% / 0% · 0 | 18% / 0% · 0 | 14% / 0% · 0 | 18% / 0% · 0 | 6% / 0% · 0 |

**The primary criterion holds for every design at every tested U, for all five W.** The baselines' primary U_max are P2 67% and A 75%, the top of their grids.
- B's W1 programmable wirelength falls from 490 mm (generic base) to **172 mm**.
- P2's falls from 468 mm to 98 mm, and A's from 443 mm to 107 mm.
- **The generic-placement collapse of §2 was a placement artifact.** A W-blind crossbar base removes it for every design.

### 4.2 Detailed routing of the programmable layer: the secondary criterion (MEASURED; 20 iterations, largest-WL program)

| Design | U % | Program | DRT violations by iteration | Final |
|---|---|---|---|---|
| B | 60 | W1 | 5,559 → 4,252 (it. 8) → 2,131 (it. 15) → 5,950 (it. 17, rip-up) → **1,167** (it. 20) | **fails** (925 met4 shorts, 242 met4 spacing) |
| B | 52 | W1 | 5,056 → 3,419 (it. 9) → 1,666 (it. 16) → 4,452 (it. 17, rip-up) → **881** (it. 20) | **fails** (652 shorts, 229 spacing) |
| B | 45 | W2 | 4,462 → 2,862 (it. 9) → 934 (it. 16) → 2,743 (it. 17, rip-up) → **416** (it. 20) | **fails** (281 shorts, 135 spacing) |
| P2 | 60 | W4 | 1,875 → 1,203 → 417 → 108 → 12 → **0** (it. 13) | **passes** |
| A | 60 | W4 | 1,730 → 1,217 → 451 → 145 → 12 → **0** (it. 16) | **passes** |
| P2 | 67 | W4 | 1,940 → 1,279 → 499 → 101 → 10 → **0** (it. 14) | **passes** |
| A | 75 | W4 | 1,837 → 1,204 → 482 → 96 → 10 → **0** (it. 14) | **passes** |

**Where B's residual violations sit:**
- Every one is on met4, spread across the bands and concentrated in the middle 40% of the core height. That is where the interval model puts each band's peak track demand: 22–23 lines in about 26–28 met4 tracks.
- The band's single column of 64 via-site pins and 26 tap pins, all met4 pads, takes centre tracks every line must reach.
- The per-input bands carry 2 lines. They close easily at 15–19% met4 usage.
- B's residual counts fall monotonically, from ~5k to ~1k, but do not reach 0 within the pre-registered 20 iterations.

### 4.3 Timing (MODELED; W1-programmed netlist, placement parasitics, 3.0 ns clock)

| Design | U % | Worst setup WS | WS through programmable nets | Hold WS | **T** = 3.0 − min(base WS, programmable WS) |
|---|---|---|---|---|---|
| B | 60 | +0.91 | **+1.26** | +0.01 | **2.04 ns** |
| B | 52 | +0.88 | +1.35 | +0.01 | 2.01 ns |
| B | 45 | +0.81 | +1.29 | +0.01 | 2.03 ns |
| P2 | 60 | −2.06 | **−1.66** | +0.00 | **4.66 ns** |
| A | 60 | +0.61 | +0.92 | −0.00 | 2.21 ns |
| P2 | 67 | −1.60 | −1.57 | −0.01 | 4.57 ns |
| A | 75 | +0.67 | +1.01 | −0.01 | 2.15 ns |

**Line count vs line load (MEASURED):**
- B's lines are 4.3× more numerous but carry ≈ 2.6 sinks each, so they are fast.
- P2's lines carry ≈ 19–38 sinks, run the full die height, and feed a deep popcount tree. That puts them 1.7 ns over budget.
- A's lines feed registered serial adders directly.

### 4.4 A×T on the structured fixed base (pre-registered metric)

A×T = base cell area / U × cycles × T.
- The "T base-only" sensitivity column ignores the programmable-path delay. That favours P2.
- The "B = …×" columns give the baseline's A×T divided by B's A×T at U60.

| Design | U % | Primary | Secondary | A×T (µm²·ns) | A×T, T base-only | B = …× better | B = …× better (T base-only) |
|---|---|---|---|---|---|---|---|
| **B** | 60 | ✓ | ✗ (1,167) | **8.10e6** | 8.10e6 | — | — |
| B | 52 | ✓ | ✗ (881) | 9.18e6 | 9.18e6 | — | — |
| B | 45 | ✓ | ✗ (416) | 10.71e6 | 10.71e6 | — | — |
| P2 | 60 | ✓ | ✓ | 17.07e6 | 13.38e6 | 2.11 | 1.65 |
| A | 60 | ✓ | ✓ (W4 at it. 16) | 18.35e6 | 18.35e6 | 2.27 | 2.27 |
| **P2** | **67** | ✓ | ✓ (W4 at it. 14) | **14.98e6** | 13.46e6 | **1.85** | 1.66 |
| **A** | **75** | ✓ | ✓ (W4 at it. 14) | **14.28e6** | 14.28e6 | **1.76** | 1.76 |

**Post-PnR functional checks** (complete programmed netlists vs numpy, mutation detected):
- B W1 at U60, U52 and U45, and B W2 at U45;
- P2 W1 and W4 at U60;
- A W1 at U60.
- Records: `results/G2/g2_verification.jsonl`.

## 5. Gate-2 verdict

### 5.1 Pre-registered protocol (generic placement)

**K2b fires → substantially weakened.**
- B has no routable utilization for random W (60 → 8%). The per-input fabrics route 4 of 5 W at 45–60%.
- K2c (timing) and K2d (lower-layer change) do not fire.

### 5.2 R2 (structured crossbar base, the one bounded revision)

**R2-K does not fire, and R2-A is not granted → G2 UNRESOLVED.**

**Primary criterion (GRT, all five W): B passes at every U in its grid (60, 52, 45).**
- At its primary U_max = 60, B's A×T is 8.10e6 µm²·ns.
- Against each baseline at its own primary U_max (P2 67%, A 75%, both also DRC-clean), B is **1.85× better than P2** (14.98e6).
  - The best P2 point with its programmable-path delay ignored is 1.65× (P2 at 60%, 13.38e6).
- B is **1.76× better than A** (14.28e6).
- R2-K would need B within 1.1× of the best baseline, or B unroutable. Neither holds.

**Secondary criterion (DRC-clean detailed routing of the largest-WL program in 20 iterations):**
- **B fails at every U of its grid:** 1,167 / 881 / 416 residual met4 violations at U60 / 52 / 45, decreasing with U.
- **P2 and A pass at U60,** closing at iterations 13 and 16.
- The failure is **B-specific**, not a testbed limit, so the pre-registered R2-A ("… and B's secondary criterion holds") cannot be granted.

### 5.3 Against the Gate-2 kill condition as stated

| Condition | Outcome |
|---|---|
| Weight changes move base cells | **Never.** W-blind placement; every base ODB is byte-identical across all programs. |
| Weight changes modify forbidden layers | **Never.** Program wires are only on met4/met5. |
| Routability/timing collapse removes the advantage | **Generic placement:** yes, a collapse. **Structured base:** no collapse. GRT routes every W with margin, B has the best timing of the three designs, and the A×T advantage (1.76–1.85× against each baseline's best U) holds at GRT level. But B's detailed routing does not close within the pre-registered effort at any tested U, while the per-input fabrics' does. |

The fixed-base advantage is therefore **neither demonstrated nor removed**. That is the definition of an unresolved gate.

### 5.4 What was learned (the scientific content of G2)

- **UBP's fixed-base cost is reachability, not ports.** B has 2.9× fewer programmable ports than the per-input fabrics (1,408 vs 4,096; Theorem 1), but 4.3× more programmable lines (548 vs 128), each of which must be reachable from all rows.
  - A W-aware layout (E6/G3) hides this cost.
  - A W-blind layout exposes it.
- **Under connectivity-driven placement the cost is fatal:** every line originates in one tap cluster.
- **Under a W-blind crossbar the cost becomes a per-band track budget:** 22–23 lines per band vs 2 for the per-input fabrics.
  - It fits at GRT level at U60.
  - It saturates SKY130's single fine programmable layer (met4, 0.92 µm) at detailed-route level.
  - The residual violations fall monotonically as U falls (1,167 → 416).
- **The line-count / line-load trade-off favours B on timing:**
  - Its lines carry ≈ 2.6 sinks, giving +1.26 ns of slack on programmable paths.
  - P2's carry 19–38 sinks and feed a deep popcount tree, giving −1.66 ns.

### 5.5 Post-hoc diagnostic (not pre-registered; cannot change the classification)

The same structured bases and the same largest-WL programs, detailed-routed with OpenROAD's default 64 iterations instead of the pre-registered 20.

**Why run it:**
- The ORFS base flows themselves use 64.
- B's 20-iteration residuals were still falling.
- It separates "the router ran out of iterations" from "the layout cannot close".

| B at U | Program | Trajectory (64 iterations) | Final | DRC-clean A×T | vs P2 best (14.98e6 / 13.38e6 base-only T) | vs A best (14.28e6) |
|---|---|---|---|---|---|---|
| 45 | W2 | identical to the 20-iteration run through it. 20 (416), then 321 (it. 24) → 100 (it. 35) → 36 (it. 52) → 7 (it. 61) → **0** (it. 64) | **0: DRC-clean** | 10.71e6 | 1.40× / 1.25× | **1.33×** |
| 52 | W1 | POSTHOC_52 | | 9.18e6 if clean | 1.63× / 1.46× | 1.56× |
| 60 | W1 | POSTHOC_60 | | 8.10e6 if clean | 1.85× / 1.65× | 1.76× |

**What this shows:**
- At U45, B's programmable layer **can** be closed on SKY130 met4–met5 with default router effort. The pre-registered 20-iteration cap, not physical infeasibility, is what failed B there.
- At U45, a DRC-clean B beats P2 by ≥ 1.2× but beats A (at 75%) by only 1.33×. The pre-registered A bar is 1.5×.
- To clear both bars, B must close at U ≥ ≈ 51%.
- **This is post hoc and does not change the pre-registered G2 classification (unresolved).** It does sharpen the decisive next experiment: a pre-registered repeat of R2 with 64 iterations, B at U52–60, against P2 at 67 and A at 75.
