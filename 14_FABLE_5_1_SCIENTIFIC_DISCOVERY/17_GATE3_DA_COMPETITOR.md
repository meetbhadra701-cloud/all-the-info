# 17 — Gate 3: strongest architectural competitors (via-ROM DA, and the frontier's own popcount fabric)

**Labels:**
- **MEASURED:** our flow (Yosys/ABC, OpenSTA, ORFS on SKY130 HD, image 69df744e2b5c).
- **INFERRED:** taken from Ankhdjet's shipped silicon calibration, not re-verified.
- **MODELED:** our periphery assumptions.
- **DERIVED:** exact counts from the formulas.
- **UNVERIFIED:** anything else.

## 1. Formalizing the strongest via-ROM distributed arithmetic (DA) for ternary MVM

**Operation:** y = W x with W ∈ {−1, 0, 1}^{m×n} and x INT8 two's complement, x = Σ_t s_t 2^t b_t (s_7 = −1). Per output row i:

  y_i = Σ_t s_t 2^t Σ_b T_ib(u_bt),  with T_ib(u) = Σ_{j∈b} w_ij u_j ∈ [−K, K]

where u_bt ∈ {0,1}^K are the K current bits of block b.

| Item | DA(K), bit-plane, spatial |
|---|---|
| Precomputed | For every row and every K-input block, the table T_ib(u) for all 2^K bit patterns u. Offset-coded T + K ∈ [0, 2K], b_K = ⌈log₂(2K+1)⌉ bits. OBC halves the table (2^(K−1) entries) at the cost of a conditional negation. |
| Where stored | A via-ROM per (row, block). Word lines = one-hot decode of the K current bits, **shared by all rows**. Each row owns b_K bitlines per block, each with precharge + sense. |
| What changes per model | Only the vias in the ROM arrays and the per-row correction-constant vias. The base (cells, decoders, sense, adders) is W-independent. |
| ROM size | DERIVED: m·⌈n/K⌉·2^K·b_K cells. For n = m = 64: K=2: 24,576; K=3: 33,792; K=4: 65,536 (OBC 32,768); K=6 OBC: 90,112. |
| Programmable connections | One via decision per ROM cell. About half the cells carry a via, i.e. Θ(2^K·b_K/K) vias per weight. |
| Adders per row | A compressor over ⌈n/K⌉ leaves of b_K bits (**the same bit count as n one-bit slots for K ≤ 4**), plus a 14-bit shift-accumulator |
| Word width | Leaves b_K bits; accumulator 14 bits |
| Latency / throughput | 8 cycles per word (one per input bit-plane), plus pipeline |
| Routing | Shared word lines (2^K per block across all rows). No long per-weight programmable wires: the vias are local to the ROM arrays. |
| Lower-layer reuse | Full. It is a ROM; only via masks change. |

**Degenerate case K = 1.** The "table" is the sign selection itself. In a via fabric that needs no ROM: a via connects the input bit or its complement to the leaf, and a per-row constant corrects the complement lanes. **That is exactly design P.** It is the spatial form of the bit-plane popcount arithmetic that HNLPU (POPCNT), BitROM and Ankhdjet use.

## 2. The DA model (per row; MEASURED datapath, INFERRED ROM, MODELED periphery)

- **Source:** `experiments/results/G3/da_model/da_model.json`, from `scripts/g3_da_model.py`.
- **Datapath:** the per-row compressor, accumulator and output stage are **synthesized in our flow** for each K.
- **ROM:** Ankhdjet's silicon-verified SKY130 cell, 2.21 µm² as built or 0.65 µm² raw, plus 20% array overhead.
- **Sense:** 5 µm² custom (MODELED), or a 15 µm² standard-cell latch.

| K | OBC | Compressor input bits | ROM cells / row | Datapath µm² (MEAS) | ROM µm² (INF, as built / raw) | Row total µm² (range) |
|---|---|---|---|---|---|---|
| 1 (= P) | — | 64 × 1 | 0 | **3,346** (P as built) | 0 | **3,346** |
| 2 | no | 32 × 3 = 96 | 384 | 4,696 | 1,018 / 300 | 5,499 – 7,180 |
| 3 | no | 22 × 3 = 66 | 528 | 3,486 | 1,400 / 412 | **4,261** – 5,910 |
| 4 | yes | 16 × 4 = 64 | 512 | 3,309 | 1,358 / 399 | 4,613 – 6,213 |
| 5 | yes | 13 × 4 = 52 | 832 | 2,879 | 2,206 / 649 | 4,282 – 6,361 |
| 6 | yes | 11 × 4 = 44 | 1,408 | 2,581 | 3,734 / 1,098 | 4,351 – 7,427 |
| 8 | yes | 8 × 5 = 40 | 5,120 | 2,275 | 13,578 / 3,994 | 7,011 – 16,996 |

