# 05 — Exact prior-art prosecution of the evolved hypothesis H1.6

**Discipline.**
- No novelty is claimed from the absence of search results.
- Every item below was retrieved in this wave. Titles, authors and passages quoted from retrieved text are **PAPER**. Anything only seen in a search-engine summary is marked **UNVERIFIED**.
- Two PDFs (satlut ASP-DAC'18; Costamagna et al. ASP-DAC'25) were text-extracted locally with `experiments/scripts/pdftext.py` (standard-library zlib), because no PDF renderer is installed.

## H1.6 stated precisely

Cut-based standard-cell mappers (emap, `&nf`, `map`) commit near-tie match decisions locally. Take the covering problem over the mapper's *own* cut-match space, at a fixed delay bound D, with each (node, phase) restricted to candidates whose area-flow cost is within a factor (1 + ε) of that node's best, plus the heuristic's own choice. H1.6 claims this restricted problem:
- (A1) contains a cover materially smaller than the heuristic's;
- (A2) keeps most of the full-space exact optimum's advantage;
- (A3) is a small fraction of the full problem.

It is therefore solvable exactly at whole-circuit scale.

## Closest prior art, claim by claim

### 1. Schmitt, Mishchenko, Brayton — *SAT-Based Area Recovery in Structural Technology Mapping* (ASP-DAC 2018; IWLS 2017 version). ABC `&satlut`.

- **Claim (PAPER):**
  - windows over a mapped network;
  - CNF over *all structural K-LUT covers* of the window;
  - delay handled by "interfacing the SAT solver with a timer";
  - "additional average area reduction of 3-4%", ">10%" on some circuits, after a high-effort area flow;
  - diagnosis: heuristics err "due to the lack of clear winner".
- **Implementation:** ABC `&satlut`, for K-LUTs.
- **Evaluation:** 6-LUT, unit area, LUT-level delay.
- **Future work (PAPER):** "Extending SAT-based mapping to work for standard cells. A preliminary implementation confirmed that the approach is practical and leads to area savings."
- **Relation to H1.6:**
  - Both use exact structural re-covering.
  - satlut decomposes by **topology** and keeps the **full** candidate space inside a window.
  - H1.6 decomposes by **ambiguity** and restricts the candidate space **globally**.
  - satlut's diagnosis is H1.6's premise.
- **Unresolved by it:** the standard-cell setting (phases, inverters, pin delays), and whether errors concentrate in near-tie decisions, which is asserted by satlut but not measured in the retrieved text.

### 2. ABC `&nf -a` — "toggles SAT-based area-oriented mapping (experimental)"

- **Claim (OBSERVED):** the yosys-abc help text, in the ORFS image's build.
- **Implementation:** exists in ABC; algorithm undocumented in anything retrieved (UNVERIFIED). Plausibly the "preliminary implementation" satlut mentions (INFERRED).
- **Evaluation:** in W10 T2, on adder, `&nf -p -a` gave the same area as `-p` (100.43).
- **Relation:** the closest possible *implementation* of standard-cell exact area recovery. **This must be run as a baseline** in any H1.6 evaluation.

### 3. Mishchenko, Brayton, Besson, Govindarajan, Arts, van Besouw — *Versatile SAT-based remapping for standard cells* (IWLS 2016; `mfs3`)

- **Claim (talk slides, UNVERIFIED detail):**
  - windows (TFO=2, TFI=4);
  - SAT-based Boolean resynthesis with implicit don't-cares on mapped standard-cell networks;
  - area-oriented, with delay preserved (unchanged in the shown experiment);
  - about 3.5% node reduction on a large industrial cone.
- **Relation:** Boolean (functional) resynthesis, not covering over a fixed cut-match space. It is complementary to H1.6, and a stronger baseline class for *area after mapping* overall.

### 4. Costamagna, Tempia Calvino, Mishchenko, De Micheli — *Area-Oriented Optimization After Standard-Cell Mapping* (ASP-DAC 2025; IWLS'24 version *Post-mapping resubstitution for area-oriented optimization*)

- **Claim (PAPER, extracted):**
  - "replaces circuit sub-portions with high-quality mapped sub-networks stored in a database";
  - dependency cuts; don't-cares;
  - optional required time at the outputs;
  - "the first open-source engine for optimizing circuits mapped with a library of standard cells";
  - EPFL: additional average area reduction "5 47%" (the extraction lost the decimal point; most likely 5.47%, UNVERIFIED) "without delay degradation", after area-oriented optimization and mapping.
- **Related work they cite:** Benini et al. (2–3-cell windows remapped by generalized matching, structural substitutions) and Kravets et al. (window-based resubstitution after mapping).
- **Relation:** Boolean resubstitution that restructures logic "not available to the technology mapper". It does not resolve covering choices inside the mapper's space.
  - It sets a **practical bar**: any covering-level method must add area savings *on top of*, or *comparable to*, about 5% post-mapping resubstitution to matter to users.
  - It also means the *total* post-mapping headroom is at least about 5% on EPFL. The *covering-level* share of that headroom is exactly what A1 measures.

