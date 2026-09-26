# Weekly Continue / Revise / Stop Gates

These are project decision thresholds, not immigration rules or promises. A week is a milestone, not an automatic seven-day timer. Work can progress faster when evidence is ready. No agent may cross into the next week's implementation until both agents record PASS for the previous gate. REVISE permits bounded repairs within the current week. Either agent's STOP halts new implementation and experiments; preserve evidence and report to the user. Documentation of the stopping reason remains allowed.

Record each vote with `scripts/control.py gate`; votes must link to a real memo. The helper verifies task ownership and dependencies, not scientific truth. Agents remain responsible for checking the evidence. Initial status is PENDING everywhere. Never replace an unknown with a pass to keep the calendar moving.

## Week 1 — Prior art and three reproducible pairs

**User checkpoint:** Check the narrow reducer question against existing hardware reduction tools and create three reproducible equivalent RTL pairs with area regressions.

Codex must provide a pinned working toolchain, explicit support contract, real equivalence logs and three uncached area repetitions for each of three pairs. Claude must provide a focused comparison of closest reducers, provenance and a two-sentence proposed technical difference.

PASS only if all three pairs meet the frozen area predicate and meaningful-output guard; both agents can run the same configuration; at least five closest relevant antecedents have been compared at mechanism level (or the search memo clearly documents why fewer are available); and no reviewed source already provides the same coupled predicate-preserving reducer without a surviving distinct mechanism. Public search supports a bounded judgment, never “no one has done this.”

REVISE if the backend erases candidate differences, syntax support is inconsistent, or a near-match needs a focused full-text/code check. Permit one explicitly bounded repair cycle, normally up to two working days, recorded before starting. Do not repeatedly widen the search or weaken synthesis.

STOP if the exact proposed contribution is already implemented without a defensible improvement, reproducible pairs cannot be found after that bounded cycle, or the predicate depends on invalid semantics or unavailable rights/data. If novelty is unresolved, keep PENDING/REVISE; do not award PASS.

## Week 2 — Trustworthy predicate and simple baseline

**User checkpoint:** Build the compile → equivalence → area predicate and a basic delta-debugging baseline.

PASS requires: all Week 1 pairs replay; a known equivalent example passes; an intentionally inequivalent control is rejected; timeouts/malformed outputs/unsupported RTL cannot be accepted; cache identity tests pass; and edit-only reduction emits at least one smaller, fresh-verified, replayable witness on the development corpus. Independent-side baseline or the agreed scaffolding for it must be ready before coupled comparison.

Claude checks adversarial cases against Codex's implementation without duplicating its oracle. Codex documents exact CLI behavior and a clean-directory export. If the reducer finds no size reduction, separate “no removable structure” from implementation failure; acquire a qualifying larger example without hiding earlier results.

REVISE once for a bounded, diagnosed implementation defect. STOP if trustworthy equivalence/measurement cannot be established or the oracle is so brittle that final results cannot be replayed. A fabricated/mocked EDA result is an immediate evidence failure.

## Week 3 — Coupled method versus baseline

**User checkpoint:** Implement coordinated structural reduction and compare it against that baseline.

PASS requires equal-budget runs on at least three development pairs, final uncached validation of every claimed success, and a concrete signal: coupled reduction yields at least 20% fewer final pair AST nodes than the best valid non-coupled baseline (edit-only, independent-side, or Yosys `bugpoint`+external-predicate) on at least two cases, without a lower valid-export count. Use original size for no-gain cases and count invalid final outputs as failures. Log coupled/independent/edit-only/`bugpoint` and no-matching ablation results.

The 20% threshold is a predeclared project heuristic. If it is missed but one distinct mechanism shows a credible benefit, mark REVISE and state a single testable modification. Permit one bounded iteration of at most two working days. STOP the centerpiece research claim if the best non-coupled baseline, including `bugpoint`+external-predicate, remains as effective after that iteration, or benefits come from unmatched budgets, weakened constraints or size-counting artifacts.

## Week 4 — Ten pairs, replay and maintainer relevance

**User checkpoint:** Test ten pairs, package replayable outputs, and assess whether the results would help a synthesis maintainer.

Freeze ten qualifying pairs across at least three structural families, with seven development and three held-out cases declared before final tuning. Seek at least three pairs with public-design/historical provenance; if unavailable, mark practical relevance unresolved. Run the complete method matrix, retain all failures and compare final candidates in a clean environment.

Technical PASS requires ten of ten exported final witnesses reproduce the qualifying equivalence/area condition (an unchanged original can be exported but counts as no reduction), coupled achieves at least 70% original pair AST reduction on at least seven cases, and at least 20% median final-size advantage over the better simple baseline across the ten cases. At least two held-out cases must show a coupled size advantage. Both runtime and evaluation-call costs must be reported. These are feasibility screens, not claims of broad statistical significance.

Practical PASS requires a maintainer-ready report with a small example, single replay command, tool/version/library provenance, expected/observed outputs, reduction trace, license clarity, and a specific reason the reduced pair would aid diagnosis. Claude scores this checklist using public issue-report conventions and records whether any actual external review occurred. Internal assessment is not external validation. No unsolicited outreach.

Final outcomes:

- **CONTINUE proposal:** both votes PASS; a defensible mechanism, measurable advantage and credible user need survive. Prepare a month-two proposal; await user direction before starting it.
- **REVISE:** technical results are promising but originality, real-world provenance or user usefulness remains unresolved. Recommend one short next experiment with a fixed budget; do not claim the month passed.
- **STOP / PIVOT:** novelty is defeated, the simple reducer is sufficient, results are irreproducible, or no useful user workflow can be demonstrated. Preserve the tool and findings; do not manufacture a portfolio narrative.

**User's decision rule:** Build the one-month feasibility prototype. Continue only if the coupled algorithm offers a real advantage and the focused prior-art check leaves a defensible contribution. Avoid committing a year to an unverified originality claim.
