# Codex Execution Manual

You are the implementation and integration owner for PPA-Delta. Execute this manual in the existing user-started Codex session. **NO SUBAGENTS: do all reasoning, coding, research checks and reviews inline. Do not create additional tasks, fork sessions, call model APIs, or delegate through shell commands.** Claude is the separate peer the user starts; you communicate through project files.

This manual is an execution specification, not a claim that the reducer already exists. The supplied working software is the coordination/vault helper. Build the prototype through the tasks below. All shared technical specifications and weekly gates are included later in this manual so it is complete when read alone; live canonical copies are in the vault. Read acknowledged change notes before relying on this initial v1 copy.

## A. Human setup — do this once

1. Keep the entire `PPA-Delta` folder together. Default project path: `C:\Users\meetb\OneDrive\Documents\ChatGPT\ideation\PPA-Delta`.
2. Open/add this exact folder as a local Codex project. Run directly in the saved folder. Do not choose an isolated worktree or cloud checkout for this two-session workflow. If the UI offers different wording, select the option that edits the existing folder.
3. Open Claude Code on the same physical folder and give it `CLAUDE-MANUAL.md`; the other manual contains its own startup prompt. Both sessions may start immediately.
4. In Obsidian, use **Open folder as vault** and choose `C:\Users\meetb\OneDrive\Documents\ChatGPT\ideation\PPA-Delta\Obsidian-Vault`. Open `00-Home`. You do not need to install plugins or type notes.
5. Paste the following message into Codex. You need not paste this entire manual.

```text
Work in C:\Users\meetb\OneDrive\Documents\ChatGPT\ideation\PPA-Delta.
Read AGENTS.md and CODEX-MANUAL.md. You are Codex, the implementation owner.
Claude is running separately in this same directory. Follow file ownership,
task dependencies and all four weekly gates. NO SUBAGENTS: perform every
task inline; do not delegate, fork, start another task or call another model.
Maintain Obsidian-Vault automatically using scripts/control.py and write
evidence after meaningful work. Start C01 and proceed through ready tasks
until the month-one verdict or a genuine blocker. Do not ask me to maintain
notes. Do not start month two, publish, or spend on external services.
```

If this folder is moved, change the first line in both startup prompts to the new shared root. The helper derives paths from its location and the manuals use project-relative paths after startup. Never move only the vault or only one manual.

## B. First ten actions inside the agent

1. Confirm `Get-Location` (PowerShell) or `pwd` (POSIX) matches the shared root. Inspect existing files and Git status without changing branches.
2. Read `AGENTS.md`, `coordination/tasks.json`, the current protocol and weekly gates. State in your first update that you will use no subagents.
3. Inspect project `.codex/config.toml`; it sets `[agents] enabled = false`. Keep that setting. The explicit instruction remains binding even if the installed client cannot apply the configuration. Do not edit the user's global settings.
4. Discover Python, Git, Docker and WSL; record actual versions and availability. Do not install duplicate runtimes. A verified delivery-time Python path is in the shared protocol.
5. Run the helper's status command and read incoming notes. Run `python -m unittest discover -s tests/control -v` to verify the supplied coordination helper before depending on it.
6. Mark C01 IN_PROGRESS. Create `scratch/codex/` and use a body file plus the helper to publish the initial environment note.
7. Choose a single reproducible EDA execution route. Prefer an existing working Linux environment/container with Python 3.11+, Yosys, EQY, a formal solver, and a redistributable library. Do not infer Docker is running merely because its executable exists.
8. Resolve official releases/artifacts once, verify checksums when provided, and freeze the exact versions and library hash. Ask the user only if login, elevation or paid resources are actually necessary. Claude can proceed with source review and corpus design meanwhile.
9. Publish `coordination/runtime.json`: native/WSL/container path mapping, Python command, EDA execution command, working directory, versions, library identity, immutable image digest or package/source checksums, and smoke-test locations. No secret environment values.
10. Continue ready Codex tasks. At a dependency blocker send one local handoff, work another ready task if possible, and otherwise save a resume note. No repeated polling.

## C. Bootstrap details and expected observations

PowerShell discovery commands:

```powershell
Get-Location
Get-Command python,py,git,docker,wsl -ErrorAction SilentlyContinue
docker version
wsl --status
& 'C:\Users\meetb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' --version
```

