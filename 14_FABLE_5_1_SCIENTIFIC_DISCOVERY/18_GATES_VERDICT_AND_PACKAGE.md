# 18 — Gates verdict and research-development package (Wave 14, gates G1–G3)

**Labels:**
- **MEASURED:** our flow — SKY130 HD, ORFS image 69df744e2b5c, own cycle-accurate simulator vs numpy.
- **MODELED:** placement-parasitic timing, and the DA periphery.
- **DERIVED:** exact counts and bounds.
- **INFERRED:** third-party silicon data, e.g. Ankhdjet's ROM cell.
- **UNVERIFIED:** not checked.

**Details:**
- Gate 1: `15_GATE1_NOVELTY.md`.
- Gate 2: `16_GATE2_FIXED_BASE.md`.
- Gate 3: `17_GATE3_DA_COMPETITOR.md`.
- Every condition was pre-registered in `09_PREREGISTRATION.md` before its data.

## 1. Gate outcomes and what failed

| Gate | Pre-registered outcome | Failure class |
|---|---|---|
| **G1** novelty / obviousness | **Materially downgraded, not killed.** No identical or technically equivalent mechanism was found; the one primary source (Ankhdjet RTL) is g = 1 per-weight accumulation. The combination (LUT-GEMM activation-group sharing + a via/metal-programmable W-independent base) is **likely obvious**. What remains is the physical consequences. | **Novelty** (downgrade) |
| **G3** strongest competitor | **Survives (S3).** Hardwired-W regime, all MEASURED and post-PnR validated: B is **1.84×** better in A×T than the frontier-style bit-plane popcount fabric P2, **2.50×** better than P, and **2.27×** better than A. Via-ROM DA (K ≥ 2) is never smaller than the K = 1 popcount fabric for ternary W (DERIVED + MEASURED + INFERRED). | — |
| **G2** fixed-base programmability, **generic placement** (pre-registered protocol) | **K2b fires → substantially weakened.** B's random programs do not route on met4–met5 at any base utilization from 60% down to 8%; A routes them at 60% and P2 at 45%. K2c (timing) and K2d (lower-layer change) do not fire. | **Physical programmability**, diagnosed as **methodology** (the placer clusters all line taps) |
| **G2 / R2** structured W-blind crossbar base (the one bounded revision) | **Primary criterion (GRT):** B routes all five W at U60. Its A×T is **1.85×** better than P2 and **1.76×** better than A, each baseline taken at its own best U (P2 67%, A 75%). **Secondary criterion (DRC-clean detailed routing in 20 iterations): B fails** at U60 / 52 / 45 (1,167 / 881 / 416 met4 violations, falling). P2 and A pass at every U tested. Pre-registered classification: **R2-K not fired, R2-A not granted → G2 UNRESOLVED**. *Post hoc (64 iterations, the router default): B closes DRC-clean at U45 but not at U52 (117) or U60 (410). At U45 it is 1.40× better than P2 but only 1.33× better than A (bar: 1.5×)* (§5.5 of 16). | **Physical programmability (unresolved)** |

## 2. Classification: **PROMISING BUT KEY GATE UNRESOLVED**

- **Not THESIS KILLED:**
  - No pre-registered kill fired: G1 was downgraded; G3 passed; G2 was substantially weakened on the generic protocol; and R2-K did not fire.
  - Weight changes never move base cells or touch forbidden layers.
  - On the structured base, routing and timing do not collapse. B keeps a 1.76–1.85× A×T advantage at GRT level over each baseline's best, and has the fastest programmable paths.
  - The thesis is not dead. Its key physical claim is unproven.
- **Not READY FOR FULL RESEARCH DEVELOPMENT:**
  - The thesis is about a **weight-independent** fabric, and there its advantage is not physically closed.
  - B misses the pre-registered DRC-clean detailed-routing criterion at every tested utilization (1,167 / 881 / 416 residual met4 violations at U60 / 52 / 45), where both per-input competitors close at U60.
  - After G1, the physical characterization is the only candidate contribution. An unclosed G2 therefore leaves the contribution unestablished.
- **The key unresolved gate: G2 closure.** Does a W-blind fixed base exist in which B's programmable layer routes DRC-clean for all test W, at a utilization where B stays ≥ 1.2× better than P2 and ≥ 1.5× better than A in A×T?
  - One pre-registered site/tap co-design experiment (§3, Q11, weeks 1–2) decides it.

