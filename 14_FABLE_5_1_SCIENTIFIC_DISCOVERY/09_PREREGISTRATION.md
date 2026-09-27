# 09 — Pre-registration: E5, the physical falsifier for regime-(V) wiring

Written before any E5 data.

## Hypothesis (H1.1, physical)

Weight-independent block-pattern fabrics keep a material area advantage after place-and-route at an equal clock: **routed core area of UBP-g ≤ routed core area of the per-input fabric / 1.5**, with detailed routing DRC-clean and timing met.

## Proposed mechanism under test

- UBP-g (g ∈ {3, 4}):
  - GEN(g) per input block (all canonical signed subset sums);
  - NEG per pattern line (shared negated lines);
  - TREE(⌈n/g⌉, w_g) per row.
- Each row leaf is connected, by the top-level netlist, to one pattern line, its negation, or a tie-low. That connection is **the via program**.

## Strongest baseline

The per-input universal fabric g1_V:
- NEG(8) per input (shared);
- TREE(n, 8) per row;
- each leaf connected to x_j, −x_j or tie-low.

This is the regime-(V) status quo (HNLPU / Ankhdjet style at the adder level).

## Inputs

- n = m = 32; i.i.d. ternary W (p0 = 0.4, numpy seed 14); symmetric INT8 activations in [−127, 127].
- Generalization run: n = m = 64, only if the n = 32 result advances and the budget allows.

## Controlled variables (identical for every design)

- **Library / PDK:** SKY130 HD (ORFS container `openroad/orfs:latest`, image id `69df744e2b5c`).
- **Module synthesis:** the same Yosys + ABC script (`synth -flatten; abc -liberty -D 4000; hilomap`), with the platform's DONT_USE cells excluded.
- **No cross-module optimization:** modules are synthesized once and instantiated. ORFS consumes the netlist via `SYNTH_NETLIST_FILES` (no re-synthesis).
- **ORFS flow:** default settings except CORE_UTILIZATION and the clock.
- **Clock:** a virtual clock of **6.0 ns** for all designs (iso-clock); input and output delays 0.

## Utilization protocol

- Each design is run at CORE_UTILIZATION ∈ {30, 45, 60} % (PLACE_DENSITY at ORFS defaults).
- The **routed core area** of a design is core area at the highest U whose detailed routing finishes with 0 DRC violations and no unrouted nets, with setup timing met (WNS ≥ 0).
- If no U satisfies this, the design is "not routable in the tested range".

## Measurement (from ORFS reports / metrics)

- Core area and instance (cell) area.
- DRC violation count after detailed routing.
- Total routed wirelength.
- Setup WNS / worst path at the finish stage.

## Independent validation

1. **Module level:** every synthesized module netlist is simulated by our own AIGER simulator (Yosys → AIG) against Python integer arithmetic (64 vectors).
2. **Top level:** the assembled top netlist (modules + ties) is converted by Yosys to an AIG and simulated against numpy `W @ x` (64 vectors).
3. **Negative control:** flipping one via connection must be caught.
4. **Physical level:** the ORFS final netlist is checked equivalent to the pre-PnR netlist with Yosys/ABC `cec`, where tractable. ORFS's own LVS is not available for this flow; the equivalence check stands in for it.

## Expected distinguishing behaviour (if the mechanism works)

- UBP routes at a utilization similar to g1's, keeping most of its ~1.6–2× cell-area advantage at n = 32.
- If select wiring dominates, UBP instead fails to route at the utilizations where g1 routes, or needs a much lower U.

## Kill and advance conditions

| ID | Condition | Classification |
|---|---|---|
| K5 | routed core area(g1_V) / min_g routed core area(UBP_V) < 1.3, or no UBP variant routable in range while g1 is | Wiring erodes the (V) advantage → **H1.1 MECHANISM FALSIFIED physically** → evolve to H1.2 (bit-serial) |
| A5 | ratio ≥ 1.5, with timing met for both | H1.1 physically supported at this scale |
| (between) | 1.3 ≤ ratio < 1.5 | weak support; record, and do not claim advance |

## Known interpretation limitations (declared)

