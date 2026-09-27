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

**B's random matrices (W1, W2) do not route at any utilization down to 8%.** At 8% the core is 2.11 mm², about 10× its hardwired E6 layout (0.21 mm²). Both per-input fabrics route W1, W2, W3 and W5; only the dense W4 overflows, marginally.

### 2.3 Detailed routing of the programmable nets (MEASURED)

At U60 no design's W1 program converges. The per-input designs do not pass detailed routing either.

| Design | W1 DRT violations |
|---|---|
| A | 12,727 → 10,665 after 6 iterations; 8,814 are met4 net-to-net shorts, 262 involve pins (`g1s/diag_w1_u60_drc.rpt`) |
| P2 | 24,818 → 23,178 |
| B | 66,520 → 121,693, diverging |

SKY130's only programmable layers are met4 (0.92 µm pitch) and met5 (3.4 µm pitch, 0.8 µm via4). With generic placement, GRT under-counts how little room they leave for die-spanning Steiner trees.
- This hits every design, and B hardest.
- The structured base of §4 removes the problem for the per-input designs; they then close detailed routing.

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
- B: W1 at U60, U52 and U45, and W2 at U45;
- P2: W1 and W4 at U60 and U67;
- A: W1 and W4 at U60 and U75.
- That is 12 structured-base programmed netlists, every one matching numpy with the mutation detected.
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
- **P2 and A pass at every U tested:** P2 at 60 and 67 (iterations 13 and 14), A at 60 and 75 (iterations 16 and 14).
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
| 52 | W1 | 881 (it. 20) → 512 (it. 30) → 349 (it. 40) → 294 (it. 50) → 178 (it. 60) → **117** (it. 64) | **117: not closed** (90 shorts, 27 spacing) | (9.18e6 if clean) | (1.63× / 1.46×) | (1.56×) |
| 60 | W1 | 1,167 (it. 20) → 702 (it. 30) → 628 (it. 40) → 518 (it. 50) → 439 (it. 60) → **410** (it. 64) | **410: not closed** (299 shorts, 111 spacing) | (8.10e6 if clean) | (1.85× / 1.65×) | (1.76×) |

**What this shows:**
- **On the R2 layout, B's DRC-clean ceiling with default router effort is between 45% and 52%.**
  - At U45 the 20-iteration cap was what failed B. With 64 iterations it closes.
  - At U52 and U60 more effort helps but plateaus: 117 and 410 residual violations, falling by only ~30% over the last 20 iterations.
