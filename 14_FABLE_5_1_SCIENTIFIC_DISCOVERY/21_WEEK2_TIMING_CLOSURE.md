# 21 — Week 2: physical timing closure and driver-sized fairness

**Specification:** `19_FINAL_UBP_DECISION.md` §H, Week 2.
- Line-driver timing closure for every design: W-blind worst-case load constraints on tap outputs, and sized spine drivers placed and routed, not just simulated.
- Extracted-parasitic STA of merged base + program.
- Three corners.
- **Kill point:** at the operating density (60%), UBP must stay ≥ 1.5× over the best driver-sized baseline.

**Generation path:** `ubpgen` only (Week 1).

Section 1 was written, committed and pushed **before any Week 2 physical build or Week 2 timing result**. Later sections record what happened.

---

## 1. Pre-registration (frozen)

### 1.1 What Week 2 replaces

Two things in the validated result were not physical:
1. The line-driver sizing of `16_GATE2_FIXED_BASE.md` §6.6 (D-R3.4) was an STA-only what-if.
2. The timing was modeled with placement parasitics at one corner.

Week 2 replaces both with physical implementations. Every driver is instantiated, placed and routed in the frozen base. Timing is extracted from the routed base + program, and analysed at three corners.

### 1.2 Driver roles (the same for every fabric)

| Role | Cell | Load | Weight dependence |
|---|---|---|---|
| **Spine driver** | the standard cell driving a line's base net: SNEG `pos`/`neg` flops in B and A; PLINE flop and inverter in P2 | spine wire (met1–met3) plus K tap inputs (plus the P2 inverter input) | **none**: fixed by the frozen base |
| **Tap driver** | the tap cell driving a programmable net (met4/met5) | the site inputs a program connects, plus the programmable wire | bounded by the worst case: every row of the tap's segment connected (m/K sinks), spanning the segment |

### 1.3 A physical-accounting correction (stated before any data)

**The historical abstract tap cells carry a buffer's timing without its area:**
- R3's `LTAP2` has `buf_4` timing in 2 sites. A sky130 `buf_4` alone occupies 6 sites.
- The per-input baselines' historical R2 tap `LTAP` is 8 sites: 2 for the pad plus 6 for `buf_4`. That is honest, but the established comparison then credited it back down to 2 sites (−960.9 µm²).
- **Every tap was therefore counted as 2 sites**, whatever buffer it models.
- **The convention favours the fabric with the most taps:** UBP3-R3 has 2,192 taps; A and P2 have 128 (R2) or 512 (P2-R3).
- Week 2 forbids idealized buffers ("the driver must exist in the routed physical design", "do not count timing improvement without counting its physical cost"). So in Week 2 **every tap is a physical cell whose area is the 2-site via/pad plus the area of the buffer whose timing it carries** (§1.4).
- This correction **disfavours UBP**. It is applied to every fabric identically.
- The A×T formula is unchanged. For continuity, the result under the historical 2-site convention is also reported, **labelled as a convention sensitivity**, never as the decision.

### 1.4 Driver-sizing policy `w2_load_rule` (W-independent, the same rule for every fabric)

**Target:** every driver of a line or tap net must deliver an output transition **S = 0.30 ns** at its worst-case W-independent load.
- S is 10% of the 3.0 ns clock, the common open-flow maximum-transition convention.
- It is evaluated at the **tt** corner, where all bases are implemented (the 3.0 ns SDC).
- It was chosen before any Week 2 result. It is the same for every fabric.
- A tighter S favours the baselines' timing (their critical paths run through line drivers) and costs UBP the most tap area. A looser S does the opposite.

**Tap drivers (explicit rule):**
- Candidates: sky130_fd_sc_hd `buf_1, buf_2, buf_4, buf_6, buf_8, buf_12, buf_16`.
- The tap cell `LTAPB<k>` (R3; single-track met4 pad) or `LTAPBW<k>` (R2; 1.24 µm pad, as the historical R2 access used untracked placement) has:
  - timing: the `buf_<k>` Liberty, cloned per corner;
  - area: (2 + sites(buf_k)) × 0.46 × 2.72 µm²;
  - A-pin `max_transition` = S.