- **Placement freedom.** The placer may arrange instances freely. A structured via-ROM array (fixed straps) is more constrained, so the result is optimistic for both designs.
- **Only used connections are routed.** A via fabric needs every candidate line to *cross* every site, which a real strap array provides without routing. The route here approximates that demand only when users are spread (random W).
- **Scale and technology.** Small layers (32×32) under-amortize the generator, which is conservative for UBP. One PDK only (SKY130, 5 metal layers).
- **Combinational only;** no pipelining; tie cells for zero leaves.
- **Novelty is not tested by E5.**

## Deviation log

The first three entries were logged before any E5 routing result was known.

- **D1 (validation item 1): module-level simulation is subsumed by top-level simulation.**
  - What was done: the assembled top netlist was simulated against numpy W@x with 64 random vectors, plus a mutation control. It exercises every module instance as used; the modules were not simulated one by one.
  - Why it matters little: a module error that never shows at the top cannot change the measured function.
- **D2 (validation item 4): the physical-level check is simulation-based, not formal `cec`.**
  - What is done: the ORFS **final routed** netlist (6_final.v) is converted by Yosys and simulated by our AIG simulator against numpy (64 vectors), plus a mutation control. Script: `scripts/post_pnr_validate.py`.
  - This is weaker than formal equivalence. It does catch any functional corruption by buffering, resizing or tie handling on the tested vectors.
- **D3 (negative-control form):** the mutation control flips the polarity of one nonzero weight in the *reference* (W → W′), rather than editing the netlist. Detecting W′ ≠ netlist is equivalent to detecting a one-via change in the netlist against W.
- **D4 (scheduling): runs are ordered U = 60, then U = 75, then U = 45** (the last only for designs that fail at 60). This does not change the definition of U_max over {45, 60, 75}.
- **D5 (E5 ubp4 U = 45).** Its U = 60 run stalled for several routing passes, so the U = 45 fallback was launched early (02:00 UTC), to save wall-clock time. At 02:31 U = 60 finished DRC-clean, so U = 45 was not needed and was stopped. The partial run is unused, and U_max = 60 as the protocol defines it.

## Amendment A1 — written after the 8×8 smoke build (module timing only) and BEFORE any n = 32 place-and-route data

**What the smoke build showed** (OpenSTA on Yosys/ABC-mapped SKY130 modules):
- Module delays are far above the ABC load-independent model used in the previous session's E3: NEG8 0.99 ns; GEN3 3.59 ns; TREE(8, 8) 3.40 ns.
- The UBP3 combinational path at 8×8 (8.1 ns) already exceeds the pre-registered 6.0 ns clock; g1's is 4.4 ns.

**Methodological defects this exposes:**
- (a) The pre-registered iso-clock would make E5 measure **timing repair**, not wiring. That confounds the question E5 exists to answer.
- (b) Budgeting module delays from pre-placement STA is unreliable, because post-placement repair and sizing change delays.

**Amended protocol (the original above is preserved):**
- **Synthesis:** every module is synthesized area-oriented (Yosys `abc -liberty`, no `-D`), with identical settings for all designs.
- **Clock:** a relaxed 20 ns virtual clock for all designs, so no timing repair is needed and WNS gives the natural delay.
- **Utilization sweep:** {45, 60, 75} % (the 30% point is dropped; 75 is added to find routability limits).
- **Routed area:** cell area / U_max, where U_max is the highest utilization with detailed routing at 0 DRC violations.
- **The iso-delay question** (a combinational delay penalty from generator/negator carry chains) is reported **separately** as natural post-route delay per design. It is not folded into the area ratio. Pipelining the generator stage, the realistic mitigation for throughput designs, is discussed and not tested.
- **K5 and A5 thresholds are unchanged** (1.3 / 1.5), now applied to cell area / U_max.
- **New reported (non-decisive) metric:** the delay ratio UBP / g1.

---

# E6 — pre-registration: evolution iteration 1 (H1.2, bit-serial)

Written before any n = 64 bit-serial data. The only prior data were the 8×8 smoke build: validation and module areas.

## Why an evolution iteration exists (what failed, what was learned)

- **What the E5 build revealed.** In bit-parallel combinational realizations, the generator's chained carry-propagate adders and the line negators sit **on the critical path**.
  - With OpenSTA on SKY130: UBP3's logic path is 9.37 ns vs g1's 6.57 ns at n = 32, a 1.43× delay penalty.
  - The previous session's ABC-model iso-delay (E3) understated this.