**Result (DERIVED + MEASURED + INFERRED):** **no DA(K ≥ 2) row is smaller than P's row**, even with the optimistic raw ROM cell. The mechanism:
1. For ternary weights, the via fabric already gets each input's multiplication (a sign) for free.
2. A K-input table leaf needs b_K = ⌈log₂(2K+1)⌉ ≥ K bits for K ≤ 4, so the compressor does not shrink.
3. For K ≥ 5 the compressor shrinks slowly, while the ROM grows as 2^K.

DA would beat P only if ROM cells cost below ≈ 0.06 µm² in SKY130 (K = 6, OBC), about 10× below Ankhdjet's raw cell. The cell-to-logic area ratio is roughly node-independent, so this conclusion is INFERRED to hold at advanced nodes.

**A time-multiplexed via-ROM** (Ankhdjet's actual design: one input row per cycle, g = 1) sits at a different operating point:
- **Area:** far denser: 2.21 µm²/weight as built, vs UBP3-serial's ≈ 51 µm²/weight.
- **Speed:** T ≈ K × SUBCOL_ROWS = 512 cycles per dot product (64-row sub-columns). Its A×T per weight is therefore **≈ 10–40× worse** than any spatial fabric here (DERIVED from its RTL cycle count and cell data).
- It dominates when throughput is not the constraint. It is not a competitor at equal throughput.

## 3. The decisive MEASURED comparison: UBP3-serial (B) vs the frontier-style popcount fabrics (P, P2)

**Setup** (all MEASURED):
- Same flow as E6: SKY130 HD, ORFS image 69df744e2b5c, NO_DCE (every instance kept), 64×64 ternary W (seed 14, p0 = 0.4), INT8 in, 14-bit out.
- **Weights are hardwired**, and placement sees W. This is the E6 regime for every design in this table.
- Routed area = synthesized cell area / U_max, where U_max is the highest U with DRC-clean detailed routing.
- The period is each design's achieved minimum, 3.0 ns − setup WS; P ran at a 5.0 ns target (D-G3.1).
- Every row is validated post-PnR: the final routed netlist, simulated by our cycle-accurate simulator, matches numpy W@x, and the mutation control is detected.

| Design | Synth cell area µm² | U_max % | Routed area µm² | Cycles/word | Min period ns | **A×T µm²·ns** | vs B |
|---|---|---|---|---|---|---|---|
| **B** UBP3-serial (E6) | 156,941 | 75 | 209,255 | 14 | 2.082 | **6.10e6** | 1 |
| A g1-serial (E6) | 334,184 | 75 | 445,579 | 14 | 2.219 | 13.84e6 | 2.27× |
| P popcount (D-G3.1, 5 ns target) | 216,071 | 60 | 360,118 | 8 | 5.290 | 15.24e6 | 2.50× |
| **P2** pipelined popcount | 250,124 | 60 | 416,873 | 8 | 3.368 | **11.23e6** | **1.84×** |
| D(K), K ≥ 2 (via-ROM DA) | — | — | row area ≥ 1.27× P's (§2) | 8 | ≈ P-class | ≥ P-class (DERIVED) | ≥ 1.84× |

**Why P and P2 lose U_max:**
- **P at U75 (3.0 ns):** timing repair inflated it to 97% utilization, and detailed placement then failed. At 5 ns and U75 detailed placement failed again. It routes clean at U60.
- **P2 at U75:** global routing failed with congestion (GRT-0232). At U60 it routes clean after 7 detailed-route iterations.
- **B** routes at U75.

The popcount trees over 64 one-bit leaves per row are wiring-heavy. The frontier arithmetic spends fewer cycles (8 vs 14) but pays in area and wiring.

## 4. Gate-3 verdict

| ID | Condition | Result |
|---|---|---|
| K3a | A×T(P or P2) ≤ A×T(B) | **Not triggered.** The best per-input competitor, P2 at 11.23e6, is 1.84× worse than B. |
| K3b | Conservative D(K) ≤ B | **Not triggered.** No D(K ≥ 2) row is smaller than P's row even with the optimistic ROM cell (§2), so D is at least P-class. |
| S3 | A×T(B) ≤ 0.83 × min(competitors) | **Holds:** 6.10e6 ≤ 9.32e6. |

**B survives Gate 3, in the regime where it was measured: weights hardwired, W-aware layout.**
- **Via-ROM DA** is not a competitor for ternary weights at equal throughput:
  - A spatial DA table leaf needs b_K ≥ K bits for K ≤ 4, so it saves no compressor bits over the K = 1 popcount fabric.
  - A time-multiplexed via-ROM (Ankhdjet) is ≈ 10–40× worse in A×T; it is a different, area-first operating point.
- **R1/Q not triggered:** the bounded revision R1 (UBP on top of the bit-plane fabric) was conditional on K3a, which did not fire.

**What G3 does NOT establish:** that B's advantage survives when the layout may not see W. That is Gate 2's question (16_GATE2_FIXED_BASE.md). Every G3 number is a hardwired-weight number.
