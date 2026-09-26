#!/usr/bin/env python3
"""Reconcile prior manifests with their actual solver output."""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP2 = ROOT.parent / "muxwise-experiment-02"
EXP3 = ROOT.parent / "muxwise-experiment-03"

def log_verdict(text: str) -> str:
    if "SAT proof finished - no model found: SUCCESS!" in text or "Equivalence successfully proven!" in text:
        return "PASS"
    if "SAT proof finished - model found: FAIL!" in text:
        return "FAIL"
    if "ERROR:" in text:
        return "INCONCLUSIVE_SETUP_OR_ERROR"
    if "TIMEOUT" in text or "interrupted" in text.lower():
        return "INCONCLUSIVE_TIMEOUT_OR_INTERRUPTED"
    return "NO_COMPLETION_FOUND"

def main() -> None:
    rows = []
    manifest = EXP2 / "results" / "formal_manifest.csv"
    with manifest.open() as f:
        for r in csv.DictReader(f):
            path = EXP2 / r["log"]
            text = path.read_text(errors="replace") if path.exists() else ""
            rows.append({"experiment": "02", "name": r["name"], "manifest_outcome": r["outcome"],
                         "process_returncode": r["returncode"], "observed_log_verdict": log_verdict(text),
                         "log": str(path.relative_to(ROOT.parent.parent)) if path.exists() else r["log"]})
    comp = EXP3 / "results" / "formal_comparison.csv"
    with comp.open() as f:
        for r in csv.DictReader(f):
            path = EXP3 / r["evidence_log"] if r.get("evidence_log") else None
            text = path.read_text(errors="replace") if path and path.exists() else ""
            rows.append({"experiment": "03", "name": f"{r['design']}_w{r['width']}_{r['config']}",
                         "manifest_outcome": r["result"], "process_returncode": "",
                         "observed_log_verdict": log_verdict(text) if path else "NOT_EXECUTED",
                         "log": str(path.relative_to(ROOT.parent.parent)) if path and path.exists() else (r.get("evidence_log") or "")})
    out = ROOT / "audit" / "formal_reconciliation.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for exp in ("02", "03"):
        split = ROOT / "audit" / f"experiment_{exp}_formal_audit.csv"
        with split.open("w", newline="") as f:
            subset = [r for r in rows if r["experiment"] == exp]
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(subset)
    print(f"wrote {out} ({len(rows)} rows)")
    for r in rows:
        if r["manifest_outcome"] != r["observed_log_verdict"]:
            print("MISMATCH", r["experiment"], r["name"], r["manifest_outcome"], "->", r["observed_log_verdict"])

if __name__ == "__main__":
    main()
