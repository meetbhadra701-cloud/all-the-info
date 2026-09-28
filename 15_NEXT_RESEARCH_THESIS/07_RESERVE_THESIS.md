# 07 — Reserve thesis: **none selected**

No second candidate survived either.
- MR-SIGNOFF was killed by its own pre-registered test.
- XABFT was killed with XACC.
- LIN-CEC was killed as occupied.

The second-best item is recorded below because it carries **measured value**. It is classified **ENGINEERING**, not research, and it is stated in the same eight-element form so the classification can be checked.

---

## Second-best item: LIN-CEC — linear-algebraic matching of XOR-dominated cones in open CEC (ENGINEERING)

> **(X)** The open flow's combinational equivalence checkers, ABC `cec` and `&cec` (CDCL-based SAT sweeping),
> **(Y)** time out on equivalent XOR-dominated circuits whose two sides factor the XOR trees differently. With no internal equivalences to sweep, the miter is a parity problem, exponential for resolution.
> **(Z)** The regime: parallel CRC / ECC encoders and linear layers. **Measured:** CRC-32 over 64, 256 and 1,024 data bits, flat matrix vs LFSR-unrolled; every check exceeds a 70 s hard cap. ABC's classic `cec` also ignored its own `-T 60` limit and hung for more than 400 s.
> **(M)** Detect GF(2)-affine cones and compare their matrices from n+1 simulations (zero and unit vectors) by Gaussian elimination. Sweep the remainder with SAT.
> **(P)** An affine map over GF(2) is determined by its values on the zero vector and a basis; the comparison is polynomial.
> **(Q)** The strongest prior approach: Gaussian elimination inside XOR-dense regions of circuit equivalence checking (published), BDD-based CEC (parity has linear-size BDDs), and Gauss–Jordan SAT (CryptoMiniSat).
> **(R)** **There is no technical distinction from Q.** This is Q integrated into ABC / Yosys.
> **(E, K)** The CRC screen of 04 has already run. The linear check proves every pair in **0.02–0.23 s**, and random simulation (4,096 vectors) agrees.

**Classification: ENGINEERING.**
- The open tool's gap is real and categorical (≥ 300–3,000×) on circuits present in most SoCs.
- The method is published, so integrating it is a tool contribution, not a thesis. Kill-database pattern: "known principle + new implementation".
- It would also need the affinity test itself to be sound: structural XOR extraction, not simulation alone. The screen did not implement that part.

**What would change this classification.** A class of XOR-dominated designs that *the published methods also fail on*, for example linear logic mixed with non-linear masking or carries. None was found or tested here.
