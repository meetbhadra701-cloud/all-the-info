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

**Regressions:** the suite now has 106 tests, all passing at the end of the week. That is the 59 existing ones plus 47 new; the new count includes the config-load cases for the added configurations. The new tests cover:
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

**Third issue, in the new built-base check (not in the design):**
- The rebuilt B60 base completed at commit `d671f5d` with 0 DRC. The tap rule was met on its built geometry: worst tap `lt_pp20_0_s0`, 145.3 µm, 56.6 fF, 0.279 ns ≤ 0.30 ns, all 2,192 taps `LTAPB2`.
- It was nevertheless reported as failing, because the new check required FIRM status. ORFS writes every placed-and-fixed cell as FIXED in `6_final.def`, taps and via sites alike, exactly as in the historical bases.
- The check now accepts FIRM or FIXED (commit `dc081b6`).
- **No rebuild.** The frozen base was re-checked, and its ODB sha256 is identical (`ae09eb11…`). Its `records/base.json` carries the re-check commit; the build itself is `d671f5d` (see `physical/orfs_base.log`).
- The A-R2 base, built at the same commit, went the same way: 0 DRC; tap rule met (worst tap `lt_ln36`, 684.9 µm, 241.7 fF, 0.276 ns); 128 `LTAPBW12` FIXED. It was re-checked with an identical sha256 (`1d9398c9…`).
- Every later design was built after `dc081b6`.

### 2.5 Two further notes on the implementation

- **Legacy placement STA.** The validated program-routing script (reused unmodified) also runs a placement-parasitic STA. It reads only the historical tap libraries, so for W2 designs it cannot time through the taps. Its numbers are marked "n/a" for W2 designs and are used nowhere; every Week 2 timing number comes from the extracted sign-off, which reads every library.
- **Historical rows.** The unsized designs are re-timed by the same sign-off:
  - UBP3-R3 60% / 52% and P2-R3 67%: the Week 1 `ubpgen` reproductions. P2-R3's missing W2, W3 and W5 were routed here, with 0 DRC; all checks pass.
  - A-R3 75%: the Week 1 `ubpgen` point.
  - A-R2 75% (W1, W4, W5) and P2-R2 67% (W4): the historical G2 builds. These are the only programs routed historically. Their frozen base DEF/SDC and routed program DEFs are copied, unmodified, into the generated golden-R2 run directories, whose netlists are byte-identical to the historical ones.

## 3. Results

Every number here is either **MEASURED** (DRC, area, correctness) or **EXTRACTED** (timing: OpenRCX on the merged base + program, then OpenSTA at tt / ss / ff). The tap rule's pre-build estimates (2.2) are MODELED. Machine-generated tables: `ubpgen/results/week2/week2.md`; per-design records and sign-off reports: `ubpgen/results/week2/<design>/`.

### 3.1 What was physically built

| Design (`w2_load_rule`) | U | Taps (class × count) | Spine sizing by the flow: violating nets at placement → repeaters left in the frozen base | Cell utilization: floorplan → placement → final | Base DRC (DRT iterations) | Tap rule on the built geometry |
|---|---|---|---|---|---|---|
| **B60** UBP3-R3 | 60% | `LTAPB2` × 2,192 | 551 nets → 609 repeaters, 4,835 µm² (unsized: 58) | 60.4 → 64.1 → 69.6% | 0 (13) | worst tap 145.3 µm, 56.6 fF, 0.279 ns |
| **A-R2** | 75% | `LTAPBW12` × 128 | 80 nets → 293 repeaters, 2,625 µm² (unsized: 219) | 75.4 → 77.9 → 83.9% | 0 (14) | 684.9 µm, 241.7 fF, 0.276 ns |
| P2-R3 | 67% | `LTAPB2` × 512 | — | 67 → 77 → 83% | **not routable**: global routing congested (GRT-0116) | — |
| **P2-R3 fallback** | 60% | `LTAPB2` × 512 | 136 nets → 3,943 resizer cells in total (P2 repairs its row logic heavily either way; unsized 67%: 3,560) | 60.3 → 68.7 → 75.8% | 0 (19) | 166.1 µm, 59.7 fF, 0.294 ns |
| P2-R2 | 67% | `LTAPBW12` × 128 | — | 67 → 76 → 82% | **not routable**: global routing congested (GRT-0232) | — |
| **P2-R2 fallback** | 60% | `LTAPBW12` × 128 | 72 + 167 nets → 3,760 resizer cells in total (unsized 67%: 3,512) | 60.5 → 68.5 → 76.0% | 0 (16) | 671.3 µm, 239.7 fF, 0.274 ns |
| B52 | 52% | `LTAPB2` × 2,192 | 551 nets → 817 repeaters, 6,366 µm² (unsized: 51) | 52.3 → 56.2 → 61.1% | 0 (9) | 153.9 µm, 57.9 fF, 0.285 ns |
| A-R3 | 75% | `LTAPB2` × 512 | 130 nets → 492 repeaters, 4,394 µm² (unsized: 222) | 75.5 → 78.4 → 84.5% | 0 (9) | 168.3 µm, 60.0 fF, 0.295 ns |

