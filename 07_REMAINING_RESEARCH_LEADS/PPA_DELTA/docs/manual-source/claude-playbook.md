# Claude Execution Manual

You are the research, benchmark and coupled-reduction owner for PPA-Delta. Execute this manual in the existing user-started Claude Code session with local filesystem and terminal access. **NO SUBAGENTS: perform all research, coding, testing and review inline. Never invoke Agent/Explore/Plan subagents, teams, delegated reviews, another model through an API, or another Claude/Codex process.** Codex is the separate peer the user starts; communicate through local files.

The supplied reducer is not already implemented. The working helper handles coordination and vault notes. This manual includes the shared technical contract and all weekly gates below. Live canonical copies are in the vault; apply acknowledged change notes when resuming after the initial v1 delivery.

## A. Human setup — do this once

1. Keep the entire `PPA-Delta` folder together at `C:\Users\meetb\OneDrive\Documents\ChatGPT\ideation\PPA-Delta`, or one replacement location used by both agents.
2. Open Claude Code in this exact local folder. Use the terminal/IDE/local coding mode that can read and write the folder. Uploading the manual to a plain chat alone cannot keep the local vault updated.
3. If using a terminal, navigate to the folder first, then start your installed Claude Code normally. Do not select a separate worktree, cloud clone or remote session for this workflow. This manual does not require a particular model or subscription.
4. Open Codex on the same physical folder and give it `CODEX-MANUAL.md`.
5. In Obsidian, use **Open folder as vault** and select `C:\Users\meetb\OneDrive\Documents\ChatGPT\ideation\PPA-Delta\Obsidian-Vault`. Read `00-Home`; no plugins or manual note entry are needed.
6. Paste the following message into Claude Code.

```text
Work in C:\Users\meetb\OneDrive\Documents\ChatGPT\ideation\PPA-Delta.
Read CLAUDE.md, AGENTS.md and CLAUDE-MANUAL.md. You are Claude, the research,
benchmark and coupled-reducer owner. Codex is running separately in this
same folder. Follow file ownership, task dependencies and weekly gates.
NO SUBAGENTS: work inline; no Agent/Explore/Plan workers, agent teams,
delegated reviews, new model sessions or model API calls. Automatically
maintain Obsidian-Vault with evidence, handoffs and decisions. Begin L01;
L02 can proceed while Codex prepares the environment. Do not ask me to
maintain notes. Do not publish, contact anyone or start month two.
```

If the project moved, replace the path in both startup prompts. Keep the manuals and vault under the shared root. Do not depend on Claude's private auto-memory as the project record; the user must be able to see the record in this vault.

## B. First ten agent actions

1. Confirm the working directory and inspect existing files. Read `CLAUDE.md`, which imports `AGENTS.md`, then read this playbook and current protocol.
2. Verify `.claude/settings.json` includes a deny rule for the `Agent` tool. Do not run an initialization workflow that may create subagents. The user instruction applies even if client versions differ or a tool remains exposed.
3. Confirm you have write access to `research/`, `benchmarks/`, `src/ppa_delta/coupled/`, `tests/claude/` and your own vault note folders. Do not touch Codex-owned package configuration or helper code.
4. Discover the available Python interpreter. Use the delivery-time path in the shared protocol if valid. Do not install another toolchain while Codex owns environment setup. If Python is unavailable, write an initial Markdown note directly in your own journal folder and continue inline reading/design work.
5. Run `scripts/control.py status --agent claude` with the discovered Python. Read inbox messages and acknowledge them after reading.
6. Mark L01 IN_PROGRESS. Read the existing research audit once. It rejected a broad RTL optimizer, not this narrowed reducer; do not treat its historical DO NOT BUILD wording as a command to abandon the new scope.
7. Search only the unresolved reducer mechanism. Save sources and conclusions in your lane and the vault, including uncertainty and inspected versions.
8. Start L02 when appropriate if L01 is blocked on source access. Only one implementation task is active at once; record the previous task as blocked before switching.
9. Inspect Codex's runtime/API handoffs when they arrive. Use its evaluator, not a private competing definition of equivalence or area.
10. Finish each work chunk with a durable evidence note and exact next step. When no task is ready, send one local handoff, save state, and yield without repeated polling.

## C. Week 1 tasks

### L01 — Focused novelty gate

Form the exact question: “Does an existing hardware testcase reducer jointly shrink two RTL descriptions while retaining equivalence between the reduced descriptions and a reproducible quantitative synthesis-area regression?”

Read `02-Research/Existing-Research-Audit.md` and `02-Research/Novelty-Question.md`. Search mechanisms and synonyms: hardware/Verilog testcase reduction; coupled or paired reduction; equivalence-preserving minimization; quality-of-results regression reduction; synthesis QoR debugging; metamorphic compiler testing; differential reduction. Investigate Yosys testcase reduction, Verismith-associated reduction, and general reducers such as C-Reduce/Perses as search leads, not presumed direct matches. Verify actual official repositories/papers before assigning features.

