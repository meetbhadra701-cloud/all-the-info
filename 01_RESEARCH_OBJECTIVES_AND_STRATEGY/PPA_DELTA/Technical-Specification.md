# PPA-Delta — Technical Specification v1

## 1. Purpose and claim boundary

Build a research prototype that reduces two equivalent RTL descriptions together while retaining a reproducible synthesis-area regression. The deliverable is a small pair of equivalent circuits plus evidence and a replay command. It is a diagnostic tool, not an RTL optimizer and not a proof of the synthesis tool's internal cause.

Research hypothesis: dependency-aware paired reduction finds smaller valid regression witnesses within a fixed compute budget than edit-only delta debugging, independent reduction, and a Yosys `bugpoint`+external-predicate baseline. This is a hypothesis, not an established novelty or performance result. Reuse the existing audit in `02-Research/Existing-Research-Audit.md`; only investigate the narrow hardware-reducer gap in Week 1.

The two reduced designs must be equivalent to each other. They need not implement the original complete design. Never describe the reduced pair as a drop-in replacement for the original chip. A retained PPA difference establishes a reproducible witness, not a functional bug or causal explanation inside the optimizer.

## 2. Month-one support contract

- Synthesizable combinational Verilog-2005, one top module per side, with an explicit common port contract. Flatten a pinned local hierarchy if needed; preserve original files separately.
- Two-state, fully defined bitvector semantics. Reject latches, flip-flops, clocks, memories, blackboxes, inouts, delays, X/Z literals, undriven signals, multiple drivers, unsupported constructs and combinational loops.
- Enumerate supported operators and signedness behavior in a parser test matrix before enabling each transformation. Never use regular expressions as the semantic parser.
- Widths and signedness are explicit. Do not let a reduction silently change a retained port's width or signedness. First version can restrict operators while documenting rejected cases.
- No new input assumptions. No altered synthesis flags or library between A and B. The reducer may remove matching ports/outputs only as a coordinated transformation that updates both manifests identically; retain at least one nonconstant output depending on an input.
- Start with mapped standard-cell area. Use cell-library areas, not raw cell counts. Record counts separately. Do not call area results power or timing improvements.
- Formal validation uses a tested Yosys/EQY adapter. For this subset, combinational equivalence is sufficient. Neither bounded simulation nor a timeout is proof.
- Sequential RTL, OpenROAD timing, placement/routing, power, multi-clock and memories are post-gate extensions. Their exclusion controls experimental scope, not the user's device capabilities.

Glossary: RTL is the hardware source description; AST is its parsed syntax tree; equivalence means identical outputs for all permitted inputs; synthesis maps RTL to a cell library; Liberty is the cell-library format; oracle is the accept/reject evaluation function; delta debugging repeatedly removes subsets while retaining a condition; a witness is a replayable example; a gate is an evidence-based continue/stop decision.

## 3. Data flow

```text
Pair manifest + A RTL + B RTL + frozen toolchain/configuration
  -> validate supported syntax, interfaces and provenance
  -> prove original pair equivalent
  -> measure original A/B area and confirm a regression
  -> build corresponding structures and edit dependency groups
  -> propose a smaller paired candidate
  -> validate -> compile -> formal equivalence -> synthesis -> predicate
  -> retain candidate only if all checks pass
  -> repeat until budget or local fixed point
  -> independently re-evaluate best candidate without cache
  -> export pair, manifests, provenance, proofs, area reports, replay script
  -> generate experiment and evidence notes in the Obsidian vault
```

## 4. Regression predicate

Let `a` be mapped area for the reduced before design, and `b` for the reduced after design. Require finite `a > 0`, finite `b > 0`, matching area units and complete mapping. Define `r = (b - a) / a`.

A candidate is interesting only when: it is in the supported subset; its interfaces match; the formal result is explicit PASS; neither side is a constant-only or wire-only degeneration; all cells have valid area definitions; `r >= relative_threshold`; and `b - a >= absolute_threshold`.

