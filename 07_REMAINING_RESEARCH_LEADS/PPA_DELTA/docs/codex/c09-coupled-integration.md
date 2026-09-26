# C09 coupled reducer integration

## Delivered integration

The shared reduction runner and public CLI now expose `coupled`,
`coupled-no-matching`, and the preregistered Yosys `bugpoint` external-predicate
baseline. All methods use the same `Budget`, immutable candidate snapshots,
canonical `SizeCounter`, evaluator, failure retention, and fresh-final-validation
rules. Candidate materialization and generator errors are counted and retained in
the trace rather than aborting the run.

The bugpoint adapter combines both designs in one elaborated RTLIL design, protects
interface ports, enables only `-cells -wires`, and deliberately omits destructive
`-connections` (`x` reconnection). Each Yosys proposal is exported to supported
Verilog, converted from Yosys's non-ANSI header into the frozen ANSI subset, and
classified by the real PPA-Delta evaluator. A result can only count as reduced if
the final export parses under the canonical source AST counter and passes a fresh
uncached evaluator run. Predicate attempts and all failures are retained in
`predicate-state.json`.

## Real integration evidence

The public six-method command was:

```powershell
.\.venv\Scripts\ppa-delta.exe compare `
  --suite configs\comparison-smoke-v1.json `
  --out runs\codex\c09-fixed-six-method-20260910T015000Z `
  --agent codex
```

It produced six denominator rows, six valid witnesses, and one identical initial
pair hash (`18f663...d94e2`) and size (47 pair-AST nodes) across every method:

| method | status | final AST | proposals | evaluations |
|---|---:|---:|---:|---:|
| unreduced | UNREDUCED | 47 | 0 | 1 |
| edit-only | NO_GAIN | 47 | 5 | 1 |
| independent | REDUCED | 39 | 4 | 6 |
| bugpoint | NO_GAIN | 47 | 20 | 22 |
| coupled | REDUCED | 35 | 24 | 26 |
| coupled-no-matching | REDUCED | 35 | 24 | 26 |

The coupled row exactly reproduced Claude L09's accepted lineage and final hash
`f83b933...bba4a`: `coupled-inline-all`, `coupled-const0-d`, then
`coupled-merge-a-into-c`. Its fresh result is INTERESTING, formal PASS, uncached,
47.614 -> 57.988 area (+21.8%). The no-matching and independent rows both end at
35 and 39 respectively. Coupled and no-matching have the same three accepted
transformations and final hash on f1, which confirms that f1's advantage is from
coordination rather than structural matching. Bugpoint terminated naturally after 20 proposals; every attempted one-sided
RTLIL cell/wire removal failed closed as UNSUPPORTED, so it correctly retained the
original as NO_GAIN.

Primary artifacts:

- `runs/codex/c09-fixed-six-method-20260910T015000Z/comparison.json`
- `runs/codex/c09-fixed-six-method-20260910T015000Z/matrix.jsonl`
- `runs/codex/c09-fixed-six-method-20260910T015000Z/rows/`
- `runs/codex/c09-fixed-six-method-20260910T015000Z/methods/f1-mux-share-add/`
- `runs/codex/c09-fixed-six-method-20260910T015000Z/publication.json`
- `runs/codex/c09-wheel-fixed/ppa_delta-0.1.0-py3-none-any.whl` (SHA-256
  `cbd827780d2a416adafd38a87b08e84b4ca4edd23b7994b7b283c86697e05d92`)

The benchmark source hashes remained the frozen values after the run (`before.v`
`5253134e...1654`, `after.v` `8ed134da...2c16`, license
`83f92cf0...9763`). No corpus file or shared configuration was modified.

## Ablation correction and interpretation

Codex's first review found that the original no-matching ablation also removed
coordination and two proposal classes. Claude accepted the finding and made a
bounded owner-lane correction while preserving the original L09 run. Both modes
now share inline-all, merge-inputs, and input-constant proposals in identical
order; only matching mode calls L08 `correspond()` and adds `cse-extract`
proposals.

Independent inspection confirms the correction: on a2, no-matching's 38 proposals
are exactly the non-CSE prefix/subset of matching mode's 40 proposals. The two CSE
proposals are generated from explicit correspondence and apply without corrupting
the pair, but each grows canonical pair AST from 76 to 78, so the shared runner
rejects it as `LOCAL_NON_SHRINKING` before EDA. They are not accepted reductions.
The clean Claude evidence (f1 35==35 and a2 62==62) and Codex's corrected f1 matrix
therefore support a null matching effect. Current evidence supports coordinated
pair reduction, not a measurable structural-correspondence benefit.

## Verification

- Codex unit suite: 48 tests passing.
- Claude unit suite: 43 tests passing.
- `scripts/check_pack.py`: PASS before final documentation.
- Failed setup and bounded bugpoint probes remain under `runs/codex/`; they are not
  used as positive evidence. The one development probe that raised before its
  normal result path was repaired as a persisted/published `SETUP_ERROR` without
  rerunning it.