### 5. Chaudhary and Pedram — *Computing the Area versus Delay Trade-off Curves in Technology Mapping* (DAC 1992; TCAD 1995)

- **Claim (search summary):** per-node delay functions; reverse-topological selection; polynomial on node-balanced trees; "easily extended" to DAGs.
- **Relation:** kills H1.2. It is not a decomposition by ambiguity.

### 6. Ghiasi, Bozorgzadeh et al. — *A Unified Theory of Timing Budget Management* (ICCAD 2004; TCAD)

- **Claim (search summary):** budgeting problems as min-cost flow, including optimal integer budgeting for library mapping.
- **Relation:** kills H1.4. H1.6 does not budget; it resolves timing exactly within the restricted model.

### 7. Liu, Shelar, Hu — *Delay-optimal simultaneous technology mapping and placement* (ICCAD 2008) / *Simultaneous Technology Mapping and Placement for Delay Minimization* (TCAD 2011)

- **Claim (search summary):** Lagrangian relaxation to assess the timing criticality of DAG paths, for *delay*.
- **Relation:** kills H1.1. Not related to H1.6's decomposition.

### 8. Priority cuts / cut ranking and pruning

(Mishchenko et al. ICCAD'07; PRAETOR, Cong et al.; *SLAP* supervised priority cuts; *Revisiting Priority Cuts*, 2026. Titles only; UNVERIFIED details.)

- **Relation:** these prune *cut candidates by cost* at each node so that *heuristic* enumeration stays tractable. That is value-based restriction, but it is not joint exact resolution.
- **Reviewer objection this invites:** "restricting candidates by cost is what priority cuts do."
- **Answer, to be defended only with data:** priority cuts restrict *which cuts are enumerated* before a heuristic selection. H1.6 restricts *which decisions are re-opened* after the heuristic, and then resolves them *jointly and exactly*.
- **Consequence:** the distinction is real in mechanism, but its *value* is entirely empirical (A2/A3).

### 9. *Revisit Choice Network for Synthesis and Technology Mapping* (arXiv 2508.14068, 2025)

- **Claim (search summary):** screening and pruning of structural "choice cones" by hybrid scores.
- **Relation:** structural choices in the *subject graph*, not match ambiguity. Complementary.

## Searches performed for H1.6 (this wave)

| # | Query theme | Result |
|---|---|---|
| 1 | Lagrangian relaxation in mapping (area/delay) | Liu/Shelar/Hu (delay) |
| 2 | Exact/ILP DAG covering, delay-constrained | Kukimoto DAC'98 (delay-optimal); Chaudhary–Pedram; DAOmap |
| 3 | Slack budgeting in mapping | Unified budget theory; AIG slack-budget restructuring (GLSVLSI'08) |
| 4 | Area–delay trade-off curves | Chaudhary–Pedram |
| 5 | SAT-based exact/window re-mapping for standard cells | satlut (LUT); mfs3 (standard cells, Boolean); ASP-DAC'25 resub |
| 6 | ABC `&nf` SAT-based area mode | no public description found |
| 7 | Candidate pruning plus exact covering | priority cuts / PRAETOR; choice-network pruning |
| 8 | Tempia Calvino / Mishchenko 2024–26 | ASP-DAC'25; IWLS'24; versatile mapping ASP-DAC'22/'24 |
| 9 | MCTS / beam search in mapping | nothing specific to cell mapping found |
| 10 | Measured optimality gaps of standard-cell mappers | nothing specific found |

## Contribution boundary (what remains plausible, and on what condition)

- **Occupied:**
  - exact *window* re-covering (satlut; standard-cell preliminary / `&nf -a`);
  - Boolean post-mapping resynthesis (mfs3; ASP-DAC'25);
  - trade-off curves;
  - budgeting;
  - Lagrangian criticality;
  - cost-based cut pruning for enumeration.
- **Not found (which is not the same as novel):**
  1. A decomposition of *standard-cell covering* by decision ambiguity, resolved *jointly and exactly at whole-circuit scale*.
  2. A measurement of how much of standard-cell mappers' area loss, at fixed delay and within their own cut-match space, is (a) present at all and (b) concentrated in near-tie decisions.
- **Condition for plausibility:** item 1 is worth building only if item 2 comes out favourably (A1, A2, A3). If A1 fails, the problem is invalidated for this search space: all remaining post-mapping headroom is structural or Boolean, which ASP-DAC'25 and mfs3 already address. If A2 or A3 fails, the mechanism is invalidated, and topology windows (occupied) remain the only exact route.
- **The strongest remaining reviewer objection, stated in advance:** "Even if A1–A3 hold on small circuits, `&nf -a`/`&satlut`-style windows plus ASP-DAC'25 resubstitution may already capture the same area. H1.6 is only interesting if it beats *those* at matched delay and runtime on circuits too large for whole-circuit exact search." That comparison is the research-development test (06), not the first experiment.