For comparison, the unsized bases' timing-driven placement repaired only a handful of nets in its first pass (B60: 3 nets, 29 buffers; P2-R3: 8). Every tap stayed `FIXED` with the configured master. Every base met the rule on its built geometry, so the permitted rebuild was never used.

### 3.2 Programs

Every design, W1–W5:
- 0 DRT violations (64-iteration cap);
- frozen-base invariance;
- post-PnR netlist = numpy W@x, oracle mutation detected;
- pre-PnR W@x, oracle and program mutations detected.

| Design | DRT iterations W1–W5 | Correct |
|---|---|---|
| B60 sized | 14, 13, 6, 13, 1 | yes |
| B60 unsized (historical) | 13, 13, 7, 13, 1 | yes |
| A-R2 sized | 18, 14, 9, 14, 7 | yes |
| P2-R3 60% sized | 9, 9, 8, 13, 2 | yes |
| P2-R3 67% unsized (historical) | 14, 9, 7, 14, 3 | yes |
| P2-R2 60% sized | 13, 13, 13, 14, 5 | yes |
| B52 sized | 16, 15, 7, 13, 1 | yes |
| B52 unsized (historical) | 14, 13, 7, 14, 1 | yes |
| A-R3 sized | 13, 9, 8, 14, 1 | yes |

### 3.3 Extracted sign-off, three corners

Worst program per corner. T = 3.0 ns − setup WNS. "Prog" = worst setup slack through a programmable net.

