# 19 — Final UBP decision (R3: the last layout revision)

**Verdict: {{VERDICT}}**

{{VERDICT_WHY}}

**Labels:**
- **MEASURED:** our flow — SKY130 HD, ORFS image 69df744e2b5c, own cycle-accurate simulator vs numpy.
- **MODELED:** placement-parasitic or lumped-RC timing.
- **DERIVED:** exact counts and models.
- **UNVERIFIED:** full texts that could not be read.

**Sources:** the pre-registration is in `09_PREREGISTRATION.md` (section R3), written, committed and pushed before any R3 physical result. Raw records: `experiments/results/G2/r3/`.

---

## The decisive experiment in one table

{{DECISIVE_TABLE}}

---

## A. Exact contribution

{{CONTRIBUTION}}

## B. Algorithm / architecture (precise enough to re-implement)

**Arithmetic (UBP-g, g = 3; bit-serial).**
- **Input:** x ∈ INT8ⁿ as two's-complement serial words, LSB first. Words are sign-extended to the output width w_o = 14, so one word takes 14 cycles; `start` marks bit 0.
- **Blocks:** the n inputs are split into ⌈n/3⌉ blocks of 3 consecutive inputs; the last block may be shorter.
- **Canonical patterns:** for a block of size g, 𝒫_g is the set of non-zero ternary g-vectors whose first non-zero entry is +1. |𝒫_3| = 13, |𝒫_1| = 1.
- **Generator SGEN(g), one per block, W-independent:**
  - It emits, every cycle, one serial bit of each pattern value p·x_block for all p ∈ 𝒫_g.
  - It uses registered serial adders and subtractors: sum = a ⊕ b ⊕ c, carry = maj(a, b, c), reset at `start`; subtraction complements b and presets carry-in to 1.
- **Negator SNEG, one per pattern:** it emits −(p·x_block) serially (~a + 1), and delays the positive stream by one cycle to keep the two aligned.
- **Lines:** each block has 2|𝒫_g| lines (26 for g = 3), shared by all m rows. In total there are 548 lines for n = 64.
- **Row i:** a registered serial adder tree STREE over ⌈n/3⌉ leaves (22 for n = 64). Leaf (i, b) is one line of block b or the constant 0.
- **Programming (the only W-dependent step).** For row i and block b, let q = (w_{i,3b}, w_{i,3b+1}, w_{i,3b+2}).
  - If q = 0, the leaf takes the site's local zero option.
  - Otherwise let s be the sign of q's first non-zero entry. The leaf is line pp_b(p) if s > 0 and pn_b(p) if s < 0, where p = s·q ∈ 𝒫_3.
  - This is exact for every W: y_i = Σ_b (s·p)·x_block = Σ_j w_ij x_j.
- **Timing:** latency 8 cycles from word start to the first output bit; throughput 14 cycles per word.

**Physical organization: the fixed base, W-blind (R3).**
- **Layers:** the base holds every cell plus all wiring on met1–met3. Programs use met4–met5 nets only, plus identical-footprint via-site master swaps (the local zero option).
- **Via site VSITE,** one per leaf: 4 sites wide. Its A pin (met4 pad, 1.24 × 1.12 µm) is programmable; its Z pin (li1) drives the leaf.
- **Line access:**
  - Every line has **K = 4 taps** (LTAP2: 2 sites wide, single-track met4 pad 0.62 × 1.12 µm).
  - The four taps sit on the same base net. The base routes the line as a **spine** on met2/met1 from its driver through its four taps.
  - Rows are split into four segments of 16. A leaf in segment s may connect only to its line's tap in segment s.
