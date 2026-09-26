# Upload instructions

Recommended order:

1. Upload `00_START_HERE/MASTER_RESEARCH_HANDOFF.md` first.
2. Upload `05_KILLED_CANDIDATES/RESEARCH_KILL_DATABASE.md` and `06_EXPERIMENTAL_EVIDENCE/EXPERIMENT_INDEX.md`.
3. Upload `09_SOURCE_INVENTORY/SEARCH_COVERAGE.md` and `09_SOURCE_INVENTORY/FILE_MANIFEST.md` so the evidence boundary is explicit.
4. Upload the documents under `01_RESEARCH_OBJECTIVES_AND_STRATEGY/` and `08_IMPORTANT_PROMPTS/`.
5. Upload the Wave 8/9 recovery notes; they explain what was not found locally.
6. Add supporting experiment reports and artifacts from `06_EXPERIMENTAL_EVIDENCE/`, `07_REMAINING_RESEARCH_LEADS/`, and `SUPPORTING_ARTIFACTS/` as upload limits allow.

If you cannot upload everything, the essential set is:

- `MASTER_RESEARCH_HANDOFF.md`
- `RESEARCH_KILL_DATABASE.md`
- `EXPERIMENT_INDEX.md`
- `01_RESEARCH_OBJECTIVES_AND_STRATEGY/PPA_DELTA/Existing-Research-Audit.md`
- `01_RESEARCH_OBJECTIVES_AND_STRATEGY/PPA_DELTA/analysis/`
- `06_EXPERIMENTAL_EVIDENCE/MUXWISE/muxwise-experiment-04/EXPERIMENT_04_REPORT.md`
- `06_EXPERIMENTAL_EVIDENCE/YOSYS_FMA/FINAL_REPORT.md`
- `06_EXPERIMENTAL_EVIDENCE/PASSWITNESS/docs/prior-art.md`
- `06_EXPERIMENTAL_EVIDENCE/PASSWITNESS/docs/limitations.md`
- `07_REMAINING_RESEARCH_LEADS/TRANSCRIPT_DERIVED_LEADS.md`
- `09_SOURCE_INVENTORY/SEARCH_COVERAGE.md`

The ZIP is convenient for transfer, but the individual files should remain available because Claude may need to inspect reports and source artifacts selectively. Do not upload the original Codex backup databases, Desktop `claude backup` credentials, `.venv`, build directories, upstream repositories, or any file outside this package.

Tell Claude that transcript-derived findings are explicitly marked and that missing Wave 8/9 materials must not be reconstructed from guesses. Ask it to use the master handoff as the map, then verify any major claim against the referenced report before proposing new research.