- **Worst-case load** C_wc = (m/K) × C_in(via-site A, tt) + c_met4 × L_RSMT.
  - L_RSMT is the rectilinear Steiner length of the tap plus every site of its segment in its band. It is computed exactly from the W-blind placement plan on the core the design itself implies (square core of area = cell area / U; fixed point over the tap class).
  - c_met4 is the platform's `setRC` value, 1.48128e-4 pF/µm.
  - No margin and no detour factor.
- **Choice:** the smallest candidate whose worst (rise, fall) NLDM output transition at input slew S and load C_wc is ≤ S. It is uniform per design (the worst tap decides).
- **Verification after the build:** the same computation is repeated on the built base's actual geometry. If the chosen class then fails, the base is rebuilt once with the next class. This is the only permitted iteration.
- **Worst-case check in sign-off:** program W5 (identical rows) connects every used line to every site of every segment, so it *is* the worst-case tap load. Its routed, extracted transitions are reported.

**Spine drivers (the physical flow):**
- The tap A-pin `max_transition = S` is enforced by the unchanged ORFS flow's own `repair_design`, at tt, with placement and then global-route parasitics. It resizes or buffers line drivers as needed.
- The sized drivers are therefore placed and routed in the frozen base. The achieved (extracted) transitions at the tap inputs are reported.

**Unchanged:**
- the logic;
- the R3 / R2 W-blind placement plans;
- the via sites (`VSITE`, 4 sites, `buf_1` stand-in);
- the 3.0 ns SDC, NO_DCE and the met1-rail PDN;
- base met1–met3, programs met4–met5;
- the ORFS image 69df744e2b5c, NUM_CORES 2 and the 64-iteration program DRT.

**Selection inputs** (W-independent, measured on the frozen unsized bases before this pre-registration; no performance data involved):

| Base (unsized) | Line driver | Largest spine load (tt, extracted) | Worst sink transition (tt) | Worst tap: sinks, L_RSMT |
|---|---|---|---|---|
| UBP3-R3 60% | `dfxtp_1` | 141.6 fF | 1.30 ns | 16, 140 µm |
| UBP3-R3 52% | `dfxtp_1` | 108.6 fF | 1.01 ns | 16, 150 µm |
| P2-R3 67% | `dfxtp_1` / `clkinv_1` | 211.7 / 169.5 fF | 1.95 / 1.37 ns | 16, 154 µm |
| A-R3 75% | `dfxtp_1` | 92.9 fF | 0.86 ns | 16, 167 µm |
| A-R2 75% | `dfxtp_1` | 50.5 fF | 0.47 ns | 64, 681 µm |
| P2-R2 67% | `dfxtp_1` / `clkinv_1` | 52.1 / 70.8 fF | 0.48 / 0.56 ns | 64, 629 µm |

### 1.5 Designs (all generated by `ubpgen`, all with policy `w2_load_rule`)

| Design | Fabric / access | U | Role in the decision |
|---|---|---|---|
| **B60** | UBP3, g = 3, K = 4, R3 | **60%** | the paper-facing UBP point |
| B52 | same | 52% | secondary sensitivity (built after the primary designs) |
| **A-R2** | per-input serial, R2 (K = 1) | 75% | the strongest validated A |
| **P2-R3** | bit-plane popcount, R3 (K = 4) | 67% | the pre-registered fairness point, the one that eroded UBP in the what-if |
| **P2-R2** | bit-plane popcount, R2 (K = 1) | 67% | the historically strongest P2 (unsized). Sizing could make it the strongest again, so it is built too |
| A-R3 | per-input serial, R3 | 75% | built if compute permits. Its period was base-set and it carries 4× the taps of A-R2, so it is not expected to be stronger. Included in the competitor set if built |

- **Utilization:** each design uses its established utilization.
- **If a design fails** base DRC, or any program fails DRT at 64 iterations:
  - **Baselines:** A is re-tried at 70% and P2 at 60%, and the routable point is used.
  - **B60:** its failure at 60% **triggers the kill** (60% is then not a legitimate operating point).

**Weight programs:** W1–W5 (seeds 1001–1005; unchanged; W14 not used) for every design.

