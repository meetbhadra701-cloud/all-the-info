# 06 — Stage C (reflection) and Stage D (comparative debate)

## Stage C — reflection on each serious hypothesis

| | H1.1 bit-parallel UBP | H1.2 bit-serial UBP | H2.1 adapter-as-redundancy |
|---|---|---|---|
| **Coherence** | Exact by construction; checked at three levels (HIST-OBS) | Coherent. Serial two's-complement streams: LSB-first addition, free sign extension, negation via complemented stream + carry-in (standard bit-serial arithmetic) | Coherent: the row replacement is exact |
| **Importance** | High (regime V is how hardwired silicon is built) | High, and closer to the frontier's arithmetic (HNLPU) | High (yield of 815+ mm² dies) |
| **Math assumptions** | Adder counts exact; cell areas measured | Per-site cost width-independent; cycle count set by output width | Defects within adapter rank; accuracy unaffected by the replacement |
| **Executability here** | Yes (ORFS container now available) | Yes (gate level); PnR is the same flow | No (no checkpoints; no defect statistics) |
| **Likely failure mode** | **Select wiring**: (3^g − 1)/2 × w-bit buses per site | Serial generator latency; popcount overhead; a hidden cycle penalty | Accuracy degradation; adapter rank already used by fine-tuning |
| **Generalizability** | Ternary/binary only (int4 wire-bound, HIST-INT) | The same alphabets; favours larger g | Any hardwired chip |
| **Novelty** | Provisional (HNLPU unread); LUT-GEMM is only an ingredient | Provisional. If HNLPU shares popcount inputs across neurons, it is occupied | Adjacent prior art (DNN fault tolerance; RRAM LoRA) |
| **Falsifiability** | Clear (PnR area at iso-clock) | Clear (iso-throughput gate level, then PnR) | Clear in principle; not locally executable |

**What failure would mean.**
- If the PnR wiring kills H1.1, that is a MECHANISM failure of the bit-parallel realization. P1 survives if H1.2 removes the cause (w-bit buses).
- If wiring kills both H1.1 and H1.2, the cause is shared: select fan-in (3^g − 1)/2 is too large at any bit width. **Then P1's mechanism class is dead at g ≥ 3.** Only g = 2 (2 lines/input; about 1.55×) would remain, which is weak.

## Stage D — comparative debate (sequential roles)

**Problem Investigator.** P1 is real.
- Metal-only programmability is the stated NRE strategy of every hardwired-LLM effort found (HNLPU: 60 of 70 masks shared; Taalas: 2 layers; Ankhdjet: via mask).
- Per-site accumulation is the only term that scales with the weight count in spatial fabrics.
- P2 is also real but is not locally executable.

**Mechanism Inventor.**
- H1.2 is the stronger *long-run* mechanism. It removes both costs that cap H1.1: bus width in the wiring, and leaf width in the logic. It also slots directly into the frontier's neuron (HNLPU POPCNT), which makes the comparison sharp.
- But H1.2's advantage over H1.1 rests on the same unverified wiring model.

**Prior-Art Prosecutor.**
- The closest work is HNLPU. Its retrieved description groups *within* a neuron.
- If its full text shows popcount inputs shared across neurons (a "shared pre-summed stream" per input block), both H1.1 and H1.2 are occupied.
- That cannot be settled here. The complete-contribution delta stands provisionally.

**Experimental Designer.**
- The one untested assumption common to both mechanisms is **physical select wiring**. The previous session's model predicts g = 3 fits and g = 4 is marginal (bit-parallel).
- A place-and-route experiment on weight-independent, hierarchy-preserved fabrics (E5):
  - **directly tests H1.1**;
  - **calibrates the wire model** that H1.2's prediction depends on.
- It is decisive in both directions:
  - if bit-parallel UBP3 loses its advantage after routing, evolve to H1.2 (its reason to exist);
  - if it keeps it, the thesis is physically supported at the tested scale.

**Scientific Reviewer.**
- E5 success would establish that cross-neuron block sharing keeps a ≥ 1.5× routed-area advantage at iso-clock on SKY130 for 64×64 layers, under placement freedom.
- It would **not** establish:
  - behaviour of a structured via-ROM array (fixed straps);
  - larger layers;
  - advanced nodes;
  - novelty.

**Decision.**
- **Primary:** P1 (H1.1, then evolution H1.2 if justified). The first decisive experiment is E5.
- **Reserve:** P2 (documented, not executable here).