- **H1.1 has a second risk:** its select buses are (3^g − 1)/2 × w bits per site.
- **Technical change (H1.2):** make the fabric bit-serial.
  - Every generator step, negator and tree node is a 1-bit serial adder with registered sum and carry. The generator latency becomes pipeline latency (cycles), not clock period.
  - Lines become single wires, cutting select wiring w×.
  - Throughput is identical by construction: one output word every T = ow cycles in both fabrics.
- **Why it addresses the failure:** the clock period is set by one serial-adder stage for both designs. The delay penalty turns into a small latency difference (cycles), which throughput designs tolerate.

## Hypothesis

At an equal clock (3.0 ns) and equal throughput, bit-serial UBP-g fabrics have **routed area ≤ bit-serial g1 routed area / 1.5**, with detailed routing DRC-clean and setup timing met.

## Designs and inputs

- n = m = 64; the same W generator as E5 (seed 14, p0 = 0.4); symmetric INT8 streams, LSB first, sign-extended, T = ow cycles per word.
- **g1:** a shared serial negator per input line, plus STREE(n) per row.
- **UBP-g (g ∈ {3, 4}):** SGEN(g) per block (all canonical patterns, aligned), plus a shared serial negator per pattern line, plus STREE(⌈n/g⌉) per row.
- Zero leaves are tied low.

## Controlled variables

- The same Yosys/ABC area-oriented synthesis (plus `dfflibmap`) for every module; modules synthesized once and instantiated.
- ORFS defaults, SKY130 HD, a real clock on port `clk` (3.0 ns), CTS included.
- Utilization protocol as in Amendment A1: {45, 60, 75} %, with routed area = synthesized cell area / U_max.

## Independent validation

- The full top netlist is exported by Yosys (liberty cell functions) to a sequential AIG. Our own cycle-accurate simulator checks 12 back-to-back words against numpy W@x at the design's latency.
- One-connection mutation control.

## Kill and advance conditions

| ID | Condition | Classification |
|---|---|---|
| K6 | g1 / best UBP routed-area ratio < 1.3, or no UBP variant DRC-clean with timing met where g1 is | H1.2 falsified. Together with E5 this decides the mechanism class. |
| A6 | ratio ≥ 1.5, timing met for both | H1.2 supported at this scale |

**Also reported:** latency (cycles) of each design, and wirelength.

## Known limitations

- Placement freedom (as in E5).
- Random W.
- One size (64) and one PDK.
- The negator-per-line structure is kept for both designs. The complement-line + via-programmed constant-correction refinement, which would help both, is not tested.

## Amendment A2 (E5 and E6): weight-dependent pruning removed

A2 is a genuine methodological defect, found and fixed **before any corrected-run data**.

### What was found (23:45–00:05 UTC, after these runs finished)

- **Runs finished at that point:** E5 g1/ubp3 at U = 60; E6 ubp3/ubp4 at U = 60.
- **First source of pruning:** the netlist emission (`hierarchy; opt_clean -purge`) removed every negator instance whose output no row used.
  - E5 ubp3: 35 of 134 removed. E5 ubp4: 223 of 320. E6 ubp4: 156 of 640.
- **Second source of pruning:** ORFS's `synth_odb.tcl` runs `eliminate_dead_logic` after flattening. That removed generator logic feeding pattern lines no row selects.
  - E5 ubp3: 180 instances. E5 ubp4: 2,722. E6 ubp3: 190. E6 ubp4: 1,719.
  - g1: 0 in every run.

### Why this is a defect, not a result

- In regime V the base layers, i.e. the whole universal fabric, are **weight-independent**. Hardware for an unused line still exists on silicon.
- Pruning it per W is exactly the weight-specific optimization the hypothesis is not allowed to use.
- It understated UBP area: about 4% (E5 ubp3), 27% (E5 ubp4), 1.5% (E6 ubp3), 18% (E6 ubp4). The bias favours UBP.
- The pre-registration's own stated intent was "modules are synthesized once and instantiated; no cross-module optimization".

### Fix

1. **Emission:** every top-level instance gets `keep` (`setattr -set keep 1 top/t:*`), so negator instances are never removed. The rebuilt netlists hold the full fabric.
   - 134 / 320 / 274 / 640 negators, checked against the closed-form count.
   - Re-validated against numpy with the mutation control.
   - Script: `scripts/reemit_a2.py`; builders patched the same way.