Create `research/prior-art-matrix.md` with source title, authors/owner, date, version/commit, inspected section, exact URL, input language, number of programs reduced, preserved predicate, formal equivalence use, PPA/QoR preservation, reduction operations, public code status and remaining uncertainty. Search patents only around a precise mechanism if the closest literature leaves a plausible invention; do not restart a broad EDA patent survey.

Aim for the five closest relevant antecedents; avoid filler counts. Use a bounded initial search, normally one working day, following backward references and relevant code. Stop extending the survey once the material question is resolved or a concrete access limitation is documented. Write the strongest argument that the contribution is already done and a two-sentence surviving difference, if any. Never claim uniqueness from lack of a search hit.

Acceptance: a candid mechanism-level matrix and PASS-candidate / REVISE / STOP recommendation with sources. Send Codex a short research handoff. Mark the research task DONE when the investigation artifact is complete even if its recommendation is STOP; then record the appropriate gate outcome immediately. Task completion is not project approval.

### L02 — Candidate pair inventory

Can start before the EDA environment is ready. Create candidate pairs and provenance in `benchmarks/candidates/`, not the qualified corpus. Sources may be transparent handcrafted examples or compatible public designs/changes. Identify mux/arithmetic sharing, factoring/reassociation, and width/extension structure as candidate families; do not assert that any produces a regression until measured.

Record every attempted pair, source license, URL/commit or synthetic construction, intended edit and expected semantics in a candidate ledger. Construct controls: inequivalent, identical, unsupported and degenerate-output pairs. Do not confuse these controls with the three required regressions. Exclude employer IP and unavailable proprietary libraries.

Acceptance: candidate manifests, original files and a provenance ledger Codex's schema can validate. If the schema is not ready, use a draft in your lane and migrate after C02 rather than changing Codex's schema unilaterally.

### L03 — Qualify three real regressions

Dependencies: L02 and C03. Read `coordination/runtime.json`, then use Codex's actual evaluator command in UUID directories under `runs/claude/`. Measure candidates and keep rejected attempts. If synthesis removes an apparent inefficiency, record equal area and try another structural case; do not downgrade the flow or alter comparison semantics to force a win.

Promote exactly qualified examples into `benchmarks/pairs/` with real equivalence evidence and frozen thresholds/configuration references. Supply at least three candidates meeting the gate's repeatability criteria; C04 independently reruns them. Acceptance: three measured equivalent, nondegenerate area-regression pairs, complete provenance and stable manifests. Send the pair IDs and run paths to Codex.

### L04 — Week 1 review and corpus plan

Dependencies: L01, L03 and C04. Read Codex's independent qualification results. Freeze pair identities/configuration for Week 2; prepare a plan for ten cases without pretending the seven additional ones already qualify. Write your Week 1 memo, distinguishing source novelty, implementation availability and actual measured results. Vote with the helper. If novelty or reproducibility fails, do not start Week 2 merely because Codex is ready.

## D. Week 2 tasks

### L05 — Reduction semantics and baseline review contract

Dependencies: L04 and both Week 1 PASS votes. Specify supported source AST operations and correspondence rules in `docs/claude/reduction-design.md`. Select an actual parse/emit library by verifying that it preserves explicit bit widths, signedness and source semantics; ask Codex to add dependency pins. Do not use an optimized netlist or regular-expression substitutions as the source-reduction representation.

Describe edit-group reconstruction for the simple baseline, common primitive operations for the independent/coupled comparison, size counting and meaningful-output constraints. Prepare tiny expected-output fixtures. Acceptance: Codex acknowledges the baseline/generator contract; no unresolved interface changes remain before C06.

### L06 — Adversarial evaluator checks

Dependencies: C05 and L05. Own tests in `tests/claude/`: malformed outputs, stale PASS logs, library-area omissions, cache changes, mismatched interfaces, signed extension cases, unsupported sequential/X behavior, zero-area degeneration and final verification failure. Run them through the public evaluator interface. A fake oracle may test generator behavior but never support a formal/area claim.

Send each actual defect to Codex with a minimal reproducer and expected classification. Retest its fix. Acceptance: the available interface rejects your adverse controls correctly and cannot promote UNKNOWN or invalid metrics as interesting.

### L07 — Baseline usefulness audit

Dependencies: C07 and L06. Run the edit-only and independent-side baselines on a qualified pair from a clean output directory. Check termination, budget accounting, retained failures, source-size counting and replay contents. Write a Week 2 review with real logs. If the simple baseline already solves the practical problem, record that as a threat to the proposed contribution. Cast your Week 2 vote after the acceptance conditions are satisfied.

## E. Week 3 tasks

### L08 — AST representation and correspondence

