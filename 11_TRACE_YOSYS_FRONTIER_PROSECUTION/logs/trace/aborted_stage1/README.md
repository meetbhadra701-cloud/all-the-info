# Aborted Stage 1 runs (incomplete logs)

These four logs are from single-configuration Stage 1 runs (`evidence/jobs_stage1.csv`). They were still running when Stage 1 was stopped and replaced by the configuration portfolio (see `EXPERIMENTAL_MATRIX.md` §5, trim 1).

- Each log has only its header: FILE, ARGS, TIMEOUT and START. There is no TRACE output and no `### END` marker.
- None of them appears in any results CSV or in `RESULTS.csv`.
- They are kept for completeness only. The same netlists were later run through the portfolio (`pf__*` logs), except the two Family C ones, which are UNSUPPORTED by template.