---

## 3. The research-development package (the 12 questions)

The prompt asks for this package if the thesis survives all three gates. It did not fail any gate outright: G2 is unresolved, not failed. The package is given anyway, because it states exactly what is established and what is not. Read it with G2 open.

### 1. What exactly is new?

**The mechanism** (UBP-g, bit-serial):
- Per block of g = 3 inputs, one weight-independent generator emits every cycle the serial values of all (3³ − 1)/2 = 13 canonical signed patterns, plus their negations: 26 lines, shared by all rows.
- Each row selects one line per block, or a local zero, by a via/top-metal connection.
- A per-row adder tree covers ⌈n/3⌉ leaves instead of n.

**What is new is not the arithmetic.** Per G1 it is a likely-obvious composition. What is new is the physical characterization of that composition. None of the following appears in any retrieved source:
- **Hardwired regime:** 2.13× less routed area than a per-input serial fabric, and 1.84× better A×T than the frontier's bit-plane popcount fabric (MEASURED, DRC-clean, validated).
- **Fixed base, generic placement:** the 26-lines-per-3-inputs requirement collapses programmable routing.
- **Fixed base, structured crossbar:** GRT routability is restored with a 1.76–1.85× A×T advantage (modeled timing). Detailed-route closure on SKY130's two programmable layers is not reached in the pre-registered 20 iterations, where the per-input fabrics close.
  - Post hoc, with the router's default 64 iterations, B closes at U45 but not at U52 or U60. At U45 its A×T is 1.40× better than P2 but only 1.33× better than A.
- **The line-count / line-load trade-off:** UBP needs 4.3× more programmable lines, but each is lightly loaded (≈ 2.6 sinks), so UBP's programmable paths are the fastest of the three designs.

### 2. What is already known?

- **Four Russians / Lupanov:** shared subset-sum tables.
- **T-MAC, LUT Tensor Core, TENET:** activation-group LUTs shared across outputs, mirror-half symmetry, runtime-indexed.
- **CSHM:** a universal precompute with per-constant selection at g = 1.
- **Via/metal-programmable W-independent bases:**
  - HNLPU "Sea-of-Neurons", a structured ASIC with metal-layer weights and POPCNT;
  - Taalas;
  - WO2025217724A1;
  - Ankhdjet's via-ROM NOR tile (primary source read).
- **Compute-in-ROM:** BitROM, TOM, YOLoC.
- **Distributed arithmetic** and via-ROM DA (Peled–Liu 1974; White 1989).
- **Structured ASICs** and via-configurable gate arrays.

The bit-plane popcount arithmetic of HNLPU, BitROM and Ankhdjet is DA with K = 1. Our P and P2 designs are its spatial form.

### 3. Why is the remaining difference scientifically substantive?

**The honest answer is that it is only partly established.**

**What is substantive, because it was not predictable from the references:**
- **The sign of the result depends on the implementation form:**
  - bit-parallel UBP loses a utilization step (E5);
  - bit-serial UBP wins 2.1× (E6).
- **The fixed-base cost is reachability, not port count.** UBP minimizes programmable ports (Theorem 1), yet in a W-blind base every port must be able to reach any of 26 lines. That multiplies programmable track demand 4.3× per input, the opposite of what the port count suggests.
- **That cost can be absorbed at GRT level only by a structured crossbar base.** Connectivity-driven placement fails at every utilization.

**What is not yet substantive:** a DRC-clean fixed-base UBP at a utilization where it beats the per-input fabrics.
- Until R2's secondary criterion is met, the advantage in the thesis's defining regime rests on global routing plus modeled timing, not on closed physical design.

### 4. What theorem / bound do we have?

**Exactness (DERIVED):**
- Every nonzero ternary g-vector is ± one of (3^g − 1)/2 canonical patterns.
- So each row's block contribution is exactly ±(pattern · x_block) or 0, for every W.

**Theorem 1** (previous session, proven): a universal fabric with fan-in s needs P ≥ mn·log₂3 / log₂(2s − 1) programmable ports, and UBP-g meets this with equality.

