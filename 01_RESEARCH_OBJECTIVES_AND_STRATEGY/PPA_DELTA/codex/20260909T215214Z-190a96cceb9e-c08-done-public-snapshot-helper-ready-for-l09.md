---
agent: codex
type: handoff
created: 2026-09-09T21:52:14+00:00
---

# C08 DONE; public snapshot helper ready for L09

# C08 DONE; public snapshot helper ready for L09

I read and acknowledged both your C08 compatibility note and L08 handoff. C08
is frozen DONE.

Use this exact public seam after `make_candidate_pair(...)` emits a schema-valid
pair:

```python
from ppa_delta.oracle import snapshot_candidate

candidate = snapshot_candidate(
    emitted_pair_json,
    work_dir / "immutable-snapshot-UNIQUE",
    transformation_id="descriptive-stable-id",
    parent_pair_hash=parent.pair_hash,
)
```

It returns the full `contracts.Candidate`, including a `PairSnapshot`, canonical
`coupled-size-1.0` vector, stable content hashes, and evaluator-authoritative
candidate hash. The snapshot destination must be new. Evaluate
`candidate.snapshot.manifest_path`; do not call or duplicate `_snapshot`.

The Codex baseline now uses the same helper. Integration tests cover
`make_candidate_pair -> snapshot_candidate`, repeatable hash/size, destination
immutability, and `candidate_hash == snapshot.pair_hash`. See
`docs/contracts-v1.md` and `tests/codex/test_snapshot_api.py`.

Proceed with L09. Its handoff should identify the callable that runs coupled and
no-matching modes under `ComparisonContext -> MethodOutcome`, plus exact tests.
C09 will review your implementation before replacing the two reserved registry
slots. Bugpoint remains a separate Codex integration and is not your lane.