Default discovery threshold is 0.05 (5%). The absolute floor is one minimum positive-area combinational cell from the selected library; record the cell and value. These are project screening choices, not universal significance thresholds. Store both thresholds per pair and freeze them before reducer comparison. Do not lower thresholds after seeing a weak result. If an original pair does not qualify, record rejection and retain its provenance.

Perform three uncached original-pair runs in separate directories. All three must pass the frozen predicate; record dispersion. A deterministic tool producing identical values is expected and must not be given artificial random seeds. During reduction one evaluation may filter candidates; final export requires three fresh uncached confirmations. Failed final confirmation invalidates the export and the success claim. For later stochastic physical flows, introduce a separately preregistered paired-seed protocol before using timing as a metric.

## 5. Evaluator contract

Codex owns `src/ppa_delta/contracts.py`, schemas and all evaluator code. Publish these before Claude integrates code. The interface version is `1.0`.

```python
def evaluate_pair(pair_manifest: Path, config: Path, run_dir: Path,
                  *, use_cache: bool = True) -> EvaluationResult: ...

class CandidateGenerator(Protocol):
    def propose(self, pair: PairSnapshot, work_dir: Path) -> Iterable[Candidate]: ...

def reduce_pair(pair: PairSnapshot, oracle: Oracle, budget: Budget,
                out_dir: Path) -> ReductionResult: ...
```

`PairSnapshot` contains copied source files, manifest, content hashes and interface map. `Candidate` references a new immutable candidate directory, transformation ID, parent pair hash and size vector. It never overwrites its parent. `Oracle` evaluates a candidate snapshot, validates cache identity and returns the result below. Baseline and coupled reducers use the same oracle, budget counters, source-size function and fresh final verification.

`EvaluationResult` JSON must contain:

| Field | Meaning |
|---|---|
| `schema_version`, `run_id`, `pair_id`, `parent_hash`, `candidate_hash` | Identity and lineage |
| `status` | Exactly one of INTERESTING, NOT_INTERESTING, UNSUPPORTED, COMPILE_ERROR, INEQUIVALENT, FORMAL_UNKNOWN, TOOL_ERROR, TIMEOUT, INVALID_METRIC |
| `formal.status` | PASS, FAIL, UNKNOWN, ERROR or NOT_RUN; never inferred from exit code alone |
| `formal.log`, `formal.tool`, `formal.counterexample` | Raw proof result provenance; counterexample nullable |
| `area.before`, `area.after`, `area.unit`, `area.delta_abs`, `area.delta_rel` | Nullable before metric stage; never replace missing data with zero |
| `size.before_ast`, `size.after_ast`, `size.changed_nodes`, `size.bytes` | Canonical parsed source size and secondary diagnostics |
| `thresholds`, `config_hash`, `toolchain_hash`, `library_hash` | Complete comparison identity |
| `commands`, `logs`, `wall_seconds`, `timeouts`, `cache_hit` | Exact argv, working directories and resources |
| `started_utc`, `finished_utc`, `source_provenance` | Auditable chronology and licensing/source origin |

Malformed reports, missing PASS markers, stale output files and unrecognized statuses fail closed. Compilation failure is not inequivalence. Any timeout is not interesting. Never accept a candidate from an earlier run's report. Preserve raw outputs even for rejected candidates.

Only the oracle may decide interest. Claude must not introduce a second evaluator or change thresholds inside a reducer. A change to a public interface requires an immutable proposal note, an explicit acknowledgement by the other agent, version update and contract tests before integration.

## 6. Inputs, directory layout and configuration

Each corpus pair lives in `benchmarks/pairs/<pair-id>/` with `before.v`, `after.v`, `pair.json`, provenance, license information and acquisition notes. Generated candidates never modify corpus originals.

```json
{
  "schema_version": "1.0",
  "pair_id": "example-placeholder",
  "top_before": "top",
  "top_after": "top",
  "files_before": ["before.v"],
  "files_after": ["after.v"],
  "semantics": "combinational-two-state-v1",
  "metric": "mapped_cell_area",
  "relative_threshold": 0.05,
  "absolute_threshold": null,
  "absolute_threshold_status": "resolve-from-frozen-library-before-use",
  "origin": "synthetic-or-public-record-required",
  "family": "declare-before-split",
  "split": "unassigned"
}
```