Dependencies: L07 and both Week 2 PASS votes. Implement only inside `src/ppa_delta/coupled/` and `tests/claude/`. Parse source pairs into an explicit representation; map identical or demonstrably corresponding structures conservatively; retain unmatched constructs. Build definition/use dependencies and group edits so a removed definition does not leave invalid references. Handle parse/emit round trips and operators individually.

Use deterministic IDs derived from source/candidate structure, not unstable object addresses. Include parent identity and operation details in a candidate trace. Acceptance: round-trip and candidate tests preserve the declared subset, produce valid manifests, and leave originals unchanged. Publish a generator-ready handoff to Codex.

### L09 — Coupled search engine

Dependencies: L08 and C08. Implement coordinated proposals and hierarchical dependency grouping against the published `Oracle`/`Budget` interfaces. Always write a new candidate directory. Count each proposal and expensive execution correctly. Retain only a strictly smaller interesting result under the v1 size objective; handle no-success, interruption, timeout and malformed candidates.

Start with a small number of understandable transformations. Do not add a neural ranker, LLM, web service or complex planner. Acceptance: at least one real reduction succeeds on a development pair, survives uncached verification and integrates without bypassing Codex's oracle. Send C09 the exact import/CLI contract and test commands.

### L10 — Development comparison and ablation

Dependencies: C09 and L09. Run the same frozen development inputs through all methods using C08's harness. Disable structural matching for the preregistered ablation; make other settings identical. Plot/tabulate canonical AST sizes, valid-export count, time and calls. Include every case and inspect whether the improvement depends on an unfair baseline restriction.

Write the strongest negative interpretation, not only successes. Supply raw rows and a Week 3 memo to Codex for C10. Vote only after the gate requirements and final checks are met. If the coupled approach does not improve upon the simple alternatives after the permitted bounded revision, recommend STOP/PIVOT honestly.

## F. Week 4 tasks

### L11 — Freeze the ten-pair suite

Dependencies: L10 and both Week 3 PASS votes. Acquire/qualify additional candidates using the same oracle. Freeze ten pairs across at least three families, development/held-out assignments and provenance before final method tuning. Prefer at least three real public-design/historical cases. Record all rejected candidates in the discovery ledger; do not omit hard cases after discovering the final method loses on them.

Write `benchmarks/suites/month-one.json` with IDs, hashes, families, split, config identity and eligibility evidence. Document whether held-out cases share origins with development examples. Acceptance: Codex can independently verify and run the suite. Do not inspect held-out reduction results to tune the method without declaring the evaluation compromised and creating a genuinely new holdout.

### L12 — Analysis of the complete experiment

Dependencies: C11. Own the analysis scripts and report in `analysis/`. Read machine-readable rows, not agent recollections. Compute all frozen metrics and denominators; include raw tables, failed cases, no-gain originals and invalidated exports. Avoid claims of statistical certainty from ten examples.

Produce a method comparison and a separate ablation table. Explain which transformations help, which cases defeat the reducer, and whether retained regressions remain meaningful small examples. No synthetic testimonials or invented downstream fixes. Acceptance: a rerunnable analysis command regenerates the report from the frozen run manifests and produces the same counts.

### L13 — Maintainer relevance and month-one recommendation

Dependencies: L12 and C12. Inspect the final bundles as a prospective user: can you reproduce them from the README, see expected and observed metrics, understand the exact tool/library conditions, and identify the retained RTL difference? Complete the maintainer-ready checklist from the gate. Draft one technically specific upstream issue locally; do not send it without user authorization. Clearly separate internal review from any actual outside feedback.

Prepare the final novelty/differentiation statement, a possible paper outline, limits to the claim, useful next integration, and CONTINUE proposal / REVISE / STOP recommendation. Optional patent notes must identify a specific mechanism and remain unverified; do not promise patentability. Update the evidence ledger with only real artifacts and events. Cast your Week 4 vote and send the final analysis to Codex for C13.

## G. Mandatory vault behavior

At session start/end and each source, benchmark, experiment, issue, handoff or decision that changes the project record, publish the relevant note automatically. Use source titles, dates, exact URLs, inspected sections and uncertainty for research notes. Use command/config/source identity, measured values, raw-artifact paths, outcome and limitations for experiment notes. Do not write to Codex's notes or the generated dashboard directly.

Write an evidence body file yourself under `scratch/claude/`, then run the helper. Mark tasks DONE only with existing evidence paths. The user's role is to read the vault, not populate it. The helper and future evaluator wrappers update the dashboard; no plugin is required.

## H. Resume prompt

```text
Resume PPA-Delta in the same local folder. Read CLAUDE.md, AGENTS.md,
your latest journal, Project-Status.md and unread handoffs. Continue
the next ready Claude task without repeating the broad research.
No subagents, teams, extra model processes or API calls. Respect Codex's
file ownership, maintain the Obsidian vault, and obey weekly gates.
```

If Codex is idle and you need its output, send one local handoff, mark the task blocked, finish independent ready work, then yield. Do not launch or impersonate Codex. A file handoff does not automatically resume an idle model session.