**Every program must satisfy:**
- 0 DRT violations;
- frozen-base invariance (hash, placement, masters, met4/met5-only routing, power grid, programmable connectivity);
- post-PnR netlist = numpy W@x;
- oracle mutation detected.

### 1.6 Sign-off timing (the same for every design and program)

1. **Merged database:**
   - the base's routed `6_final.def`;
   - the program's routed pgm_* nets from the program DEF;
   - the program's master swaps.
2. **Extraction:** OpenRCX with the platform rules (`rcx_patterns.rules`; `define_process_corner -ext_model_index 0`), exactly as the ORFS final report runs it, then SPEF. This is **EXTRACTED**. One RC corner (the rules file has one); the RC is not varied across PVT (stated as a limitation).
3. **STA:** OpenSTA with three corners, the base SDC and propagated clocks.
   - **tt:** `tt_025C_1v80`, the ORFS library the bases were implemented with.
   - **ss:** `ss_100C_1v60`, the standard slow sign-off corner.
   - **ff:** `ff_n40C_1v95`, the standard fast / hold corner.
   - ss and ff come from the volare sky130A build `fa87f8f4…` (tarball sha256 `d4081b3c…`).
   - Its tt library is numerically identical to the ORFS tt: all 554,454 values agree to 6 significant digits. So the three corners share one characterization.
   - The custom cells are cloned per corner by the historical cloning procedure; with the tt library it reproduces the historical `g2_cells.lib` byte for byte.
4. **Recorded per corner and program:**
   - setup WNS and hold WNS over all paths;
   - T = 3.0 ns − setup WNS;
   - the critical path: start, end, whether it traverses a programmable net, and the largest-delay stage (cell and net);
   - the worst slack through programmable nets;
   - the achieved transition at tap inputs (spine) and at site inputs (programmable nets).

### 1.7 Metric and decision rule

- **A×T** = physical cell area (floorplan instance area, taps and sizing included) / U × cycles per word × T.
  - Cycles: 14 for B and A, 8 for P2.
  - The formula is unchanged. No credits: every W2 tap is physical.
- **Nominal comparison** (continuity): tt corner, with T from W1 (the established rule) and from the worst of W1–W5.
- **Conservative comparison (decisive):** T_cons = the worst over W1–W5 of T at the **ss** corner (the worst setup corner).
- **Hold:** must be ≥ 0 at every corner.
  - A hold violation is reported as a failure of that design at that corner.
  - A failing competitor is **not** dropped from the competitor set; that is conservative for UBP.
  - A hold failure of B60 is reported as a B failure.
- **Kill rule at 60%:** R = min over competitors {A-R2, P2-R3, P2-R2 (and A-R3 if built)} of A×T_cons / A×T_cons(B60).
  - **R < 1.5 → WEEK 2 KILL CONDITION TRIGGERED.**
  - **R ≥ 1.5**, with every B60 program valid → **WEEK 2 PASSED.**
- **Competitor set:** only designs built under the Week 2 physical model. The historical unsized designs carry idealized (area-free) tap buffers, so they are reported as historical rows, with their timing re-measured by the same sign-off where their programs are routed, but they are not decision competitors.
- **52%:** reported as a sensitivity. Its outcome does not change the decision.

### 1.8 Deviations

- Implementation bugs may be fixed and logged.
- The rule (S, corner, candidates, load formula, iteration), the corners, the metric, the programs and the kill rule do not change after any Week 2 result is seen.

---

## 2. Implementation (filled during the week)

### 2.1 Generator extensions (`ubpgen`, the only generation path)

