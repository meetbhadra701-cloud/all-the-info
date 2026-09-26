# Remaining and provisional leads

## PPA-Delta coupled reducer

The strongest locally recoverable current lead is the PPA-Delta project under `01_RESEARCH_OBJECTIVES_AND_STRATEGY/PPA_DELTA/` and the associated design/review material under `07_REMAINING_RESEARCH_LEADS/PPA_DELTA/docs/`. Its question is narrow: whether a coupled reducer using structural correspondence can produce measurable value beyond valid simple baselines under a frozen benchmark and time budget.

The local project materials report a C10 six-method comparison with equal 200-candidate / 1800-second budgets and cache disabled. Coupled reduction beat valid baselines on 3/3 cases; a repaired bugpoint baseline produced NO_GAIN; one comparison reports 39 versus 60 candidates on a 21-node case without matching. A separate review says the coupled method missed the stated >=20% improvement bar on 0/3 cases and that structural correspondence was not yet supported. The correct status is therefore PROVISIONAL/REVISE, not proven novelty.

What remains unresolved: broaden and freeze the baseline set, establish external prior-art coverage, validate across additional workloads, quantify overhead and reproducibility, and determine whether the measured advantage is a robust scientific mechanism rather than benchmark-specific engineering.

## Mapper semantic-contract gap

The Wave 5B transcript evidence and MUXWISE material suggest a real interaction between memory semantic contracts, read/write granularity, mapper pattern recognition, and physical resource selection. The strongest available status is an engineering/semantic-contract gap with constructive tests, not a proven new theory. A future investigation must use a correctly specified witness, independent oracle, clean tool provenance, and a broader matrix before treating it as a research contribution.

## Cross-stage timing/security guarantees

DITSpec-HLS, MaskedHLSVerif, L2S, CODO, and GhostForge repeatedly point toward a potentially meaningful question: how a semantic/security guarantee survives composition, lowering, scheduling, retiming, and physical implementation. The broad formulation is heavily occupied; only a precisely scoped theorem plus independently reproducible artifact should survive further screening.