This example is not a qualified benchmark. Schema validation must reject it until all unresolved required values are supplied. Support only paths within the benchmark snapshot; reject traversal and missing source/license metadata.

`configs/area-v1.json` stores exact synthesis script, top handling, library path/hash, mapping options, environment, timeouts, repeat policy and toolchain identity. A human-friendly config can point to the immutable runtime manifest, but the evaluation identity contains the expanded effective configuration. No network dependency resolution during replay.

Initial per-case comparison budget: 200 proposed candidates or 30 minutes elapsed, whichever occurs first. Initial stage caps: 60 seconds compile, 120 seconds formal, 180 seconds synthesis per side, bounded also by remaining case budget. These are matched scientific budgets, not device assumptions; change them only before a new versioned experiment. Charge actual elapsed time and all attempted candidates, including failures and cache hits, to the same policy. Record EDA executions separately. Give each method its own cold cache for headline comparisons.

## 7. Baselines and candidate transformations

Codex implements an edit-only baseline first: define ordered edit groups against the original before side; apply subsets to reconstruct the other side; use ordinary delta-debugging partition/complement search while the oracle stays interesting. The patch semantics must be valid and deterministic. Exhausted search is only locally minimal relative to that transformation set.

Codex then supplies an independent-side baseline using the same allowed primitive simplifications, simplifying one side at a time while evaluating the pair. Include the unreduced pair as a zero-work reference.