These inspect the environment; do not interpret a missing command as a failed project. If Docker reports a server error, use an already running WSL/native Linux route or report that the daemon needs starting. Do not change the machine's virtualization configuration silently. If using an existing Python, create a project virtual environment with `<python> -m venv .venv`; then use `.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on POSIX explicitly. Activation is optional and must not be assumed to persist between tool calls.

Use the official OSS CAD Suite build repository for available Yosys/EQY distributions, or a documented source/container build. Pin a dated release or commit plus checksums; never record “latest” as the replay identity. Query the installed tools' help to verify syntax before writing wrappers. Do not download or install OpenROAD for the first area-only experiment unless it is already part of the chosen environment.

Create `pyproject.toml` with an installable `ppa-delta` CLI and test dependencies pinned in a lock mechanism. Avoid runtime calls to any LLM. Install with the chosen interpreter's `-m pip` into the project environment; record the actual commands. Package tests may run on the host while EDA runs in a container, but path mapping and timeouts must be explicit and covered by a smoke test.

Bring up three tiny controls first: equivalent combinational descriptions, an intentionally inequivalent pair, and a pair whose metrics are identical. Expect formal PASS only for the first/third, a failing witness for the second, and NOT_INTERESTING for equal-area designs. None is a qualifying PPA regression until measured.

## D. Week 1 tasks

### C01 — Runtime and environment

Follow the bootstrap steps above. Write frozen toolchain metadata and an environment note with actual outputs. Do not report EDA ready until both synthesis and formal executables run. Record any path quoting issues from spaces in the Windows path. Acceptance: the runtime can execute a tiny real equivalence check and mapped-area measurement; exact invocation is saved. Send Claude a runtime-ready handoff. Mark C01 DONE with evidence.

### C02 — Contracts and package skeleton

Dependencies: C01. Implement the v1 dataclasses/result enums, JSON schema validation, package skeleton and CLI help. Own all shared contract files. Define the `Oracle`, `Budget`, `PairSnapshot`, `Candidate` and generator protocol exactly as specified later in this manual. Publish a minimal fake oracle only inside test fixtures, clearly marked. It is for Claude's isolated generator tests and cannot qualify benchmarks. Send an API-ready handoff with a concrete example and the interface version. Acceptance: schema/contract tests reject missing data and invalid statuses; Claude can code against the documented signatures.

### C03 — Real smoke evaluator

Dependencies: C02. Implement isolated subprocess execution, timeout handling, explicit top/interface checks, formal adapter and mapped-area extraction. Preserve full raw logs. Do not infer proof success only from exit status; check complete PASS evidence for all partitions. Make compile/formal/metric stages separately inspectable. Acceptance: equivalent, inequivalent, equal-area, unsupported and tool-failure controls receive correct distinct statuses. Send Claude the command to evaluate candidate corpus pairs.

### C04 — Validate the first three pairs

Dependencies: C03 and Claude L03. Read Claude's pair manifests; snapshot originals. Run three uncached repetitions of each pair with frozen settings. Check the nonconstant-output guard, mapped-cell coverage, relative and absolute thresholds, provenance and semantic restrictions. Reject invalid pairs with detailed evidence and let Claude replace them; do not change thresholds to rescue them. Acceptance: three qualified pairs with actual logs and a replayable configuration. Then write your Week 1 vote after reviewing Claude's narrow prior-art memo. Claude completes L04 and supplies its own vote.

## E. Week 2 tasks

### C05 — Harden the oracle

Dependencies: C04 and both Week 1 PASS votes. Complete content-addressed caching keyed on all source content, manifests, effective config, tools, library, semantics and predicate parameters. Cache only complete finished records; separate run IDs from reusable content identity. Test timeouts, empty reports, stale files, zero/negative/nonfinite area, unsupported cells, filename injection, source changes during snapshot, config changes and formal UNKNOWN. Acceptance: Claude's adversarial tests cannot produce a false INTERESTING outcome.

### C06 — Simple reduction baselines

Dependencies: C05 and L05. Implement edit-only delta debugging and independent-side reduction using the shared oracle and size counter. Preserve initial and best validated pairs. Support deterministic ordering, explicit budgets, interrupted-run metadata and zero-success behavior. Do not optimize only the new method's cache or give the baseline less candidate space without explaining the comparison. Acceptance: at least one smaller valid witness survives fresh validation, and controlled fixtures check search logic without substituting for real EDA evidence.

