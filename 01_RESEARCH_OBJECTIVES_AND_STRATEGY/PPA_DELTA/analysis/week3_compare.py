"""L10 analysis: read the frozen comparison's machine-readable rows and compute the Week-3 gate
check + ablation, from artifacts only (never agent recollection).

Usage: python analysis/week3_compare.py runs/claude/l10-compare-XXance/comparison.json
Writes analysis/week3-comparison.md and prints the verdict. Deterministic; rerunnable.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METHODS = ["unreduced", "edit-only", "independent", "bugpoint", "coupled", "coupled-no-matching"]
BASELINES = ["edit-only", "independent"]  # the "simple" baselines the gate compares against
GATE_FRACTION = 0.20


def _pair_ast(size):
    return size["before_ast"] + size["after_ast"]


def load_rows(comparison_json: Path):
    data = json.loads(comparison_json.read_text())
    rows = []
    for rel in data["rows"]:
        rows.append(json.loads((ROOT / rel).read_text()))
    return rows


def build(rows):
    table = {}  # (pair, method) -> row
    pairs = []
    for r in rows:
        table[(r["pair_id"], r["method"])] = r
        if r["pair_id"] not in pairs:
            pairs.append(r["pair_id"])
    return table, pairs


def main():
    comparison_json = Path(sys.argv[1]).resolve()
    rows = load_rows(comparison_json)
    table, pairs = build(rows)

    lines = ["# L10 — Week-3 frozen comparison and ablation", "",
             f"Source: `{comparison_json.relative_to(ROOT).as_posix()}` · classification: OBSERVED (real EDA).",
             "All methods share one starting snapshot, the frozen 200/1800 budget, cache disabled.", "",
             "## Final pair-AST by method (lower is better)", "",
             "| pair | " + " | ".join(METHODS) + " |",
             "|---|" + "---|" * len(METHODS)]
    valid_counts = {m: 0 for m in METHODS}
    per_pair = {}
    for pid in pairs:
        cells = []
        for m in METHODS:
            r = table.get((pid, m))
            if r is None:
                cells.append("—"); continue
            pa = _pair_ast(r["final_size"])
            valid_counts[m] += int(r["valid_witness"])
            mark = "" if r["valid_witness"] else "✗"
            cells.append(f"{pa}{mark}")
        per_pair[pid] = {m: (_pair_ast(table[(pid, m)]["final_size"]) if (pid, m) in table else None)
                         for m in METHODS}
        lines.append(f"| {pid} | " + " | ".join(cells) + " |")

    lines += ["", "✗ = not a valid witness. Valid-export counts: "
              + ", ".join(f"{m}={valid_counts[m]}" for m in METHODS), ""]

    # Gate check: coupled >= 20% fewer than the better simple baseline, on >= 2 pairs.
    lines += ["## Gate check — coupled vs the better simple baseline", "",
              "| pair | better baseline (edit-only/independent) | coupled | reduction vs baseline | ≥20%? |",
              "|---|---|---|---|---|"]
    passing = 0
    for pid in pairs:
        base = min((per_pair[pid][b] for b in BASELINES if per_pair[pid][b] is not None), default=None)
        coup = per_pair[pid]["coupled"]
        if base is None or coup is None:
            lines.append(f"| {pid} | n/a | {coup} | n/a | — |"); continue
        frac = (base - coup) / base if base else 0.0
        ok = frac >= GATE_FRACTION
        passing += int(ok)
        lines.append(f"| {pid} | {base} | {coup} | {frac*100:.1f}% | {'YES' if ok else 'no'} |")

    # Ablation: coupled vs coupled-no-matching (isolates structural matching).
    lines += ["", "## Ablation — structural matching effect (coupled vs coupled-no-matching)", "",
              "| pair | coupled | no-matching | matching effect |", "|---|---|---|---|"]
    matching_helps = 0
    for pid in pairs:
        c, nm = per_pair[pid]["coupled"], per_pair[pid]["coupled-no-matching"]
        if c is None or nm is None:
            lines.append(f"| {pid} | {c} | {nm} | n/a |"); continue
        delta = nm - c
        matching_helps += int(delta > 0)
        lines.append(f"| {pid} | {c} | {nm} | {'+' if delta>0 else ''}{delta} nodes |")

    coupled_valid = valid_counts["coupled"]
    baseline_valid = max(valid_counts["edit-only"], valid_counts["independent"])
    verdict = {
        "pairs": pairs,
        "coupled_beats_baseline_20pct_on": passing,
        "gate_20pct_met": passing >= 2,
        "coupled_valid_not_lower": coupled_valid >= baseline_valid,
        "matching_helps_on_pairs": matching_helps,
        "recommendation": ("PASS" if passing >= 2 and coupled_valid >= baseline_valid else "REVISE_OR_STOP"),
    }
    lines += ["", "## Verdict (machine-readable)", "", "```json", json.dumps(verdict, indent=2), "```", ""]

    out = ROOT / "analysis" / "week3-comparison.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(verdict, indent=2))
    print(f"\nWrote {out.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
