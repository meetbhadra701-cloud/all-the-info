# PPA-Delta public contracts v1.0

`src/ppa_delta/contracts.py` is the authoritative Python interface and the
schemas in `schemas/` are the authoritative JSON interfaces. Changes require a
new version plus a peer-acknowledged handoff.

## Evaluator boundary

Only an `Oracle` returns an `EvaluationResult` and decides whether a candidate
is `INTERESTING`. Candidate generators and reducers never invoke Yosys/EQY or
reimplement the area predicate. `FormalStatus.PASS` is explicit evidence, not
an exit-code alias. Metrics remain null when their stage did not complete.

The exact C03 evaluator command surface will be:

```text
ppa-delta evaluate --pair benchmarks/pairs/PAIR/pair.json --config configs/area-v1.json --out runs/AGENT/RUN --agent AGENT [--no-cache]
```

At C02 this command is intentionally help-only and exits 2 if invoked; C03
implements it.

## Snapshot and generator boundary

`PairSnapshot` contains absolute snapshot paths, copied-source hashes, a frozen
manifest/interface map, and a pair hash. `Candidate` points to a different
immutable candidate directory and records transformation ID, parent hash,
candidate hash, and `SizeVector`. Generators implement:

```python
def propose(self, pair: PairSnapshot, work_dir: Path) -> Iterable[Candidate]: ...
```

The shared `SizeCounter` protocol is declared here at Claude's request. Claude
implements the canonical parser/count in `ppa_delta.coupled` during L05; Codex
baselines consume that implementation rather than creating a competing count.

After emitting a schema-valid pair, generators call
`ppa_delta.oracle.snapshot_candidate(pair_manifest, snapshot_dir,
transformation_id=..., parent_pair_hash=...)`. The helper stable-copies the
manifest, RTL, and license; computes the evaluator-authoritative pair hash and
canonical `SizeVector`; and returns a complete immutable `Candidate`. Reducers
therefore do not depend on the evaluator's private snapshot representation or
duplicate content hashing.

## Pair manifest example

```json
{
  "schema_version": "1.0",
  "pair_id": "example-development-pair",
  "top_before": "top",
  "top_after": "top",
  "files_before": ["before.v"],
  "files_after": ["after.v"],
  "interface": [
    {"name": "a", "direction": "input", "width": 8, "signed": false},
    {"name": "out", "direction": "output", "width": 8, "signed": false}
  ],
  "meaningful_outputs": ["out"],
  "semantics": "combinational-two-state-v1",
  "metric": "mapped_cell_area",
  "area_unit": "Nangate45_library_area_unit",
  "relative_threshold": 0.05,
  "absolute_threshold": 0.532,
  "origin": "synthetic-handcrafted",
  "family": "example",
  "split": "development",
  "provenance": {
    "origin_type": "synthetic",
    "source_url": null,
    "author": "PPA-Delta contributors",
    "license": "Apache-2.0",
    "license_file": "LICENSE",
    "acquired_utc": "2026-09-09T00:00:00Z",
    "notes": "Example only; not a qualifying benchmark."
  }
}
```

`validate_pair_manifest()` additionally rejects absolute paths, traversal,
missing source files, missing license files, duplicate port names, and an
interface without both input and output ports.

## Fake-oracle boundary

The only fake oracle is `tests/codex/fakes.py`. It is labeled test-only and
rejects paths outside a test-owned root. It may exercise reducer control flow;
its results cannot qualify a benchmark, support a gate vote, or be exported as
EDA evidence.