2. **ORFS:** `eliminate_dead_logic` is disabled through a mounted copy of `synth_odb.tcl` (`scripts/orfs_patch/`). Nothing else in the flow changes.
3. **The g1 runs are kept as they are:** its netlists were already full fabrics (32 / 64 negators) and `eliminate_dead_logic` removed 0 instances. The patched and unpatched flows are therefore identical for g1.
4. **Area basis made precise.** "Synthesized cell area" = ORFS `synth__design__instance__area` (`1_synth.json`), i.e. the netlist as handed to ORFS.
   - It is taken **before** floorplan's `repair_tie_fanout`. That step splits each zero-leaf tie into one cell per load: +6,810 cells in g1 vs +430 in ubp3 at n = 32. This is an artifact that inflates g1: in a via fabric, zero is a ground connection.
   - Floorplan, final, and final-minus-ties areas are reported as sensitivity bases.

### Unchanged

The K5/A5 and K6/A6 thresholds, the utilization protocol, and the clocks.

### Preserved

The pruned runs' logs, netlists and summaries: `results/E*/pruned_A1_runs/`, `results/E*_pruned_A1_summary.md`. They are reported, not used for decisions.

### Known consequence

At U = 60, ubp3's actual cell load differs only slightly from the pruned run (1.5–4%). ubp4's differs a lot.

## E6 deviation log

- **D6.1 (netlist format; before any E6 PnR data): the top-level start-delay and alignment flip-flops were re-emitted as explicit `sky130_fd_sc_hd__dfxtp_1` instances.**
  - What happened: the first E6 ORFS launch failed at stage 1 for all six jobs (OpenSTA `STA-0171` syntax error). The top module still held behavioural `always @(posedge clk)` registers, which Yosys's Verilog backend writes with a `reg … = 0` initializer.
  - The fix: the same D flip-flops are instantiated as library cells, i.e. the cell `dfflibmap` would pick. Function, latency and every module are unchanged.
  - The build was re-run, and validation plus the mutation control were re-checked on the new netlist before PnR.
- **D6.2:** D1–D4 of E5 apply to E6 as well. The physical-level check uses the sequential simulator on 6_final.v (12 back-to-back words).

---

# Gates G2 and G3 — pre-registration

Written 2026-09-27, after Gate 1 (15_GATE1_NOVELTY.md) and **before any G2 or G3 data**.

## Why G3 runs first

Gate 1 established something from primary source (Ankhdjet RTL) and from summaries (HNLPU, BitROM): the frontier's arithmetic is **bit-plane popcount**. Each cycle it consumes one activation bit per input, counts signed hits per output, then shift-accumulates over the 8 bit-planes.

Our E6 baseline (A = g1-serial) used registered serial adders over 14 cycles/word instead. If the popcount per-input fabric beats UBP3-serial, then:
- UBP-serial is dominated regardless of fixed-base behaviour;
- G2 on UBP-serial would be moot.

G3's decisive measurement therefore runs first. G2 is pre-registered conditionally below.

## G3 — strongest competitor

**Metric:** **A×T** = routed area (µm²) × time per output word (cycles_per_word × achieved minimum clock period).
- Same technology and flow as E6: SKY130 HD, ORFS image 69df744e2b5c, NO_DCE, all instances kept.
- n = m = 64; ternary W (seed 14, p0 = 0.4); INT8 activations; 14-bit outputs.
- **Lower is better.**
- Routed area = synthesized cell area / U_max, U ∈ {60, 75}, DRC-clean and setup/hold met at a 3.0 ns clock.

**Designs:**

| ID | Design | Status of its numbers |
|---|---|---|
| A | g1-serial (E6) | MEASURED, reused |
| B | UBP3-serial (E6), **the thesis** | MEASURED, reused |
| P | **Bit-plane popcount per-input fabric** (HNLPU/BitROM/Ankhdjet arithmetic in spatial form = DA with K = 1). See the spec below. | To be MEASURED |
| D(K) | **Via-ROM distributed arithmetic**, K ∈ {2, 3, 4}, with and without OBC | MODELED |

**P specification:**
- Per input j: a shared current-bit line b_j and its complement b̄_j (one shared inverter).
- Per (row i, input j): a via selects b_j (w = +1), b̄_j (w = −1) or tie-0 (w = 0) into leaf slot (i, j).
- Per row: a combinational popcount of the 64 slots, then a pipeline register, then a shift-accumulator.
  - The accumulator's init value is a **via-programmed constant** c_i = #{j : w_ij = −1}. It is exact: complement lanes give −b = b̄ − 1, and the per-word correction for two's-complement INT8 is +n_neg.
  - The MSB plane is subtracted.
