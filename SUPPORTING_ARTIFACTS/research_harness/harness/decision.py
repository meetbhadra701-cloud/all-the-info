"""Pre-registered comparative decision rules.

Origin: ubpgen/week2.py (decide). The UBP Week-2 kill rule was
    R = min over the complete competitors of metric(competitor) / metric(candidate),  R < threshold -> KILL,
with the candidate required to be valid (correct, DRC-clean, hold met) and every pre-registered competitor complete.
Written once, before any result, and then applied mechanically -- that is what stopped a 1.473 result being
rationalized as a pass.

The rule is metric-agnostic: pass lower-is-better metrics (A x T, runtime, proof time) as they are; for
higher-is-better metrics (throughput, coverage) pass their reciprocals or set higher_is_better=True.
"""
from __future__ import annotations


def ratio_rule(candidate: float, competitors: dict[str, float | None], threshold: float,
               required: list[str] | None = None, candidate_valid: dict[str, bool] | None = None,
               higher_is_better: bool = False) -> dict:
    """Decision of record. Missing required competitors -> INCOMPLETE (never a pass by omission).
    candidate_valid: named validity checks of the candidate; any False -> KILL whatever the ratio."""
    missing = [k for k in (required or []) if competitors.get(k) is None]
    out = {'threshold': threshold, 'missing': missing, 'candidate': candidate}
    if missing or candidate is None:
        out['verdict'] = 'INCOMPLETE'
        return out
    ratios = {k: (candidate / v if higher_is_better else v / candidate) for k, v in competitors.items() if v is not None}
    strongest = min(ratios, key=ratios.get)
    valid = dict(candidate_valid or {})
    out.update({'R': ratios[strongest], 'strongest': strongest, 'all': ratios, 'candidate_valid': valid,
                'verdict': 'PASS' if (all(valid.values()) and ratios[strongest] >= threshold) else 'KILL'})
    return out


def sensitivities(candidate: dict[str, float], competitors: dict[str, dict[str, float]]) -> dict:
    """The same min-ratio under alternative metric definitions (reported, never decisive).
    candidate: {variant: value}; competitors: {name: {variant: value}}."""
    out = {}
    for variant, cv in candidate.items():
        r = {k: v[variant] / cv for k, v in competitors.items() if v.get(variant) is not None and cv}
        if r:
            s = min(r, key=r.get)
            out[variant] = {'R': r[s], 'strongest': s, 'all': r}
    return out