- **At that ceiling (U45), a DRC-clean B beats P2 by 1.40× (1.25× if P2's line delay is ignored) but beats A (at 75%) by only 1.33×.**
  - The pre-registered bars are ≥ 1.2× vs P2 and ≥ 1.5× vs A.
  - B passes the first bar and misses the second.
  - To clear both, B must close at U ≥ ≈ 51%.
- **So router effort alone does not resolve G2.** The layout itself must free met4 tracks: stagger the site pins across the band, split the taps, and keep pads off line tracks. Alternatively, a third programmable layer.
- **This is post hoc and does not change the pre-registered G2 classification (unresolved).**
- It defines the decisive next experiment: a pre-registered site/tap co-designed band (R3), routed at 64 iterations, with B at U52–60 against P2 at 67 and A at 75.

## 6. R3 — the final layout revision: segmented line taps (pre-registered in 09, R3)

**What changed from R2 (layout only; logic, programs and criteria unchanged):**
- Every line has **four taps** (LTAP2, 2 sites wide, single-track met4 pad) on its base net. The base routes each line as a spine on met1–met3 through its taps.
- Rows are split into four segments. A leaf connects only to its line's tap in its own segment.
- Taps sit at the line's home x, staggered in y. Sites stay in one track-aligned centre column per band.
- Tap area is unchanged (4 × 2 sites = 8), so the base cell area is still 169,952 µm².
- Chosen from R2's measured mechanism and development matrices only.

### 6.1 Bases (MEASURED)

| U % | Base DRC (met1–met3) | Base setup / hold WS (ns) | Base met2 GRT usage | Base ODB sha256 (first 12 hex) |
|---|---|---|---|---|
| 52 | 0 | +0.976 / +0.268 | 61.2% (R2: 20.7%) | aefbdaff878a |
| 60 | 0 | +1.022 / +0.293 | — | 70add1cde3c5 |

The line spines move the long wiring into the base, which had headroom: at 52%, R2's base used 20.7% of met2.

### 6.2 All five programs, met4–met5 only, detailed routing to normal completion (64-iteration default)

MEASURED, except the timing column, which is MODELED with placement parasitics as pre-registered. Every row has **0** GRT overflow and **0** residual DRT violations.

| U % | W | DRT iterations to 0 | GRT met4 / met5 usage | met4 / met5 WL (µm) | via4 | Setup / hold / programmable-path WS (ns) | = numpy, mutation | Invariants (zero-site swaps) |
|---|---|---|---|---|---|---|---|---|
| 52 | W1 | 14 | 16.5% / 7.5% | 60,063 / 4,236 | 772 | +0.888 / +0.192 / +1.094 | ✓ ✓ | ✓ (118) |
| 52 | W2 | 13 | 17.1% / 7.9% | 62,396 / 4,464 | 823 | +0.888 / +0.192 / +1.082 | ✓ ✓ | ✓ (115) |
| 52 | W3 | 7 | 8.9% / 4.0% | 32,097 / 1,905 | 361 | +0.888 / +0.192 / +1.071 | ✓ ✓ | ✓ (734) |
| 52 | W4 | 14 | 16.5% / 7.4% | 60,641 / 5,174 | 937 | +0.888 / +0.192 / +1.073 | ✓ ✓ | ✓ (7) |
| 52 | W5 | 1 | 3.5% / 0.5% | 12,533 / 23 | 4 | +0.888 / +0.192 / +0.996 | ✓ ✓ | ✓ (64) |
| 60 | W1 | 13 | 18.1% / 7.8% | 57,018 / 3,340 | 685 | +0.840 / +0.213 / +0.840 | ✓ ✓ | ✓ (118) |
| 60 | W2 | 13 | 18.8% / 8.6% | 58,847 / 4,190 | 789 | +0.939 / +0.213 / +0.998 | ✓ ✓ | ✓ (115) |
| 60 | W3 | 7 | 9.7% / 5.1% | 30,419 / 1,356 | 253 | +0.939 / +0.213 / +0.971 | ✓ ✓ | ✓ (734) |
| 60 | W4 | 13 | 18.1% / 6.6% | 57,409 / 4,148 | 879 | +0.825 / +0.213 / +0.825 | ✓ ✓ | ✓ (7) |
| 60 | W5 | 1 | 3.9% / 0.6% | 11,649 / 0 | 0 | +0.788 / +0.213 / +0.788 | ✓ ✓ | ✓ (64) |

**Compared with R2 at 52%:**
- W1's programmable wirelength falls from 181 mm to 64 mm.
- met4 GRT usage falls from 47% to 16.5%.
- Detailed routing goes from 881 residual violations after 20 iterations to **0 after 14**.

**Invariants, checked after every program (`scripts/r3_invariance.py`):**
- The base ODB hash is unchanged.
- All instances keep their location, orientation and status: 14,027 at 52% and 14,078 at 60%.
- Master changes are exactly the programmed zero-site swaps.
- Routing exists only on met4/met5, using only the M4M5 via, and no base net is re-routed.
- The power grid is byte-identical.
- Records: `results/G2/r3/r3_results.jsonl` and `inv_*.json`.

### 6.3 Advantage (pre-registered metric)

- A×T = 169,952 / U × 14 × T.
- Baselines as established, credited with a 2-site tap: A at U75 = 14.25e6, P2 at U67 = 14.93e6.
- The threshold is 14.25e6 / 1.5 = 9.497e6.

| U % | T, W1 rule (ns) | T, worst-program rule (ns) | A×T(B) | vs A (U75) | vs P2 (U67) | Pre-registered criteria |
|---|---|---|---|---|---|---|
| **52** | 2.024 | 2.024 | **9.26e6** | **1.538×** | 1.612× | **PASS** (all) |
| **60** | 2.160 | 2.212 | **8.57e6** (worst: 8.77e6) | **1.663×** (worst: 1.624×) | 1.743× | **PASS** (all) |

### 6.4 Rigor check: timing with routed parasitics (not pre-registered)

**Method:**
- Base nets use the base's own extracted SPEF (OpenRCX on the routed met1–met3).
- Every programmable net uses a conservative lumped RC from its routed met4/met5 geometry: all wire capacitance sits behind the full wire resistance (`scripts/r3_prog_spef.py`, `r3_sta_extracted.tcl`).
- Summary: `results/G2/r3/sta_extracted_summary.json`.

| Design / U | Programmable-path WS by W, extracted (ns) | Base WS | T (W1 rule / worst program) | vs A (U75) (W1 / worst) |
|---|---|---|---|---|
| B, 52 | W1 +1.077, W2 +1.087, W3 +1.062, W4 +1.065, **W5 +0.918** | +0.976 | 2.024 / **2.082** | 1.538× / **1.495×** |
| B, 60 | W1 +0.882, **W2 +0.853**, W3 +0.964, W4 +0.867, W5 +0.941 | +1.022 | 2.118 / 2.147 | 1.696× / **1.673×** |
| A, 75 | W4 +1.046, W5 +0.944 | +0.853 | 2.147 (base-limited) | — |

- The programmable nets themselves are electrically tiny: the largest R3 net is 28.6 Ω and 25 fF.
- **W5 at 52%:** every row is identical, so each segment tap drives 16 sites. The worst path is **SNEG flop → base spine → tap → site**: a minimum-size flop (dfxtp_1) drives a 109 fF spine with a 1.0 ns slew. The base's timing repair never saw that path, because it exists only once a program connects a tap. A production base would size line drivers for the worst-case program; W-independent timing closure would need worst-case load constraints on the tap outputs.
- **At 52%, the most conservative timing therefore puts UBP3 at the 1.5× boundary: 1.495×, 0.3% short.**
- **At 60% it clears 1.6× under every timing model and program.**
- Timing is met at 3.0 ns everywhere: minimum setup WS +0.79 ns, hold ≥ +0.19 ns.

### 6.5 Gate-2 verdict after R3

**G2 PASSES.**
- **Pre-registered result:**
  - A weight-independent UBP3 base, placed once, routed once on met1–met3 and never changed, accepts all five weight programs through met4–met5 alone.
  - Every program is DRC-clean at default router effort and functionally exact.
  - UBP3 keeps ≥ 1.5× lower A×T than the strongest fixed-base per-input fabric, at 52% (1.54×) and at 60% (1.66×).
- **Rigor check:** with routed parasitics and the worst program, 52% is the break-even point (1.495–1.54×), and **60% is the robust operating point (≥ 1.67×)**.
- **Fairness point** (P2 rebuilt with R3's taps, §6.6):
  - As measured, P2-R3 is slower than P2, so A stays the strongest competitor.
  - A post-hoc driver-sizing sensitivity makes P2-R3 the strongest competitor. It puts 52% at 1.48× and leaves 60% at ≥ 1.56×.
  - **The robust operating point is 60%. At 52%, the advantage is at break-even.**

### 6.6 Fairness: P2 rebuilt with R3's segmented taps

**Pre-registered measurement.** Timing is MODELED as for B; everything else is MEASURED.

**Base (U67):**
- DRC 0 on met1–met3.
- Setup / hold WS: −0.846 / +0.024 ns.
- Cell area 274,662 µm², unchanged: the build is area-neutral.
- ODB sha256 `afde9bb09f05…`.

**GRT, all five W:** overflow 0 for every W. met4 usage is 6.6–17.4%; the largest wirelength is W4's, 92,156 µm.

**W4 (largest-WL program):**
- Detailed routing reaches **0 violations in 14 iterations**.
- Invariants hold: base hash, placement, 650 zero/one master swaps, met4/met5 only, power grid.
- The programmed netlist matches numpy, and the mutation is detected.
- Programmable-path WS −2.803 ns.

**W1:**
- The programmed netlist matches numpy, and the mutation is detected.
- **Programmable-path WS −2.453 ns**, against −1.57 ns for P2's original single tap.

**A×T:** T = 3.0 − min(−0.846, −2.453) = 5.453 ns, so A×T(P2-R3) = **17.88e6**. That is worse than P2's own 14.93e6.

**Under the pre-registered reporting rule:**
- P2-R3 is a valid point, but its A×T is not below A's 14.25e6.
- **The strongest fair competitor therefore remains A** (B: 1.538× at 52%, 1.663× at 60%). B is 1.93× / 2.09× better than P2-R3.
- **Base-only-T bound, as in R2:** T = 3.846 ns gives 12.61e6. B is then 1.36× (52%) / 1.47× (60%) better. R2's best P2 base-only bound, 13.38e6 at U60, gives 1.44× / 1.56×.

**Why P2-R3 is slower** (W1 critical path, `results/G2/r3/p2r3_w1_critical_path_u67.log`):
- The minimum-size line flop (dfxtp_1) and its inverter (clkinv_1) now drive the full-height spine to four taps: 107 fF and 91 fF, with ≈ 1 ns slews. That is 1.9 ns of the path.
- These nets have no timing endpoint until a program connects a tap, so the base's timing repair never sees them. This is the mechanism behind B's W5 path in §6.4.
- P2's per-segment programmable nets are short. The loss is in the line drivers, not in the programmable layer.

**Post-hoc sensitivity: spine-driver sizing (D-R3.4).** Not pre-registered; it changes no classification.
- In both designs, every spine-root driver (the instance driving a base net that feeds a tap) is upsized to the drive-4 member of its own family.
- This is W-independent and counted in area.
- Method: MODELED STA only, nothing re-placed; `scripts/r3_whatif_drivers.tcl` → `results/G2/r3/whatif_drivers_*.log`, collected by `scripts/r3_fairness.py` → `fairness_summary.json`.

| Design / U, W | Roots upsized (Δ cell area) | Programmable-path WS, before → after (ns) | T (ns) | A×T |
|---|---|---|---|---|
| P2-R3 / 67, W1 | 64 dfxtp_1 + 64 clkinv_1 (+561 µm²) | −2.453 → −1.167 | 4.167 | **13.69e6** |
| P2-R3 / 67, W4 | same | −2.803 → −1.442 | 4.442 | 14.60e6 |
| B / 52, W1 / W5 | 548 dfxtp_1 (+2,057 µm²) | +1.094 → +1.505 / +0.996 → +1.405 | 2.024: base-set, no gain | 9.37e6 (sizing only adds area; B keeps 9.26e6) |
| B / 60, W1 / W4 / W5 | same | +0.840 → +1.229 / +0.825 → +1.214 / +0.788 → +1.176 | 1.978: now base-set | **7.94e6** |

Ratios are the competitor's A×T divided by B's. B at 52% is as built (sizing does not help it).

| Competitor | A×T (µm²·ns) | vs B, 52% (9.26e6) | vs B, 60% as built (8.57e6; worst program 8.77e6) | vs B, 60% driver-sized (7.94e6) |
|---|---|---|---|---|
| A at 75 (credited) | 14.25e6 | 1.538× | 1.663× (1.624×) | 1.795× |
| P2 at 67 (credited) | 14.93e6 | 1.612× | 1.743× (1.702×) | 1.881× |
| P2-R3 at 67, measured | 17.88e6 | 1.931× | 2.088× (2.039×) | 2.253× |
| **P2-R3, driver-sized (W1 rule)** | **13.69e6** | **1.478×** | 1.598× (1.561×) | 1.725× |
| P2-R3, driver-sized (W4) | 14.60e6 | 1.576× | 1.704× (1.664×) | 1.839× |
| P2-R3 base-only-T bound (idealized) | 12.61e6 | 1.362× | 1.472× (1.438×) | 1.589× |

**Reading:**
- The pre-registered fairness point does not qualify the result: implemented with the same flow, R3's taps make P2 slower.
- The sensitivity shows why that is not the end of the question. The slowdown is a line-driver artefact a designer would fix. Sized, P2-R3 becomes the strongest competitor, at 13.69e6.
- **At 52%**, B beats that competitor by **1.478×, below the 1.5× bar**. With routed parasitics and the worst program, B beats A by 1.495× (§6.4). So 52% is at break-even under any treatment stricter than the pre-registered one.
- **At 60%**, B stays ≥ 1.56× against every measured or driver-sized competitor under every timing rule: the worst case is 1.561×, B's worst program against the driver-sized P2-R3. With both designs sized it is 1.725×.
- **The only pairing below 1.5× at 60%** is asymmetric: an idealized P2-R3 with zero programmable-line delay against an unsized B (1.44–1.47×). Give B the same sizing and it is 1.589×. Idealize both designs to their base-only T and it is 1.61×.
- **Standing qualification, carried into the final verdict:** the ≥ 1.5× fixed-base advantage is **robust at 60%** and **marginal at 52%**.
