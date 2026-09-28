# Research rules for the next thesis

These rules were derived from the UBP closeout. The evidence behind each one is in `14_FABLE_5_1_SCIENTIFIC_DISCOVERY/24_LESSONS_FOR_NEXT_THESIS.md`; the tools that enforce them are in `SUPPORTING_ARTIFACTS/research_harness/`.

1. **Important problem first.** State who has the problem, what it costs today, and why it is not solved. The mechanism comes after.
2. **Concrete mechanism hypothesis second.** One mechanism M, with the causal reason it should work, precise enough to implement and to be refuted.
3. **Strongest baseline immediately.** Name the best existing approach B (published, default-tool, or frontier) before the first candidate number. Run B through the same evaluator, and give it every treatment the candidate gets.
4. **Cheap falsifier immediately.** An experiment of hours, not weeks, whose failure would kill M. Run it before building anything that depends on M.
5. **Whole-system evaluator immediately.** Real cells, the flow's own sizing, extracted parasitics, the slow corner, the target operating point. Report what limits the figure of merit for the candidate and for B. Idealized models only bound the candidate.
6. **Prior art in two stages.** A frontier scan before choosing the mechanism. Exact novelty prosecution once the mechanism is precise, classifying it as known ingredient, equivalent mechanism, obvious composition, or distinct contribution.
7. **At most two substantive mechanism revisions.** After that, a new mechanism, or a new problem, starting again at rule 1.
8. **Pre-register decisive tests.** Commit the metric, threshold, competitors, corners, operating point, fallbacks and validity conditions before any result (`harness.prereg.audit`). Pre-register tool effort at the tool's default.
9. **Never convert implementation defects into scientific wins.** A result that depends on a bug, an idealization, a missing cost or a tool shortcut is not a result. Fix, re-measure, and apply the fix to B too.
10. **Preserve negative results.** Kills, failed points and withdrawn claims stay in the record with their evidence. Superseded documents get a notice, not a rewrite.
11. **Prefer structural headroom.** Require the idealized advantage to exceed the threshold by more than the overhead factor measured on the first full-cost pilot. A knife-edge thesis is not ready.
12. **Close failed theses cleanly.** A pre-registered kill is final. Write the closeout, extract the reusable assets, record the lessons, and move on. No rescue, no "v2".