- 8 cycles per word, plus pipeline latency.

**D(K) specification:**
- Per block b and cycle t, the K current bits address a one-hot word-line decoder, shared by all rows.
- Per (row, block): a b_K-bit value is read from a 2^K-entry (2^(K−1) with OBC) via-ROM column group, with a sense per bitline.
- Per row: an adder tree over ⌈n/K⌉ values, then the same accumulator as P.
- **Model inputs:**
  - ROM cell area from Ankhdjet's silicon-verified SKY130 cell (2.21 µm² as built; 0.65 µm² raw; +20% array overhead; INFERRED/UNVERIFIED);
  - sense/precharge periphery (MODELED);
  - per-row datapath MEASURED at synthesis in our flow, then divided by the same U as P.

**Validation:** P and any revision design get sequential-AIG simulation against numpy W@x (bit-plane protocol), the mutation control, and post-PnR simulation of the final routed netlist.

**Kill and advance conditions for the thesis (B):**

| ID | Condition | Classification |
|---|---|---|
| K3a | A×T(P) ≤ A×T(B), both MEASURED routed | UBP3-serial is **dominated by the frontier-style per-input fabric**: killed as proposed (architectural competitiveness). E6's A6 was won against a weak baseline. |
| K3b | Conservative D(K) model (as-built 2.21 µm² cell) with A×T ≤ A×T(B) for some K | Substantially weakened (via-ROM DA equivalent or better) |
| S3 | A×T(B) ≤ 0.83 × min(A×T(P), A×T(D)), i.e. ≥ 1.2× better than every competitor | B survives G3 |

## Bounded revision R1 (only if K3a fires)

