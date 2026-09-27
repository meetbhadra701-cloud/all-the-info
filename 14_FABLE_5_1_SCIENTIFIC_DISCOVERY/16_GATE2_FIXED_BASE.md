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

## 4. R2 — structured (crossbar) W-blind base

(Pending: results below are filled in from the R2 runs.)

## 5. Gate-2 verdict

(Pending R2.)