| Module | Week 2 addition |
|---|---|
| `config.py` | `access.mode` (`r3` / `r2`), `drivers.policy` (`historical` / `w2_load_rule`), `drivers.slew_target_ns`, `drivers.tap_class`; illegal combinations rejected (r2 with K ≠ 1, unknown policy, a tap class without the W2 policy, `drive4` with the W2 policy, S outside [0.05, 1.5] ns) |
| `access.py` | R2 access (one tap per line, the validated `g2_struct` placer); the physical taps `LTAPB<k>` / `LTAPBW<k>` (LEF + Liberty for every candidate); per-corner clones of every custom cell |
| `drivers.py` | the `w2_load_rule` tap-class rule (1.4), its record, and its re-check on the built geometry |
| `pdk.py`, `liberty.py` | the pinned ss / ff libraries (sha256-verified download into an uncommitted cache); a minimal Liberty reader (areas, pin capacitances, NLDM tables) |
| `signoff.py` + `resources/signoff_*.tcl` | merged base + program DEF, OpenRCX extraction, one OpenSTA session per corner (1.6) |
| `accounting.py` | exact flow-sizing accounting: every final instance matched to the input netlist by flattened name and priced from Liberty |
| `week2.py`, `configs/suite_week2.json` | the per-design summary and the decision (1.7) |
| `golden.py` | the historical R2 builds (A at 75%, P2 at 67%) as golden references, alongside the R3 ones |

The historical path is unchanged:
- Every golden configuration defaults to `drivers.policy = historical`.
- All 49 files of each Week 1 golden design keep their Week 1 sha256; generation only adds new cell files.
- `access.mode = r2` reproduces the historical R2 builds of A and P2: byte-identical netlists and program TCL, semantically identical plan and flow configuration.

**Regressions:** the suite now has 104 tests, all passing: the 59 existing ones plus 45 new. The new tests cover:
- the driver-sizing rule is deterministic (same configuration → same choice and files);
- W does not affect the choice (other programs → the same class, base netlist, plan and flow configuration);
- illegal driver configurations fail;
- an explicit tap class that differs from the rule's choice is refused, and the one permitted rebuild (`drivers.post_build_step = 1`) takes exactly the next class;
- the golden unsized designs are unchanged;
- the sized base differs from the unsized one only by the tap master;
- the generalized Verilog programming equals the validated routine;
- tap-cell area, `max_transition` and timing;
- the corner clones, which reproduce the historical Liberty byte for byte at tt;
- the DEF merge, the path parser and the area accounting.

### 2.2 Tap classes chosen by the rule (resolved at generation, before any Week 2 build; now frozen in the configs)

| Design | Worst tap: sinks, L_RSMT | C_wc | Candidates tried (transition at S = 0.30 ns input slew) | Class | Taps × sites |
|---|---|---|---|---|---|
| B60 | 16, 143 µm | 56.3 fF | buf_1 0.653, **buf_2 0.278** | buf_2 (`LTAPB2`) | 2,192 × 6 |
| B52 | 16, 154 µm | 57.8 fF | buf_1 0.671, **buf_2 0.285** | buf_2 | 2,192 × 6 |
| P2-R3 | 16, 154 µm | 57.9 fF | buf_1 0.673, **buf_2 0.285** | buf_2 | 512 × 6 |
| A-R3 | 16, 166 µm | 59.6 fF | buf_1 0.693, **buf_2 0.293** | buf_2 | 512 × 6 |
| A-R2 | 64, 681 µm | 241.2 fF | buf_1 2.75 … buf_8 0.383, **buf_12 0.276** | buf_12 (`LTAPBW12`) | 128 × 18 |
| P2-R2 | 64, 633 µm | 234.0 fF | buf_1 2.67 … buf_8 0.372, **buf_12 0.268** | buf_12 | 128 × 18 |

