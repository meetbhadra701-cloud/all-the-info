# L01 — Search log

Owner: Claude · Task L01 · Classification: OBSERVED. All searches run 2026-09-09.

Bounded, focused search per the manual: start from the existing audit, investigate only the
unresolved reducer mechanism, stop when the material question resolves. Not a broad EDA
re-survey.

## Queries run (WebSearch / WebFetch), 2026-09-09

| # | Query / URL | Purpose | Decisive result |
|---|---|---|---|
| 1 | `bugpoint` pass source, `raw.githubusercontent.com/YosysHQ/yosys/main/passes/cmds/bugpoint.cc` | Read the actual failure-predicate + reduction ops of the highest-STOP-risk antecedent | Single design; unary failure predicate; RTLIL; no equivalence, no metric. Verbatim option list captured in matrix row 1 |
| 2 | "Yosys bugpoint pass documentation minimize failing design script" | Confirm docs match source; find `exec`/external-failure capability | Docs confirm `exec`-based external failures and non-crash `select -assert-*` predicates |
| 3 | "coupled reduction two RTL designs preserving equivalence synthesis area regression witness" | Direct hit on the exact contribution | Only RTL2RTL equivalence-checking and optimization; no coupled *reducer* |
| 4 | "Verismith Verilog test case reduction equivalence checking synthesis fuzzing Herklotz" | Nearest hardware reducer besides bugpoint | Single-design Verilog reducer for synthesis *miscompilation* bugs; equivalence used as bug oracle |
| 5 | "delta debugging pair of programs relational predicate joint reduction two inputs simultaneously reducer" | Find any pairwise / relational reducer | **PPR (FSE 2023)** surfaced — pairwise reduction exists |
| 6 | "reducing test cases for compiler performance regressions missed optimization bugs" | Software analogue of QoR-regression reduction | Differential perf-regression *detection* + minimization; program-level, not paired-equivalent |
| 7 | "PPR pairwise program reduction simultaneously minimizing bug-triggering and passing variant" | Pin down PPR's predicate and objective | PPR reduces seed+variant, minimizes their diff; predicate is a conjunction of two unary properties |
| 8 | PPR PDF `cs.uwaterloo.ca/~cnsun/public/publication/fse23/fse23.pdf` (text extracted locally, stdlib) | Read §4 Approach + §6 Discussion from the primary source | Confirmed: `psi_P(P') AND psi_Q(Q')`, no formal equivalence, opposite objective (minimize diff) |
| 9 | "hardware RTL testcase reducer preserving area delay power quality-of-results regression not crash" | Close the "quantitative-metric hardware reducer" question | None found; only optimization + detection. Negative confirmation recorded |
| 10 | Verismith README (raw) | Confirm reducer option names from primary docs | README omits reduction detail → documented access limitation on matrix row 3 |

## Access limitations (recorded, not worked around)

- Verismith's exact reducer command/option names are not in the README; confirming them needs
  the FPGA 2020 paper body or the Haskell source. The verdict (single-design, unary
  correctness-bug predicate, source-level) is firm from the abstract and secondary sources, so
  this does not change the matrix; noted for completeness.
- Two source PDFs were saved locally by WebFetch and parsed with a stdlib inflate+text
  extractor (no external tool, no model call). Extraction is lossy on ligatures; quoted
  fragments were cross-checked against the DOI abstract.

## Stop criterion met

The material question — does any existing reducer preserve a *relational* equivalence+area-gap
predicate over a pair — is resolved (no) after five closest antecedents plus the negative
confirmation. Search halted per the manual rather than extended into a broad survey. Patent
search deferred: the surviving mechanism is narrow and the literature question is settled;
a patent pass is only warranted if the contribution advances to a filing decision (Week 4 /
L13), and would then be scoped to the relational predicate.