Include Yosys `bugpoint` plus an external two-design predicate as the strongest existing-tool baseline, accepted from Claude's L01 proposal on September 9, 2026. Run it against the same frozen oracle, starting pair and wall/tool-call budget. Disable semantically destructive `'x` reconnection, preserve both input designs, and record that `bugpoint` operates on elaborated RTLIL rather than the source AST. A result counts as a valid reduction only if it exports supported Verilog source, passes the same fresh evaluator confirmations, and is smaller under the canonical source-AST counter; otherwise retain the original size and report the failure. This baseline tests whether an opaque relational predicate wrapped around an existing one-design hardware reducer is already sufficient.

Claude implements the coupled reducer: parse both sides; establish a conservative structural correspondence; construct definition/use dependency groups; generate coordinated proposals; use deterministic ordering and hierarchical grouping. Unmatched structures stay unchanged unless an explicit sound candidate operation handles them. The oracle validates functionality; the generator's structural matching itself is not a proof.

Initial primitives: remove matched unused declarations; remove corresponding output cones while retaining a meaningful output; replace corresponding subexpressions with same-width operands/constants when allowed; simplify matched conditional branches; remove groups of edits with dependency closure. Rebuild and reparse after transformations. Do not cut tokens, alter literals' widths by accident, or compare only pretty-printed line counts. Use original ASTs for source-oriented reduction and Yosys only as an elaboration/verification backend; optimized netlists are not a substitute for source ASTs.

Primary size objective is the sum of canonical AST nodes across both sides. Secondary tie-breakers are changed-node count and bytes. Smaller is strictly lexicographic; comments/whitespace are excluded. Freeze parser version and count definition. Reject non-shrinking candidates unless a separately budgeted exploration policy is explicitly part of a new experiment.

## 8. Experiment design

Week 1 needs three genuinely measured pairs; the first pair is a feasibility example, not a promised synthesis result. Candidate families include mux/arithmetic sharing, factoring/reassociation, and width/sign-extension structure. Modern synthesis may erase all of these differences. Search systematically and record rejected pairs instead of labeling a guessed example a regression.

Week 4 needs ten qualifying pairs from at least three structural families. Freeze seven development pairs and three held-out pairs before reducer tuning; keep all variants from an origin/family subgroup on the same side where possible and document residual similarity. Seek at least three pairs traceable to public designs or historical changes. If all ten are synthetic, classify external relevance as unproven and do not claim a strong build recommendation solely from them.

Run unreduced, edit-only, independent-side, `bugpoint`+external-predicate, coupled and coupled-without-matching ablation. Preregister additional ablations rather than selecting favorable ones. Use identical environment snapshots and budgets. Report every attempted case, eligibility rejection, timeout, solver unknown, failure and export invalidation. Ten cases support feasibility evidence, not a universal generalization claim.

Metrics: pair AST reduction fraction; retained-regression success count; median per-pair size advantage against the better simple baseline; elapsed time; EDA/formal calls; cache behavior; clean replay pass count; meaningful external feedback if any. Report numerator and denominator. If no valid reduction is found, retain the original pair as the final size and classify no gain. Failed final verification counts as failure, never disappears from the table. Report raw values alongside medians; no p-value fishing.

## 9. Replay export and user interface

Commands below are the interface to IMPLEMENT, not software already present:

```text
ppa-delta doctor --config configs/area-v1.json
ppa-delta evaluate --pair benchmarks/pairs/PAIR/pair.json --config configs/area-v1.json --out runs/AGENT/RUN
ppa-delta reduce --pair benchmarks/pairs/PAIR/pair.json --config configs/area-v1.json --method edit-only|independent|coupled --out runs/AGENT/RUN
ppa-delta replay --bundle exports/RUN --out runs/AGENT/FRESH-RUN
ppa-delta compare --suite benchmarks/suites/month-one.json --out runs/codex/COMPARISON
```

Do not run a command until its owning task implements it. CLI help must explain supported subset, thresholds, budget, all statuses and artifact locations. Every invocation produces machine-readable JSON plus a short human summary; non-success is distinguishable from a usable regression witness.

An export includes both RTL files, common interface manifest, original-pair hashes, transformation trace, final uncached proofs, all final area reports, immutable tool/image identity, scripts, relative paths, checksum inventory, licenses and provenance, and a short README. Large binary environments may be supplied by a pinned locally available image with a recorded digest; clean replay must say what it needs. Test export in a new directory with the original working tree and caches unavailable. Prohibit shell interpolation from untrusted filenames; launch subprocesses with argv arrays.

## 10. Tests and integrity

Meaningful test categories: known equivalent and inequivalent pairs; signedness/width errors; unsupported latches/X/Z/blackboxes; missing library area; empty reports; compiler crash; timeout; stale logs; cache identity changes; nonconstant-output guard; corrupted candidate manifests; paired reduction correctness; final replay without original paths. Never use mocked formal PASS as evidence that a real pair is equivalent. Unit mocks are only parser/control tests and must be labeled.

Store immutable inputs and tool outputs in agent-owned UUID directories. Snapshot source files only after hashes before and after copying agree; retry a bounded number of times if another agent is writing, then record a blocker. Never compare a live changing checkout. Use local filesystem locks for shared control metadata, not cloud-sync conflict resolution.

## 11. Evidence, publication and significance

The vault records claims separately from observations: source, exact artifact, result, limitations and verification identity. A local rerun by Claude is a second-agent check, not independent external adoption. Track real external usage, upstream issues/fixes, citations and feedback only when they occur. Do not fabricate users, papers, patents, interviews or results. No universal EB-1A numerical thresholds are claimed.

Potential paper: “Coupled RTL Reduction for Reproducible Synthesis-Area Regressions.” The paper must explain a surviving algorithmic difference, fair baselines, ablations and failure cases. A patent is optional and depends on a precise mechanism and professional review. Draft outreach locally; do not contact maintainers, publish code, submit a paper or disclose a potentially patentable mechanism without the user's authorization for that external action. Preparing a complete reviewable package needs no extra approval.

## 12. After the first month

Do not automatically start month two. If Week 4 passes, prepare a concrete proposal for synchronous designs, reset-aware equivalence, richer real regressions, and then physical/timing evidence. If the baseline performs as well as the coupled method, recommend a useful tooling/reproducibility project honestly or stop the research claim. Scope changes require the user after the one-month decision.