Tap area against the historical accounting:
- B: 2,192 × 6 sites = 16,456 µm², against 5,485 µm² at 2 sites (+10,971 µm², +6.5% of B's cell area).
- A-R2 and P2-R2: 128 × 18 sites = 2,883 µm², against 1,281 µm² for the historical 8-site LTAP (itself credited down to 320 µm²).
- P2-R3: 512 × 6 sites = 3,844 µm², against 1,281 µm².

### 2.3 Clarifications recorded before any Week 2 build

1. **Area in A×T: the established floorplan instance area, unchanged.**
   - "Taps and sizing included" (1.7) refers to the tap sizing: the physical taps are netlist cells, so their full area is in the floorplan instance area.
   - The spine sizing is done by the unchanged flow *after* the floorplan (`repair_design` at global placement, 3_4 and 5_1), inside the fixed die (core = floorplan instance area / U). So it is not in the floorplan number. The die does not grow; the sizing cells take whitespace.
   - **Physical cost, measured and reported, never ignored:** `accounting.py` prices every resized input cell and every resizer-inserted cell. For each design it reports:
     - the flow sizing area;
     - the same for its unsized counterpart;
     - the increment, which is the Week 2 policy's spine-sizing cost;
     - the effect on routability, congestion, DRT convergence and hold.
   - **Sensitivities, reported and never decisive:**
     - A_incr = A + the increment;
     - A_phys = input-netlist area + all flow sizing;
     - A_conv = every tap at 2 sites, the historical convention.
   - **Why "all flow sizing" is not the decisive number.** The unsized historical builds already differ a lot in flow repair, all of it uncounted by the established metric:
     - UBP3-R3: 1,244 µm² (60%) and 1,104 µm² (52%);
     - A: 2,663 µm² (R2) and 2,635 µm² (R3);
     - P2: 38,361 µm² (R3) and 36,805 µm² (R2), mostly timing-driven-placement buffers.
   - Charging all of it would favour UBP by about 13% of P2's area. That would change the established metric in UBP's favour, so it is not done.
2. **Critical-path reporting.** The sign-off path reports carry the driven net of every stage (`-fields … net`), so the critical driver and net are recorded, not only the cell. The measured slacks are unchanged: the historical B60 W1 re-run gives identical tt / ss / ff slacks.

### 2.4 Implementation bug found in the first builds, fixed (1.8), builds restarted

- **What happened.** The first B60 and A-R2 bases (started 03:36Z) reached global routing, but the flow's `repair_design` had changed nothing at 3_4:
  - 0 cells resized;
  - 0 buffers inserted;
  - timing-driven placement found only 3 slew violations in the whole design.
- **Diagnosis** (OpenSTA probe of the placed database, placement parasitics):
  - the tap A pins had a slew of 0.74–0.88 ns;
  - OpenSTA reported **no** slew violation there.
- **Cause.** The sky130 `buf_<k>` input pin already carries `max_transition : 1.5`. The generator had *inserted* `max_transition : 0.30` in front of it instead of replacing it. Liberty's last attribute wins, so the limit stayed 1.5 ns and the pre-registered spine constraint was never seen.
- **Fix** (`access.w2_lib`): the existing attribute is replaced, so exactly one `max_transition = S` remains on every tap input, at every corner.
  - Probe with the fixed library on the same placed database: **2,192 of 2,192** tap pins violating, against 0 before.
  - A test now requires exactly one `max_transition` equal to S on every tap input.
- **Action.** Both partial builds were stopped before any program was routed or timed, and deleted. No Week 2 timing result existed. The designs are rebuilt from scratch with the fixed library; the rule, the classes and every other setting are unchanged.

**Second issue, found when the constraint became active (rebuild 04:00Z):**
- **What happened.** Every W2 base now stopped in timing-driven global placement with `RSZ-3006`: "Load pin 'lt_pn9_9_s0/A' is dont_touch. Cannot insert a buffer."
- **Cause.** The POST_SYNTH hook marks taps and via sites `dont_touch`, which protects them through synthesis and floorplan buffer removal. A load pin of a `dont_touch` instance cannot be re-connected, so `repair_design` can neither buffer a spine in front of its taps nor skip it; it aborts the flow. The historical designs never hit this because nothing violated at their taps.
- **Fix** (`access.W2_RELEASE`, W2 designs only). The placement hook releases `dont_touch` on the taps right after the W-blind placer fixes them FIRM; the via sites keep theirs.
  - FIRM cells are fixed for every later placer.
  - Probes on the failed B60 database: `remove_buffers` (which global placement runs first) keeps all 2,192 released FIRM taps (0 removed). `repair_design` then fixes all 548 spines (1,647 buffers inserted, 4 cells resized, +4.4% cell area), with 0 tap pins above S and a worst tap-input slew of 0.177 ns (placement parasitics).
  - The built-base check now also requires the full tap count, the configured master and FIRM status on every tap.
- **Action.** The four partial run directories (B60, A-R2, P2-R3, P2-R2; none past global placement) were deleted, and every design is rebuilt from scratch. The rule, the classes, the flow settings and everything else are unchanged.

## 3. Results

## 4. Decision