- **Placement** (FIRM before global placement):
  - 22 vertical **bands**, one per block, of equal width.
  - The band's 64 via sites sit in one column at the band centre, row i at height (i + 0.5)/64, with pads centred on met4 tracks.
  - Tap (line t of the band's T lines, segment s) sits at height (s + (t + 0.5)/T)/4, at the line's home x = (t + 0.5)/T of the band width, track-aligned.
  - Everything else is placed by the tool from base connectivity only.
- **Area:** 4 taps × 2 sites = 8 sites per line, identical to one 8-site tap. Base cell area is 169,952 µm², the same as R2.

## C. Mathematical results (with assumptions)

1. **Exactness (DERIVED).** Every non-zero ternary g-vector is ±p for exactly one p ∈ 𝒫_g, so the programming rule above computes W x exactly for every W ∈ {−1, 0, 1}^{m×n}.
2. **Port bound — Theorem 1 (proven in the previous session).**
   - *Model:* a DAG of two-input adders with fixed base connectivity. Port p has s_p options: pre-built candidate signals, one of which may be 0; a non-zero candidate may be taken with either polarity. A fabric is *universal* if some programming realizes y = W x for every ternary W.
   - *Claim:* a universal fabric with port fan-in ≤ s has P ≥ m n log₂3 / log₂(2s − 1) programmable ports, and A ≥ (P − m)/2 adders.
   - *UBP-g meets the port bound with equality* when g | n: P = m⌈n/g⌉ and 2s − 1 = 3^g.
3. **Reachability, not port count, sets the fixed-base cost (DERIVED; new in G2/R3).**
   - In a W-blind base, every port of block b must be able to reach each of its block's 2|𝒫_g| = 3^g − 1 lines. That is m⌈n/g⌉(3^g − 1) potential connections, against 2mn for a per-input fabric: a ratio of (3^g − 1)/(2g) = **4.33 at g = 3**.
   - Theorem 1's port minimum is bought with this reachability.
   - **Interval model.** The programmable met4 demand of a band is the maximum overlap of its (line, segment) nets' vertical spans.
   - **Calibration on R2 (single tap, K = 1):** peak / usable tracks is 0.96 at U45 (closed), 1.05 at U52 and 1.15 at U60 (neither closed).
   - **K = 4 segmentation** cuts the worst peak from 23 to 12 lines per band on development matrices. The price is base spine wiring of about (K − 1)/K of the band height per line.
   - This is a model, not a theorem. R3's outcome is its test.
4. **DA width lemma (DERIVED).**
   - A ternary K-input distributed-arithmetic leaf needs ⌈log₂(2K + 1)⌉ ≥ K bits for K ≤ 4, so it never reduces compressor input bits below the K = 1 popcount fabric.
   - Its ROM grows as 2^K (Gate 3).

## D. Physical evidence (MEASURED unless labelled)

{{PHYSICAL}}

## E. Strongest competitors

{{COMPETITORS}}

## F. Scope

- **Weights:** ternary {−1, 0, +1}. Binary ±1 is the special case with 2^(g−1) patterns per block.
- **Activations:** INT8, two's complement.
- **Bit-serial,** 14 cycles per 14-bit output word. The bit-parallel form is excluded; it lost a utilization step in E5.
- **Measured size:** one 64 × 64 layer, g = 3, K = 4.
- **Programmable-layer assumptions:**
  - Weights change only met4–met5 wiring (and via4) plus a local zero option. The zero option is modelled as an identical-footprint master swap standing for a via choice.
  - met1–met3, the cells and their placement are frozen. The line spines live in the base.
- **Technology:**
  - SKY130 HD: met4 0.92 µm pitch, met5 3.4 µm, 0.8 µm via4. Base PDN is met1 rails only (IR out of scope).
  - The via sites and taps are abstract cells (buffer-modelled via stacks).
- **Timing:**
  - Pre-registered: the base's routed timing plus placement-parasitic timing of the programmed netlist.
  - Rigor check: extracted base parasitics plus routed-geometry lumped RC for every programmable net.

## G. Remaining risks

{{RISKS}}

## H. Paper-scale plan (4–8 weeks)

{{PLAN}}

## I. Candidate paper thesis

{{THESIS}}

## J. Strongest reviewer attack

{{ATTACK}}
