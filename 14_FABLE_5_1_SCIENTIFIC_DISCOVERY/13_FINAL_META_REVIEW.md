# 13 — Final meta-review (mandatory)

This is an independent review of the whole Wave-14 investigation, written after all decisive runs.

## 1. What did we learn about the underlying scientific problem?

- **Accumulation hardware in regime V has a real, physically robust inefficiency that cross-neuron sharing can remove.**
  - Compared with the per-input universal fabric, a W-independent fabric of shared block-pattern generators needs about half the **routed** area at equal clock and throughput in bit-serial form (2.13×, n = 64).
  - It needs 5–6× less via-programmed wiring.
- **The binding physical cost is select-bus width, not select fan-in.** Bit-parallel UBP loses one utilization step to congestion (E5). Bit-serial UBP does not (E6).
- **Pre-placement timing misleads in both directions:**
  - bit-parallel UBP's 1.43× logic-depth penalty shrank to 1.10× post-route, because g1's larger area adds wire delay;
  - bit-serial UBP met the real clock *faster* than g1.

## 2. What did the original hypotheses get wrong?

- **H1.1's assumed risk was right in kind but not in magnitude.** Wiring is the limiter for bit-parallel UBP, but it costs one utilization step (2.08× → 1.67×), not the whole advantage.
- **The evolution's stated trigger was a pre-placement artifact.** The 1.43× delay penalty that motivated H1.2 largely vanished after routing (1.10×).
  - H1.2 was nevertheless justified by a different effect that E5 then revealed: congestion.
- **The prior session's E3** understated g1's tree width by one bit (01). Its "iso-delay" rested on ABC's load-independent model. Both were corrected here by physical measurement.
- **Our first E5/E6 netlists were not truly universal.** Default tool pruning removed unused generator and negator logic (A2). Unchecked, this would have overstated the UBP4 advantage by up to 27%.

## 3. What did experimentation reveal that literature alone did not?

1. **The cost moves from the mux to the wire, and bit width decides whether the wire fits.**
   - Bit-parallel UBP: 10-bit buses congest at U = 75.
   - Bit-serial UBP: single wires route like the baseline.
2. **Select wiring *drops* with UBP by ≈ g/(1 − p0)** (5.8× measured), because rows have n/g leaves. The literature's LUT designs never face this, since their index is a runtime mux.
3. **Tool defaults (`opt_clean -purge`, `eliminate_dead_logic`) silently convert a universal fabric into a W-specific one.** Any regime-V study must check a W-independence invariant.

## 4. Which mechanisms failed and why?

- **H1.1 (bit-parallel UBP): partially weakened, not falsified.**
  - It passed A5 at the pre-registered basis (1.67× ≥ 1.5).
  - It is routability-limited: it fails global routing at U = 75.
  - It is 10% slower post-route.
- **H3.1 (hash-friendly pairing, regime F): killed.** It is Paar/da4ml CSE (prior art).
- **H2.1 (adapter-as-redundancy): not testable here.** It stays in reserve.
- **The (F) claim from the previous session:** stays withdrawn (hashing).

## 5. Did different mechanisms fail because of a shared constraint?

- **Yes, partly.** Everything that "fails" in regime-V accumulation fails through **wiring per programmable site**:
  - int4 is wire-bound (HIST-INT);
  - g = 4 is wire-sensitive (previous model);
  - bit-parallel g = 3 loses a utilization step here.
- **The shared constraint:** the bits × candidate lines that must reach each site.
- Bit-serialization is the one change that attacks that product directly, by dividing it by w.

## 6. Did hypothesis evolution produce a genuinely different mechanism?

- **Different cost structure, same principle.**
  - H1.2 changes the arithmetic (serial registered adders), the interconnect (1-wire lines), and the timing model (latency instead of delay).
  - Its measured behaviour differs in the decisive way: it routes at U = 75.
- **But it is the same sharing principle realized in another arithmetic style**, not a new idea. It is a substantive revision, not a new mechanism.

## 7. What did the evaluator teach us?

1. **Physical PnR can separate claims that cell-level and adder-level models cannot.** It revealed the congestion step, and that delay is erased by wire.
2. **An evaluator must check invariants that functional validation cannot see.** A2 was found only by cross-checking two area reports. Every functional check passed on the pruned netlists.
3. **Direct decomposition of routed wire beats inference from totals.** The select-wiring parser turned "total WL is lower" into the specific, testable law "select WL ≈ 1/g × (1 − p0)⁻¹".

## 8. Which prior-art objections were decisive?

- **None was decisive against the complete contribution.**
- **Decisive against sub-claims:**
  - the block-precompute arithmetic, including mirror-half + sign index, is **occupied** by runtime LUT accelerators (TENET, T-MAC, LUT Tensor Core);
  - the (F) weight-specific variant is **occupied** by CSE / da4ml.

## 9. Which objections concerned only known ingredients rather than the complete contribution?

- The LUT arithmetic (TENET/T-MAC).
- Via-programmable fabrics (HNLPU/Taalas/Ankhdjet).
- Bit-serial neurons (HNLPU).

Each is an ingredient. **The combination is not found in any retrieved source**, but its **obviousness is high**. A patent examiner would likely combine TENET with HNLPU. The defensible part is scientific: the physical cost structure and the bit-serial requirement.

## 10. Did we actually invent something technically distinct?

**Modestly.**
- **The previous session** proposed the regime-V block-sharing fabric and proved its port optimality.
- **This session:**
  - evolved it into a bit-serial form that shares pattern *streams* across serial neurons (not found in HNLPU's summaries, provisional);
  - showed physically that this form, unlike the bit-parallel one, keeps a 2× routed-area advantage without a routability penalty.
- **The distinct element is an architectural combination with a measured physical justification**, not a new algorithmic principle.

## 11. Or did we merely perform another sophisticated research audit?

- **More than an audit.** We built and validated an evaluator around *our* mechanism, not someone else's paper. We tested it with pre-registered kill conditions that could have fired, and revised it once for a physically observed reason.
- **But:** a large share of the session went into evaluator correctness. That includes two protocol amendments and one self-inflicted defect (A2) found and fixed. And the novelty question is still gated on sources we could not read.

## 12. What result would still kill the surviving thesis?

1. **Novelty:** HNLPU's full text, or a Taalas disclosure, showing shared multi-input pattern streams.
2. **Fixed placement:** with placement fixed and W-dependent routing confined to the top layers, bit-serial UBP fails to route, or falls below 1.5× where g1 routes.
3. **A stronger baseline:** a transistor-level DA-via-ROM, or HNLPU-style custom neurons, is ≥ 2× smaller than g1 per weight at an advanced node.
4. **Scale or trained weights:** at n ≥ 256 with real BitNet weights, the ratio falls below 1.5×. Theory predicts the opposite, toward g.

## 13. Why is further work scientifically justified — or not?

**Justified, with gates:**
- **Consequential problem:** the dominant area term of hardwired LLM silicon.
- **Precise, exact mechanism:** W-independent, port-optimal.
- **Causal account confirmed physically:** fewer leaves lead to fewer programmable wires; bit-serial removes bus congestion.
- **Trustworthy evaluator:** post-route functional validation, W-independence invariant, parser cross-check.
- **Cheap, sharp falsifiers exist:** the fixed-placement ECO test, DA-ROM, the full-text check.

**Not justified:** heavy investment before the three week-1 gates (22 in 12). Each can end the project quickly and cheaply.
