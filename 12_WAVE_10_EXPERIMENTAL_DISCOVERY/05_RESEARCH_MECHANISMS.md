# 05 — Research mechanisms

## Stage reached

The Wave 10 prompt allows research mechanisms, with at least two competing approaches, **only after evidence** that a candidate survives its decisive experiment. **No candidate reached this stage.**
- C1 was killed by its pre-registered decisive experiment D1.
- C6's result is recorded in `04_EXPERIMENTAL_INVESTIGATION.md` §7 and `06_FINAL_DECISION.md`.

Nothing below proposes a research mechanism. Doing so would fabricate a stage that was not reached.

What this document does contain is the *explanatory* mechanism analysis performed for C1's demonstrated effect. The discovery order calls that step "isolate the cause". It is recorded here so that a future wave does not repeat it.

## C1: two competing explanations for the evolved mapper's area gain, and how D2 decided between them

**Observed effect (D1).** GPT-5 it29 reduces area by 8.1% against mockturtle `map` (EPFL-20 geomean 0.9186), at +4.4% delay.

### M-a: pure delay relaxation

The evolved code merely makes the mapper slower. The area gain would then equal what the baseline gets from its own `required_time` knob at the same delay.

- **Prediction:** A_evolved / A_initial@D_evolved ≈ 1.
- **Status:** partly true.
  - The relaxation factor is 0.9537 of the 0.9186 total (D1 §5.2).
  - Against ABC, relaxation is the *whole* effect: operator factor 0.9957.

### M-b: better covering at the same delay

The evolved selection rules produce covers that are genuinely smaller at equal delay.

- **Prediction:** A_evolved / A_initial@D_evolved < 1, carried by the area-round rules.
- **Status:** partly true, but *not* via the area-round rules.
  - The operator factor is 0.9632.
  - D2 shows it comes entirely from the **delay-round** acceptance rule. That rule accepts a faster match only if its area flow stays within 0.25·inv_area of the incumbent or it gains ≥ 0.5·inv_delay, and it drops a phase only if area flow does not grow.
  - Adding only that rule to the initial operators reproduces GPT-5 within 0.3% (area) and 0.1% (delay) on both suites.
  - Removing it from GPT-5 returns the initial mapper within 0.25%.
  - The area-round and exact-area edits are inert.

### Synthesis (INFERRED from D1 + D2)

Both explanations are partly true, and one delay-round rule drives both components:
1. It relaxes delay.
2. It changes the starting cover and the required-time profile from which cut-based area recovery proceeds. Area recovery is path-dependent, so the result is covers that the required-time knob alone does not reach.

This second effect is exactly what emap's area-oriented match alternatives target. emap remains better at iso-delay:
- EPFL-20: GPT-5/emap = 1.0238;
- IWLS05-22: 1.0624.

**Why this is not a research mechanism.** Area-aware tie-breaking inside a delay-oriented mapping pass is an established design axis: area-flow tie-breaks in priority-cut mapping, and emap's alternatives. The evolved rule is dominated at iso-delay by the library's own newer mapper. It does not pass the contribution test in `03_STRONGEST_PRIOR_ART.md`.

## What would be required to reach a mechanism stage in this line (not done; recorded as UNRESOLVED directions)

1. **Evolve from emap, with iso-delay or Pareto selection instead of the scalarized S_overall.** This needs LLM API calls, which the user's approval for this wave excluded. Whether it would beat emap is unknown; no claim is made.
2. **Transplant the evolved delay-round rule into emap and test at iso-delay.** This is feasible locally but is engineering, and emap already has area-oriented alternatives. It was not run.