| Design | Corner | Worst program | T (ns) | Hold WNS, min over W1–W5 | Critical path | Through programmable wiring | Largest stage (cell, net, delay) | Prog slack | Tap-input transition |
|---|---|---|---|---|---|---|---|---|---|
| **B60 sized** | tt | W3 | 2.134 | +0.208 | `stt3_ff` → row40 tree | **no** (control broadcast) | dfxtp_4, `st_tree`, 0.819 ns | +0.98 (W5) | 0.303 ns |
| | ss | W4 | **4.180** | +0.605 | `stt3_ff` → row40 tree | **no** | dfxtp_4, `st_tree`, 1.471 ns | −0.91 (W5) | 0.479 |
| | ff | W1 | 1.403 | +0.096 | row34 → output `y[34]` | no | output buffer, 0.509 ns | +1.72 | 0.229 |
| B60 unsized (hist.) | tt | W2 | 2.157 | +0.287 | spine `ng16_4` → tap → site → row41 | **yes** | dfxtp_1 spine flop, `pn16_4`, 1.195 ns | = critical | 1.321 |
| | ss | W2 | 4.213 | +0.622 | same | yes | dfxtp_1, `pn16_4`, 2.061 ns | = critical | 2.090 |
| | ff | W4 | 1.367 | +0.149 | output path | no | output buffer | +1.64 | 0.999 |
| **A-R2 sized** | tt | W2 | 2.184 | +0.073 | row24 → output `y[24]` | no | output buffer, 0.775 ns | +1.43 (W5) | 0.212 |
| | ss | W2 | **3.888** | +0.341 | `stt1_ff` → row59 tree | **no** (control broadcast) | buf_4 (placement buffer), 0.964 ns | −0.10 (W5) | 0.335 |
| | ff | W2 | 1.504 | +0.006 | output path | no | output buffer, 0.539 ns | +2.02 | 0.160 |
| A-R2 unsized (hist., W1/W4/W5) | ss | W1 | 4.208 | +0.307 | `stt1_ff` → row5 tree | no | dfxtp_4, `st_tree`, 1.322 ns | −0.89 (W5) | 0.748 |
| | ff | W1 | 1.481 | **−0.0001** | output path | no | | | |
| **P2-R3 60% sized** | tt | W4 | 6.040 | +0.345 | spine → tap → site → row popcount | yes | nor3_2, `g40_6[3]` (row logic), 1.32 ns | = critical | 0.274 |
| | ss | W4 | 11.245 | +0.685 | same | yes | nor3_1, `g48_6[3]` (row logic), 2.27 ns | = critical | 0.516 |
| | ff | W4 | 3.801 | +0.218 | same | yes | nor3_2, row logic, 0.92 ns | = critical | 0.185 |
| P2-R3 67% unsized (hist.) | tt / ss / ff | W4 | 6.927 / 13.097 / 4.440 | +0.024 / +0.221 / **−0.023** | spine → tap → row popcount | yes | row logic 1.27 / 2.32 ns | | 1.97 / 3.09 / 1.48 |
| **P2-R2 60% sized** | tt / ss / ff | W4 | 5.455 / 10.440 / 3.453 | +0.002 / +0.250 / **−0.038** | spine → tap → site → row popcount | yes | row logic (nor3_2 / o21ai_1, `g48_6[*]`): 1.29 / 2.31 / 0.90 ns | = critical | 0.254 / 0.401 / 0.192 |
| **B52 sized** | tt | W1 | 2.210 | +0.320 | `stt3_ff` → row47 tree | **no** (control broadcast) | dfxtp_4, `st_tree`, 0.913 ns | +1.11 | 0.307 |
| | ss | W1 | 4.398 | +0.651 | same | **no** | dfxtp_4, `st_tree`, 1.635 ns | −0.67 | 0.486 |
| | ff | W4 | 1.453 | +0.166 | output path | no | output buffer, 0.553 ns | +1.80 | 0.231 |
| **A-R3 sized** | tt / ss / ff | W4 | 2.219 / 4.380 / 1.485 | +0.092 / +0.341 / +0.012 | `stt1_ff` → row8 tree (tt, ss); output path (ff) | no | dfxtp_4, `st_tree`: 0.922 / 1.631 ns | +1.25 / −0.44 / +1.90 | 0.174 / 0.276 / 0.132 |

**Worst-case tap load check (1.4).** W5 connects every used line to every site of every segment. Its routed, extracted transitions at tt, against S = 0.30 ns:

| Design | Site inputs (the tap's far sinks) | Tap inputs (spine) |
|---|---|---|
| B60 | 0.283 ns | 0.298 ns |
| A-R2 | 0.266 ns | 0.212 ns |
| P2-R3 60% | 0.302 ns | 0.272 ns |
| P2-R2 60% | 0.283 ns | 0.254 ns |
| B52 | 0.285 ns | 0.305 ns |
| A-R3 | 0.288 ns | 0.174 ns |

- The MODELED rule and the EXTRACTED result agree to within 3%. P2-R3's sites are 2 ps over S, and B52's tap inputs 5 ps; both are reported, not adjusted.
- For comparison, the unsized historical builds:
  - B60: 0.168 ns at the sites (the idealized `LTAP2` carries `buf_4` timing in 2 sites), but 1.31 ns at its tap inputs;
  - A-R2: 0.634 ns at the sites.

### 3.4 Result table (60%; the conservative comparison decides)

A×T = floorplan instance area / U × cycles per word × T; T = the worst of W1–W5 at ss. "Relative to UBP" = A×T / A×T(B60 sized).

| Design | U | Driver policy | Area (µm²) | Worst-program period (tt) | Worst-corner period (ss) | A×T | Relative to UBP | DRC | Correct |
|---|---|---|---|---|---|---|---|---|---|
| UBP3-R3, unsized **(historical)** | 60% | historical: LTAP2 (2 sites, buf_4 timing); spines as synthesized | 169,952 | 2.157 ns (W2) | 4.213 ns (W2) | 16.71 M | 0.95 | 0 | yes |
| **UBP3-R3, physically sized (new)** | 60% | `w2_load_rule`: buf_2 taps × 2,192; spines by `repair_design` | 180,922 | 2.134 ns (W3) | 4.180 ns (W4) | **17.64 M** | 1.00 | 0 | yes |
| **A-R2, physically sized (new): the strongest physical baseline** | 75% | `w2_load_rule`: buf_12 taps × 128 | 358,018 | 2.184 ns (W2) | 3.888 ns (W2) | **25.99 M** | **1.47** | 0 | yes |
| P2-R3, unsized **(historical)** | 67% | historical | 274,662 | 6.927 ns (W4) | 13.097 ns (W4) | 42.95 M | 2.43 | 0 | yes; ff hold −0.023 ns |
| **P2-R3, physically sized (new)** | 60% (67% not routable) | `w2_load_rule`: buf_2 taps × 512 | 277,225 | 6.040 ns (W4) | 11.245 ns (W4) | 41.57 M | 2.36 | 0 | yes |
| P2-R2, physically sized (new) | 60% (67% not routable) | `w2_load_rule`: buf_12 taps × 128 | 276,264 | 5.455 ns (W4) | 10.440 ns (W4) | 38.46 M | 2.18 | 0 | yes; **ff hold −0.038 ns** |
| A-R3, physically sized (new) | 75% | `w2_load_rule`: buf_2 taps × 512 | 358,979 | 2.219 ns (W4) | 4.380 ns (W4) | 29.35 M | 1.66 | 0 | yes |

**R (conservative) = 25.99 M / 17.64 M = 1.473**, set by A-R2. The other competitors are weaker: A-R3 1.66, P2-R2 2.18, P2-R3 2.36. Every pre-registered competitor was built, and each was physically sized.

### 3.5 Why the conservative ratio is 1.47

1. **The driver-timing objection is closed.** Sizing moved UBP's programmable paths off the critical path at every corner:
   - tap-input transition 1.32 → 0.30 ns (tt);
   - programmable-path slack at ss −1.21 → −0.42 to −0.91 ns;
   - at tt, +0.98 ns or more.
2. **The ss period of both B60 and A-R2 is now set by the same W-independent control broadcast, not by programmable wiring.**
   - This is the reduction trees' start strobe `st_tree`: one flop to the first tree stage of all 64 rows.
   - The pre-registered rule sizes line and tap drivers only, for every fabric; this net is left to the unchanged flow, which closes timing at tt.
   - B60: the flop, flow-upsized to `dfxtp_4`, drives 25 loads and 256 fF directly, which costs 1.471 ns at ss. **T_ss = 4.180 ns.**
   - A-R2: the flow buffered the same net earlier (the flop drives 10 loads, 59 fF). **T_ss = 3.888 ns.**
3. **The flow's handling of this net shifts about ±0.3 ns with placement.**
   - The same `stt3_ff` path, timed on the same program (W4):
     - unsized B60: T = 3.893 ns at ss (then masked by the 4.11 ns spine path);
     - sized B60: T = 4.180 ns;
     - tt slack +1.035 → +0.867 ns.
   - A-R2 moved the other way: 4.208 ns unsized, 3.888 ns sized.
   - B60 needed a repeater on every spine: 551 violating nets at placement, 609 repeaters left in the frozen base, utilization 60.4 → 64.1% after placement. That changed its placement.
   - This is part of the physical cost of sizing: measured, not modeled.
4. **Area.** Physical taps cost B 2,192 × 4 extra sites = +10,971 µm² (+6.5% of its floorplan area), against +0.7% for A-R2 (128 taps).
   - Under the historical 2-site convention (a sensitivity, never decisive) the conservative R would be 1.557.
5. **Together.** R = (A-R2 area / 0.75) / (B60 area / 0.60) × T_A / T_B = 1.583 × (3.888 / 4.180) = **1.473**.

### 3.6 Physical cost of sizing

- **Area.** Tap buffers are in the floorplan instance area: B +6.5%, A-R2 +0.7%, P2-R3 +0.9%. Flow sizing on top (spine buffers and resizes), each against its unsized counterpart:
  - B60: 5,318 µm² (vs 1,244), increment **+4,074 µm²**;
  - A-R2: 3,080 µm² (vs 2,663), increment +418 µm²;
  - P2-R3 (60%): 42,463 µm² (vs 38,361 at 67% unsized), +4,103 µm²;
  - P2-R2 (60%): 40,480 µm² (vs 36,805), +3,675 µm²;
  - B52: 6,849 µm² (vs 1,104), +5,746 µm²;
  - A-R3: 4,850 µm² (vs 2,635), +2,215 µm².
- **Routability.**
  - P2 at its established 67% is **no longer routable** in either access mode: its cells grow from 67% to 82–83% utilization. The pre-registered 60% fallback routes cleanly.
  - B60 and A-R2 route their bases with 0 DRC in 13–14 DRT iterations (unsized B60: 10), with final cell utilization 69.6% (unsized 68.5%) and 83.9%.
- **DRT convergence (programs).** Unchanged within noise (above).
- **Hold.**
  - Every sized design holds ≥ 0 at every corner, except P2-R2 at ff: −0.038 ns, an input-port path. As pre-registered, it is reported as a failure of that competitor at ff and kept in the competitor set.
  - The tightest passing one is A-R2 at ff: +0.006 ns.
  - Three unsized historical designs fail hold at ff by 0.0001–0.023 ns: A-R2, A-R3 and P2-R3. These are input-port paths closed at tt only.

### 3.7 Ablation: unsized historical vs physically sized (conservative ss period, worst program)

| Fabric | Unsized T_ss | Sized T_ss | What limits the sized design at ss |
|---|---|---|---|
| UBP3-R3 60% | 4.213 ns (spine) | 4.180 ns | control broadcast |
| A-R2 75% | 4.208 ns (control) | 3.888 ns | control broadcast |
| P2-R3 | 13.097 ns (67%) | 11.245 ns (60%) | its own row popcount logic |
| P2-R2 | 10.395 ns (67%, W4 only) | 10.440 ns (60%) | its own row popcount logic |
| UBP3-R3 52% | 4.042 ns (spine W5; control path 3.965 ns) | 4.398 ns | control broadcast |
| A-R3 75% | 4.360 ns (control) | 4.380 ns | control broadcast |

### 3.8 Sensitivities (reported, not decisive)

| Variant | R |
|---|---|
| **Conservative, decisive** (ss, worst program, floorplan area) | **1.473** |
| Nominal: tt, W1 (the established rule) | 1.621 |
| Nominal: tt, worst program | 1.621 |
| ff, worst program | 1.680 (A-R3; A-R2 1.697) |
| Conservative + flow-sizing increment (A_incr) | 1.442 |
| Conservative + all flow sizing (A_phys) | 1.445 |
| Conservative, historical 2-site tap convention (A_conv) | 1.557 |
| 52% (B52 vs the same competitors), conservative / nominal | 1.213 / 1.355 |

## 4. Decision

**Pre-registered rule (1.7):** R = min over the physically sized competitors of A×T_cons / A×T_cons(B60); R < 1.5 → KILL.

- **B60 is valid:** 5 / 5 programs correct, 0 DRC, hold ≥ 0 at tt / ss / ff.
- **A×T_cons(B60)** = 180,922 µm² / 0.60 × 14 × 4.180 ns = **17.64 M**.
- **Strongest competitor: A-R2**, physically sized at 75%: 358,018 µm² / 0.75 × 14 × 3.888 ns = **25.99 M**.
- **R = 1.473 < 1.5.**

# WEEK 2 KILL CONDITION TRIGGERED

**Why, exactly:**
1. The driver objection itself is closed: UBP's programmable paths are no longer critical at any corner (3.5).
2. At the conservative corner, both B60 and A-R2 are limited by the same W-independent control broadcast, the tree-start strobe. The pre-registered rule does not size it, for any fabric, and the tt-closing flow buffered it worse in B60: 4.180 vs 3.888 ns. Before sizing, this path was 3.893 ns in B60, masked by the spine; sizing's placement changes moved it by +0.29 ns.
3. Physical taps cost B +6.5% area (2,192 taps), against +0.7% for A.
4. Together: 1.583 (area / U) × 0.930 (T) = 1.473.

**What the kill is not:**
- **Not a failure of programmability, correctness or routability at 60%.** B60 routes, and every program is exact and invariant.
- **Not a nominal failure:** at tt the ratio is 1.62.
- **It holds under every area accounting except the historical 2-site tap convention** (1.557), which the pre-registration excludes from the decision.

**Consequence (per the Week 2 instructions):** no new architecture and no rescue in this run; Week 3 is not started. The 52% point (secondary) is weaker still: 1.21 conservative, 1.36 nominal. Its larger core lengthens the same control broadcast (T_ss 4.40 ns).