### C07 — Export, replay and automatic experiment notes

Dependencies: C06 and L06. Implement the v1 export/replay contract. Every completed or failed evaluator/reducer command must atomically save its result, then call the vault publisher with an accurate summary and links. If publishing fails, preserve the EDA result, return/report the documentation failure and retry publication separately; never rerun an expensive experiment merely to recreate a note. Include `--agent` or equivalent execution metadata to direct notes to the correct lane. Acceptance: clean-directory replay works with originals/caches unavailable, and an actual run automatically appears in the vault. Review L07 and cast your Week 2 vote.

## F. Week 3 tasks

### C08 — Fair comparison harness

Dependencies: C07 and both Week 2 PASS votes. Implement method registration and a benchmark harness using the frozen schema. Read Claude's interface handoff before wiring the generator. Support unreduced, edit-only, independent and coupled methods with identical budgets and starting snapshots. Save all per-case rows before computing summaries. Test that timeout/failure/no-gain cases remain in denominators. Publish the harness invocation for Claude.

### C09 — Integrate the coupled reducer

Dependencies: C08 and L09. Review Claude's code inline for I/O contract, oracle access, unsupported cases, size counting, termination and immutable snapshots. Send fixes to Claude instead of modifying its directory. Wire the public CLI and run integration tests after the owner resolves problems. Acceptance: the same input can be processed by all methods without modifying corpus files or shared configuration.

### C10 — Week 3 fairness audit

Dependencies: C09 and L10. Check development comparison/ablation results, budgets, source hashes, final validation and failure accounting. Verify at least two claimed benefits by clean rerun. Inspect whether improvements arise from structure-aware proposals or accidental baseline disadvantages. Acceptance: a specific pass/revise/stop memo supported by raw rows; cast the Week 3 vote. Do not tune Claude's reducer or extend the corpus to hide weak cases.

## G. Week 4 tasks

### C11 — Frozen ten-pair comparison

Dependencies: C10, L11 and both Week 3 PASS votes. Hash the suite before running. Run the complete method matrix with fresh per-method caches and frozen budgets. Record elapsed time and all proposal/tool calls. Do not change held-out cases, limits or rules while running. Acceptance: complete machine-readable rows for all ten qualifying pairs and all methods, including failed/unknown/no-gain outcomes.

### C12 — Clean replay and release candidate

Dependencies: C11 and L12. Package a local release candidate with real examples, install/doctor commands, supported-subset documentation, usage, limitation and license/provenance notes. Run final uncached validations and clean-directory replays. If one fails, invalidate that result and have Claude recompute analysis. Draft a CI job that runs bounded controls and a separately selectable EDA suite. Do not publish or contact anyone. Acceptance: ten-pair accounting is complete, all claimed witnesses verified, and a stranger could follow the README without hidden local paths.

### C13 — Final decision packet

Dependencies: C12 and L13. Verify Claude's analysis and relevance assessment against raw artifacts. Produce a concise month-one memo: novelty delta, metrics, baselines, held-out behavior, cost, failure cases, replay status, practical relevance, external evidence actually obtained, and CONTINUE proposal / REVISE / STOP. Record your Week 4 vote. If both pass, outline month two without beginning it. Deliver the local prototype path, replay example, vault decision links and any genuine user decision needed.

## H. Every task's completion checklist

- File ownership respected; no subagents or hidden model calls used.
- Tests cover the actual changed behavior; real EDA claims use real tool output.
- Corpus originals and old evidence preserved; configurations hashed.
- Current task acceptance criteria met; dependent peer handoff delivered if needed.
- Vault note includes observations, failures, artifact paths and next step.
- `control.py task ... DONE --evidence ...` succeeds only after the above.

## I. Resume prompt for an idle or restarted Codex session

```text
Resume PPA-Delta in the same local project folder. Read AGENTS.md, your
latest journal, Project-Status.md and unread handoffs. Do not restart the
research or overwrite Claude's work. No subagents, new sessions or model
API calls. Continue the next ready Codex task, maintain the Obsidian vault,
and respect the weekly gates and the month-one stopping boundary.
```

The user may send this after a session ends. Do not create a watcher that keeps models running, and do not ask the user to copy information between the vault and agent chats.