**Reachability bound (DERIVED; new in G2):**
- A W-blind base must make (3^g − 1)/g lines per input reachable from every row: 26/3 ≈ 8.7 vs 2 for per-input fabrics.
- In a structured crossbar, the densest band needs as many met4 tracks as the maximum overlap of its line intervals.
- For the random W that is 22–23 of the band's 26 lines (W3: 13; W4: 19). On SKY130 met4 (0.92 µm pitch) this bounds B's programmable-layer U_max to ≈ 44% at 75% track usage and ≈ 63% at 90% (`scripts/g2_track_model.py`, spread taps).
- The measured DRT behaviour is consistent with this bound: not closed at 45–60, and the residual falls with U, from 1,167 to 416.

**DA bound (DERIVED):**
- A ternary K-input DA leaf needs b_K = ⌈log₂(2K + 1)⌉ ≥ K bits for K ≤ 4, so it saves no compressor bits over K = 1.
- Its ROM grows as 2^K.
- For DA to beat the K = 1 fabric, its ROM cells would have to cost < 0.06 µm² in SKY130.

### 5. What physical results do we have? (all MEASURED, SKY130 HD, 64 × 64, INT8 in / 14-bit out, post-PnR validated)

| Regime | Result |
|---|---|
| Hardwired (E6) | B routed area 209,255 µm² vs A 445,579 µm² at U75, both DRC-clean, timing met at 3.0 ns. |
| Hardwired (G3) | A×T: B 6.10e6; P2 11.23e6; A 13.84e6; P 15.24e6 µm²·ns. |
| Fixed base, generic placement (G2) | B's W1/W2 overflow at every U ≥ 8%; A routes 4 of 5 W at U60; P2 routes 4 of 5 at U45. Base ODBs byte-identical across all programs; program wires only on met4/met5. |
| Fixed base, structured (R2) | All three designs route all 5 W at U60 at GRT level. Programmable WL: B 172 mm, P2 98 mm, A 107 mm. DRT closes for P2 and A at U60 but not for B at 60 or 52 in 20 iterations. At U45, B is left with 416 violations. |

### 6. Does the base fabric truly remain reusable across weights?

**Logically and at the mask level, yes (MEASURED):**
- One frozen base (cells plus met1–met3) was programmed with five different W, using only met4/met5 nets and identical-footprint via-site master swaps.
- Every base database stayed byte-identical.
- No program wire fell below met4.
- The complete programmed netlists match numpy W@x, with mutation controls.

**Physically, for B, not yet closed:**
- On the structured base, every program routes at GRT level.
- Detailed routing of B's programmable layer leaves 1,167 / 881 / 416 met4 violations at U60 / 52 / 45 after 20 iterations.
- The per-input fabrics close.

**Real model weights were not tested:** HuggingFace is blocked in this environment.

### 7. How does UBP compare with the strongest via-ROM / DA alternative?

**Spatial via-ROM DA:**
- With ternary weights, the via fabric already gets each input's multiplication (a sign) for free.
- A K-input table leaf is at least as wide as K one-bit leaves (K ≤ 4).
- So D(K ≥ 2) is never smaller than K = 1 popcount (P), even with an optimistic 0.65 µm² ROM cell (§2 of 17).

**Time-multiplexed via-ROM (Ankhdjet):**
- Far denser: 2.21 µm² per weight.
- But ≈ 512 cycles per dot product at 64-row sub-columns, which makes it ≈ 10–40× worse in A×T. It is a different, area-first operating point.