**R1 = UBP applied on top of the bit-plane popcount fabric ("UBP3-bitplane", design Q).**
- Per block of 3 inputs, a shared generator computes, **each cycle**, all 13 canonical pattern values of the 3 current bits. It computes both polarities in **offset code**: value + #negative entries ∈ [0, |q|], at most 2 bits.
- Per (row, block), a via selects one pattern bus or tie-0.
- Per row: a compressor over 22 leaves of ≤ 2 bits (vs P's 64 one-bit slots), plus the same accumulator. The via-programmed constant absorbs the offsets.

**Expected (DERIVED, before data):**
- The compressor shrinks by at most ≈ 64/44 ≈ 1.45×, and the accumulator is unchanged, so the whole-row gain is smaller.
- The select wiring stays at ≈ 44 programmable one-bit connections per row, vs P's ≈ 38.

**Distinguishing experiment:** PnR of Q vs P, same protocol and metric.

| ID | Condition | Classification |
|---|---|---|
| A-R1 | A×T(Q) ≤ A×T(P)/1.2 | Revision survives |
| K-R1 | A×T(Q) > A×T(P)/1.1 | Revision killed |
| (between) | | Inconclusive; no advance claimed |

## G2 — fixed-base programmability (conditional)

- It runs on the surviving UBP variant vs its strongest per-input baseline: **B vs A** if S3 holds; **Q vs P** if R1 survives.
- **If nothing survives, G2 is moot and is not run.** The reason is recorded.

**Protocol:**
1. **Base = everything W-independent:**
   - the fabric;
   - one **via-site cell** per leaf: pin Z on li1 drives the leaf; the programmable pin A is on met4;
   - one **line-tap cell** per line polarity: pin A on met1 from the line driver; programmable pin Z on met4;
   - a PDN confined to met1–met3.
2. **W-blind placement.** The base is placed once from W-independent connectivity only; there are no programmable nets during placement. `set_dont_touch` is set on all programmable pins; no W-dependent buffering or resizing.
3. **Base routing once** on met1–met3 only (`MAX_ROUTING_LAYER = met3`). Result: DRC and area.
4. **For each test matrix** (next item), programmable nets connect line-tap Z to via-site A. They are routed **on met4–met5 only**, in a run that contains only programmable nets; the base wires all sit at or below met3. Zero weights select the via-site's local tie option (identical footprint; no programmable wire).
5. **Test matrices:**
   - W1, W2: random, p0 = 0.4 (seeds 1001, 1002);
   - W3: sparse, p0 = 0.8 (seed 1003);
   - W4: dense, p0 = 0.1 (seed 1004);
   - W5: adversarial, every row identical (seed 1005), the maximum line fan-out;
   - real BitNet weights **if obtainable**. They are not expected: HuggingFace is blocked. If unavailable, the gap is documented.
6. **Measurements:**
   - base DRC;
   - per W: programmable-layer GRT overflow, DRT DRC, met4/met5 wirelength;
   - timing, MODELED: setup/hold at 3.0 ns with placement-based parasitics on the complete programmed netlist;
   - functional check: the complete programmed netlist (fixed base + W program) simulated against numpy;
   - a check that the program DEF contains no wires below met4;
   - a check that the base database is byte-identical across all W.

**Kill and advance conditions:**

| ID | Condition | Classification |
|---|---|---|
| K2a | UBP base needs a lower U than the baseline's base (met1–met3 only) and the resulting ratio < 1.5 | Weakened |
| K2b | Any test W fails programmable routing (overflow or DRC > 0) for the UBP variant where the baseline succeeds | Substantially weakened |
| K2c | Modeled setup fails for any W for UBP where the baseline passes | Weakened |
| K2d | Any W needs a lower-layer change: a program wire below met4, or a change to the base DB | Killed (not a fixed base) |
| A2 | All five W route DRC-clean on met4–met5, timing is met, and the ratio holds (≥ 1.5 for B vs A; ≥ 1.2 for Q vs P) | Advance |

## G3 deviation log

- **D-G3.1 (2026-09-27 04:00, before any P or P2 routed result).**
  - **What happened:** unpipelined P cannot be packed at U = 75 with the 3.0 ns clock. Its input→popcount path is 4.46 ns pre-route, so timing repair inflated it from 216,071 to 277,770 µm² (97% utilization). Detailed placement then failed (`DPL-0033`).
  - **Why this is a deviation:** holding the competitor to a clock chosen for B would weaken it artificially.
  - **Change:** P is re-run at a 5.0 ns clock (U = 75, then 60). The pipelined P2 keeps 3.0 ns.
  - **Unchanged:** A×T uses each design's achieved minimum period, so the metric is unaffected. The best of P and P2 is taken as "P" for K3a.

## G2 deviation log

- **D-G2.1 (baseline for G2).** Built before G3 finished: the P2 base (frontier-style per-input fabric) alongside B's.
  - The pre-registration named A for the S3 case.
  - A and P2 have the **same programmable structure**: 64 one-bit leaves per row, 2 line polarities per input. So G2's programmability test is equivalent for either. P2 is also the stronger per-input competitor if G3 shows it is.
  - The final G2 baseline choice is recorded with the G3 result.
- **D-G2.2 (power grid, 04:26 UTC, before any programmable-layer data).**
  - **What happened:** the first B base (met1 rails + met2 straps) routed DRC-clean on met1–met3. The final power-grid check then reported 169 via-site / line-tap stacks shorting the met2 straps (`PSM-0043`). A fixed base cannot have via stacks through power straps.
  - **Change:** the base PDN is **met1 follow-pin rails only**, with no straps on any layer, and IR-drop analysis is disabled. Power integrity is out of scope.
  - **Consequence:** this favours every design equally, since no strap tracks are consumed. A real base would co-design strap columns with the via-site arrays at an equal area cost. Superseded log: `experiments/results/G2/superseded_strapPDN/`.

## G2 pre-registered outcome (recorded 2026-09-27 ~06:35 UTC, before any R2 data)

**Bases:** every fixed base is DRC-clean on met1–met3:
- UBP3 at U ∈ {60, 45, 30, 15, 8};
- P2 at U ∈ {60, 45};
- A at U = 60.

**Programmable GRT on met4–met5.** Cells give the overflow count; 0 = routes.

| Design | U | W1 | W2 | W3 | W4 | W5 |
|---|---|---|---|---|---|---|
| UBP3 | 60 | 14,159 | 14,304 | 2,106 | 9,913 | 0 |
| UBP3 | 45 | 14,719 | 14,755 | 1,849 | 9,790 | 0 |
| UBP3 | 30 | 16,621 | 16,562 | 112 | 10,075 | 0 |
| UBP3 | 15 | 12,291 | 12,263 | 0 | 3,134 | 0 |
| UBP3 | 8 | 2,619 | 2,139 | 0 | 0 | 0 |
| P2 | 60 | 466 | 415 | 0 | 3,962 | 0 |
| P2 | 45 | 0 | 0 | 0 | 519 | 0 |
| A | 60 | 0 | 0 | 0 | 108 | 0 |

**DRT at U60 (programmable nets only, met4–met5).** No design converges:
- A W1: 12,727 → 10,665 after 6 iterations. 8,814 of the violations are net-to-net met4 shorts; only 262 involve pins.
- P2 W1: 24,818 → 23,178.
- UBP3 W1: 66,520 → 121,693.

**Classification:**
- **K2b fires.** W1 and W2 fail for UBP3 at every U down to 8%. A routes them at U60 and P2 at U45, at GRT level. → **substantially weakened**.
- **K2d does not fire.** No program wire lies below met4, and the base ODB hashes are recorded (`results/G2/base_odb_sha256_before_programs.txt`).

**Diagnosis (overflow maps):**
- The generic, connectivity-driven base placer cannot see the programmable nets, so it clusters every line tap next to the line generators and input pins.
- A: all 128 taps sit within an 80 × 190 µm patch at the die edge.
- UBP3 at 8%: 2,476 of 2,484 GRT overflows form one vertical stripe through the tap cluster. Its 499 used lines leave one patch, and the horizontal capacity across that patch (met5 at 3.4 µm pitch) grows only with the die side.
- This is a **placement-methodology** failure mode, and it penalizes the design with the most lines. It does not show that a W-blind base must fail.
- Hence the one bounded revision below.

## R2 — structured (crossbar) W-blind base — the one bounded revision + distinguishing experiment

Written before any R2 data. This is a **methodology** revision; the architecture is unchanged.

**What changes and what doesn't:**
- The base netlists and the via programs are unchanged; only the placement of the programmable-pin cells is fixed, W-blind, before global placement (`scripts/g2_struct.py`, ORFS `POST_PDN_TCL`).
- **Bands:** one vertical band per line group: 22 bands for UBP3, one per 3-input block, 26 taps each; 64 bands for P2 and A, one per input, 2 taps each.
- **Via sites:** the site of (row i, band k) sits at the band centre, at core height (i + 0.5)/64.
- **Taps:** the band's taps sit next to the site column, spread evenly over the height; tap t of T sits at (t + 0.5)/T.
- These cells are FIRM. Everything else is placed by ORFS from base connectivity.
- Protocol, cells, PDN, programs, layers and tools are otherwise identical to G2.

**Prediction (DERIVED, `scripts/g2_track_model.py` extended to spread taps, before data):**
- UBP3's densest band needs 23 of the band's met4 tracks (W2). Its programmable-layer-limited U_max is therefore ≈ 44% if 75% of met4 tracks are usable, or ≈ 63% if 90% are.
- P2 and A need 2 tracks per band, so their programmable layers are not binding.

**Grid:**
- B (UBP3): U ∈ {60, 52, 45}
- P2: U ∈ {60, 67}
- A: U ∈ {60, 75}

**Primary criterion (U routes):** base DRC 0 on met1–met3 **and** GRT overflow 0 on met4–met5 for all five W.
**Secondary criterion:** DRT (20 iterations) on the W with the largest GRT wirelength converges to 0 violations.
**U_max:** the highest routed U in the grid.

**Metric:** A×T = (G2 base synthesized cell area) / U_max × cycles/word × T.
- Base cell areas: B 169,952; P2 274,662; A 356,417 µm².
- T = 3.0 ns − min(final setup WS of the base, modeled setup WS of the W1-programmed netlist through programmable nets).

**Conditions:**

| ID | Condition | Classification |
|---|---|---|
| R2-A | A×T(B) ≤ A×T(P2)/1.2 **and** ≤ A×T(A)/1.5 at the primary U_max, **and** B's secondary criterion holds | G2 passes after R2 (advance) |
| R2-K | A×T(B) > min(A×T(P2), A×T(A))/1.1, **or** B routes no U in its grid | R2 killed. G2 fails, so the via-programmable claim is killed. |
| (between) | | G2 unresolved |

**If DRT fails for every design** (as at unstructured U60), the secondary criterion is reported as a testbed limit (SKY130 met4/met5 pitch and via4 size) and R2-A cannot be granted.
