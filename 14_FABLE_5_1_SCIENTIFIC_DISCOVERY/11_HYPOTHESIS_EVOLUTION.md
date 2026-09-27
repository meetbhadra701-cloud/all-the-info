# 11 — Hypothesis evolution (bounded loop: 1 of at most 2 iterations used)

```
PROPOSE H1.1 (bit-parallel UBP, inherited) → BUILD EVALUATOR (ORFS PnR + own simulators)
→ TEST MINIMAL INSTANCE (8×8 smoke, n = 32) → DIAGNOSE (delay penalty, see below)
→ REVISE: H1.2 bit-serial → TEST REVISION (E6, n = 64, PnR) → DECIDE (10, 14)
```

## Iteration 1: H1.1 (bit-parallel) → H1.2 (bit-serial)

**What failed.**
- Not the pre-registered area test: E5 was still running when the revision was registered.
- What failed was a **property H1.1 needs in order to be useful: iso-delay.**
- On SKY130 with OpenSTA, the bit-parallel UBP datapath puts the generator's chained carry-propagate adders and the line negators **in series with the row tree**:
  - logic path UBP3 9.37 ns vs g1 6.57 ns at n = 32 (1.43×), pre-placement;
  - post-route natural delay: see 10.
- The previous session's E3 hid this. It used ABC's load-independent delay model and budgeted trees against it (01, lesson 2).

**What was learned.**
- In bit-parallel form, UBP buys area by adding a **serial pre-adder stage**. At iso-delay, the trees must absorb the generator's delay, which erodes the area gain.
- Pipelining the generator would restore the clock but add registers on (3^g − 1)/2 × w-bit lines per block.
- The H1.1 area advantage is therefore real only for **latency-tolerant** designs. Those are exactly the designs a throughput-oriented hardwired LLM chip is made of.

**What changes technically (H1.2).**
- Every arithmetic element becomes a **bit-serial** adder: one full adder, with sum and carry registered. This covers the generator steps, the negators and the tree nodes.
- Pattern lines become **single wires**, so select wiring falls w× (10× at g = 3, 4).
- The generator's depth turns into **latency cycles**, not clock period.
- Throughput is identical by construction: T = ow cycles per word for both fabrics, because LSB-first serial accumulation is set by the *output* width.
- This is HNLPU's arithmetic style (bit-serial neurons), so the comparison sits at the frontier's own operating point.

**Why the revision addresses the failure.**
- The clock period of both fabrics is one serial-adder stage. The UBP penalty becomes **+1 cycle of latency** (measured: 8 vs 7 cycles at n = 64), which throughput designs tolerate.
- Width-independent leaves and single-wire lines also remove H1.1's second risk: w-bit select buses.

**What result distinguishes the revision** (pre-registered, 09 §E6):
- **A6:** routed-area ratio ≥ 1.5 at a real 3.0 ns clock, with setup and hold met and equal throughput.
- **K6:** ratio < 1.3, or UBP not DRC-clean with timing met where g1 is.

## Result of iteration 1 (10 §2–3)

- **H1.2 PASSED (A6).** g1/UBP3 routed area = **2.13×**.
  - Both designs are DRC-clean at U = 75, the top of the range.
  - Both meet setup and hold at the real 3.0 ns clock; UBP3's minimum period is shorter (2.08 vs 2.22 ns).
  - Latency is +1 cycle; throughput is equal.
  - Select wiring is 5.8× lower.
- **What E5 revealed about H1.1 changes the story behind the revision.**
  - The *pre-placement* delay penalty that triggered the revision shrank to 1.10× post-route.
  - A different bit-parallel cost appeared instead: **select-bus congestion.** Bit-parallel UBP fails global routing at U = 75, where g1 routes. That drops its ratio from 2.08× (equal U) to «E5_RATIO».
  - H1.2 removes exactly this cost: single-wire lines route at U = 75 like g1.
  - So the revision was justified, but by the *second* risk it named (w-bit select buses), not by the delay trigger.
- **Distinguishing result, as pre-registered:** A6 met at the real clock with equal throughput. The bit-serial form routes where the bit-parallel form congests.

## Iteration 2: not used (deliberately)

1. **The revised mechanism passed.** A second revision would be optimization, not a response to failure.
2. **The remaining risks are evaluator scope, not mechanism failures:**
   - fixed placement / upper-metal-only routing;
   - the DA-via-ROM baseline;
   - novelty.

   Each is better addressed as a gate (14) than as another mechanism change.
3. **Budget:** preserving about $20 for recovery or follow-up, as instructed.