**The best P-class fabric (P2) vs B:**
- Hardwired: 1.84× worse in A×T (MEASURED).
- Structured fixed base, at GRT level with modeled timing: 1.85× worse (1.65× if P2's slow programmable lines are ignored). P2 closes DRT; B does not in 20 iterations.
- DRC-clean comparison (post hoc, B at U45 with 64 iterations): P2 is 1.40× worse (1.25× if its line delay is ignored).

### 8. What is measured vs modeled?

| MEASURED | MODELED | DERIVED | INFERRED | UNVERIFIED |
|---|---|---|---|---|
| Routed areas, U_max, DRC counts, GRT overflow, programmable WL, DRT trajectories, base-flow STA (routed parasitics), post-PnR functional equivalence, base immutability | Timing of programmed netlists (placement parasitics), DA periphery (sense 5–15 µm²) | Pattern counts, Theorem 1, reachability/track bound, DA bit-width bound, A×T arithmetic | Ankhdjet ROM cell area (2.21 / 0.65 µm²) | HNLPU / Taalas internals (full texts blocked), advanced-node behaviour, energy, real-model weights |

### 9. What is the proper scope?

- **Weights:** ternary {−1, 0, +1}. Binary is a special case with fewer patterns: 2^(g−1) for ±1.
- **Activations:** INT8.
- **Bit-serial** (14 cycles per 14-bit output word) is the only form with a clear advantage; the bit-parallel form was weakened in E5.
- **Measured size:** 64 × 64 only, one layer, g = 3 (g = 4 measured in E6 at 1.77×).
- **Process:** SKY130 HD, with only two programmable layers (met4 0.92 µm, met5 3.4 µm, 0.8 µm via4).
- **"Via/metal-programmable"** here means top-metal programming (met4–met5 nets + via-site masters). Single-via-layer programming was not tested.

### 10. What is still missing before a paper?

1. **DRT closure of B's programmable layer on a fixed base** at a utilization that keeps ≥ 1.2× over P2 and ≥ 1.5× over A, i.e. U ≥ ≈ 51%.
   - Today B closes only at U45 (post hoc, 64 iterations).
   - This needs site/tap co-design (staggered site columns, split taps, pin pads off the line tracks) or a third programmable layer. Each is a new, separately pre-registered revision.
2. **Scale:** n, m ≥ 256–1024. The line count grows with n; the reachability bound must be re-checked.
3. **Real ternary weights** (BitNet b1.58) through the full G2 protocol.
4. **An advanced node,** or at least a PDK with ≥ 3 thin programmable layers, and single-via programming.
5. **Energy / power** with activity from real activations.
6. **Full texts** of HNLPU, the Taalas patents, TENET and T-MAC, to settle G1 (currently summary-based).
7. **A W-specific structured-ASIC CSE baseline** (G1's "◐ competitor").

### 11. What should the next 4–8 weeks look like?

| Weeks | Work | Decision point |
|---|---|---|
| **1–2 (decisive)** | **G2 closure.** Pre-register **R3**, a site/tap co-designed band: via sites staggered across the band so each met4 pad owns a track; taps split into two half-height groups; pads kept off line tracks. Route at the router default (64 iterations). Run B at U52–60 vs P2 at 67 and A at 75, with R2's other criteria. Sensitivity: a third programmable layer (base met1–met2). Post hoc, R2 with 64 iterations closes B only at U45, which is not enough vs A. | **Kill** the via-programmable claim if B cannot close at a U that keeps ≥ 1.2× over P2 and ≥ 1.5× over A. Otherwise G2 passes. |
| 3 | **Novelty closure.** A person with access reads HNLPU (ASPLOS'26), the Taalas filings (WO2025217724A1 applicant, HC-series) and the TENET / T-MAC full texts. Settle "anticipated" vs "obvious composition". | If anticipated: stop, or rescope to the physical study only. |
| 3–4 | **Real weights.** BitNet b1.58 layers (supplied locally; HuggingFace is blocked here). 64 × 64 tiles through the full G2 protocol on the winning base. | Kill if real-weight programs fail where random ones pass. |
| 5–6 | **Scale.** One 256 × 256 tile. Re-derive the reachability bound: lines grow ∝ n and sinks per line ∝ m, so the band density changes. Measure it. | Kill if the per-band track demand grows faster than the band width at scale. |
| 7–8 | **Advanced stack and energy.** A PDK with thin programmable layers (e.g. ASAP7 M6–M9, or single-via programming at one via layer); activity-based power with real activations; a paper outline if every earlier gate passed. | Advance to "READY FOR FULL RESEARCH DEVELOPMENT" only if G2 closure and the novelty closure both pass. |

### 12. What is the strongest reviewer objection still standing?

> "This is LUT-GEMM with the index hardwired — an obvious composition. Its advantage was demonstrated only where the layout could see the weights. In the regime the paper is about — a weight-independent base — the 4.3× larger programmable line set collapses under standard placement. It routes only with a hand-structured crossbar, and even then its detailed routing does not close on the process used, while the per-input fabrics' does. Show a DRC-clean fixed base, at scale, with real weights, that still beats the popcount fabric."

We cannot yet rebut the last sentence.
