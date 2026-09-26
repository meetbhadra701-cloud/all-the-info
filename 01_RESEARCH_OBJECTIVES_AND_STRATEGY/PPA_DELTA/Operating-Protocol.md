# Two-Session Operating Protocol

## Strict no-subagents rule

**NO SUBAGENTS. ALL MODEL WORK MUST BE DONE INLINE IN THE CURRENT SESSION.** There are exactly two user-started peers: one Codex session and one Claude session. Neither may spawn, delegate to, fork, message into a new model session, launch an agent team, call an agent SDK, invoke another AI through shell/API, or use a skill/command that internally creates agents. Do not call Explore, Plan or review subagents. Do not use `/init` workflows that delegate. Ordinary Python, compilers, solvers and tests are allowed; they are not model agents. The two peers communicate through local files only.

This is an explicit user cost constraint. Do not override it to finish sooner or improve coverage. Do not start additional tasks on the user's behalf. If a tool exposes delegation despite the project configuration, do not invoke it. Read this rule again after compaction/restart.

## Shared directory and ownership

Project root is the folder containing `CODEX-MANUAL.md`, `CLAUDE-MANUAL.md` and `coordination/tasks.json`. Default location is `C:\Users\meetb\OneDrive\Documents\ChatGPT\ideation\PPA-Delta`. Both agents must operate on this SAME physical folder, not different worktrees, uploads, remote clones, or independently synchronized machines. The vault is exactly `<project-root>/Obsidian-Vault`.

The Windows folder and its WSL `/mnt/c/...` view are one physical tree. Record the mapping in `coordination/runtime.json` before mixing shells. OneDrive is not a distributed lock: do not operate from two computers through sync. Within this machine use the local coordination helper. Never move the working project while agents are active.

| Owner | Exclusive writable paths |
|---|---|
| Codex | `src/ppa_delta/contracts.py`, `src/ppa_delta/__init__.py`, `src/ppa_delta/cli.py`, `src/ppa_delta/oracle/`, `src/ppa_delta/baselines/`, `src/ppa_delta/reporting/`, `src/ppa_delta/replay/`, `tests/codex/`, `tests/control/`, `scripts/`, `configs/`, `schemas/`, `pyproject.toml`, dependency lock files, `.github/`, build/runtime config, root release docs |
| Claude | `src/ppa_delta/coupled/`, `tests/claude/`, `benchmarks/`, `research/`, `analysis/`, `docs/claude/` |
| Each agent | Its own `runs/<agent>/`, `scratch/<agent>/`, and vault notes under the matching `<agent>` subfolder |
| Helper only | `coordination/state.json`, `coordination/messages/`, `coordination/acks/`, `Obsidian-Vault/Project-Status.md` |
| Codex, with explicit Claude acknowledgement for semantic changes | Shared schemas, task definitions, technical contract, weekly gates, ownership map, integration/release files and frozen runtime |

Claude may review every file and request changes, but does not edit Codex's implementation. Codex may review Claude's reducer and corpus, but does not silently fix them. Write a handoff describing the exact file, finding and expected behavior. The owner fixes and tests it inline. New paths must be assigned before work begins. Shared specification edits require an acknowledged proposal; purely correcting a broken link or typo may be done by Codex with a logged note.

Do not recursively format, rename, clean or restore the whole repository. Restrict tools to owned paths. Do not overwrite the other agent's work or change branches/worktrees while both are active. Git inspection is allowed. Codex alone may make local checkpoint commits after obtaining a quiescent acknowledgement from Claude; stage explicit paths, inspect staged diff, and never use `git add .`, `commit -a`, `reset --hard`, `clean`, force push or history rewrite. Git operations may target an ancestor repository; inspect `git rev-parse --show-toplevel` and remain within this project. Do not create a nested Git repository automatically. No remote publishing without explicit user authorization.

## Startup for every session

1. Confirm your identity is Codex or Claude and the current directory is the project root. Read root `AGENTS.md` and, for Claude, `CLAUDE.md`.
2. Read your manual's role playbook once. On later turns read only the current task section, this protocol, latest gate notes and changed contracts; do not reread the entire research archive.
3. Verify no-subagent settings and obey the instruction even if a client cannot enforce the setting. No global configuration changes.
4. Locate Python 3.11 or newer. Use an existing interpreter; do not assume `python` or `py` is on PATH. On this machine a verified interpreter at delivery time is `C:\Users\meetb\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`. Do not hardcode that path into product replay bundles. If unavailable, Codex owns installing/configuring Python; Claude writes initial Markdown notes directly in its own journal folder while waiting.
5. Run `python scripts/control.py status --agent codex` or `--agent claude` using the discovered interpreter. Read unread handoffs. Acknowledge only after reading the linked note with `ack --agent <you> --id <message-id>`.
6. Read `coordination/tasks.json`. Select a ready task in your lane. If one is already IN_PROGRESS, resume it before starting another. No more than one active implementation task per agent.
7. Mark it IN_PROGRESS with a brief objective. Perform the task inline; verify its acceptance conditions; publish a real evidence note; then mark DONE with evidence file paths.
8. Before every final response, refresh your status and write what changed, tests performed, remaining uncertainty, and the exact next step. The user must never be asked to manually maintain the vault.

## Automatic vault updates

The vault is a local Markdown knowledge base. It requires no community plugin, Obsidian API key, AI subscription or background daemon. Obsidian can remain open while agents create notes. The agents are responsible for calling the helper after meaningful work; the helper creates the notes and dashboard. It does not write while both sessions are stopped and does not invent experiment summaries.

Use `scripts/control.py` for task state, votes, notes and handoffs. Status/task/gate/note commands regenerate `Project-Status.md` under a short filesystem lock. Notes have unique names including agent identity, timestamp and random ID. No shared append-only Markdown file is edited by both agents.

Mandatory update triggers: session start/end; task start/completion/blocker; new relevant source; accepted/rejected benchmark; completed or failed experiment; changed scientific assumption; API handoff; weekly gate vote; external recognition/adoption when it actually occurs. Do not record every thought or every tool call. Keep raw logs outside the vault and link to their project-relative paths; vault summaries contain results, not megabytes of console output.

Always label information as OBSERVED, PLANNED, HYPOTHESIS or EXTERNAL-REPORT. Every experiment note includes pair IDs, source/config/toolchain hashes, command, budget, before/after values, proof status, failures, artifact paths, interpretation and next action. An internal agent review is not independent third-party validation.

### Commands that work now

Replace `python` below with your discovered interpreter. Run from project root. The examples show Codex; Claude substitutes its name and task IDs. Agents write the body file themselves; the user does not.

```text
python scripts/control.py status --agent codex
python scripts/control.py task --agent codex --id C01 --status IN_PROGRESS --summary "Verify runtime and toolchain"
python scripts/control.py note --agent codex --kind journal --title "Runtime discovery" --body-file scratch/codex/runtime-note.md
python scripts/control.py note --agent codex --kind handoff --title "Evaluator v1 is ready" --body-file scratch/codex/handoff.md --to claude
python scripts/control.py task --agent codex --id C01 --status DONE --summary "Runtime verified; see evidence" --evidence scratch/codex/runtime-note.md
python scripts/control.py gate --agent codex --week 1 --decision PASS --summary "Gate evidence verified" --evidence scratch/codex/week-1-gate.md
```

These are usage examples, not instructions to claim C01 complete or vote PASS before evidence exists. A body file and any evidence path must already exist inside the project. Prefer attaching the immutable vault note path returned by `note`, plus the actual machine-readable report. Acknowledgements acknowledge receipt, not correctness or consent to unrelated changes.

`status` displays ready tasks, current task states, combined gate results and unread messages. A note containing a handoff request must name requested action, file/interface version, supporting evidence, recipient, and whether it blocks work. The recipient replies with its own handoff note and acknowledges the original. Neither agent calls a tool to send messages externally or starts another model session.

## Dependencies without wasting usage

Read the inbox before starting a work chunk and after a completed task. Do not repeatedly poll an unchanged file, repeatedly call the other agent, or run sleep loops. If blocked, mark BLOCKED and send one handoff. Continue a different ready task if available. If nothing is ready, save a resume note and finish the turn. Files do not automatically wake an idle agent; the user may need to send the included resume prompt. This is the only possible manual coordination beyond opening the sessions; no manual vault entry is required.

Do not rescan broad EDA literature. Claude owns the focused Week 1 search, starting with the existing audit. Read only sources needed to resolve the reducer question. Codex reviews that evidence instead of independently repeating the search. Reuse cached measurements only when complete identities match; use uncached runs where validation requires them. No model calls inside the reducer, evaluator, tests or helper.

## Gates, disagreement and recovery

Both agents independently write their weekly evidence memo and record their own vote. Combined PASS requires both PASS. Missing evidence is PENDING/REVISE. Either STOP is binding for new development; explain the precise reason to the user. No automatic month-two work.

If a DONE task later proves defective, preserve its historical completion. File an issue, set the affected week's vote to REVISE, perform a bounded fix in the same owned paths, retest the dependent evidence, and write a correction note. Codex may add a repair task to the manifest after Claude acknowledges it. Do not retroactively erase failures or quietly revise the thresholds. A STOP is latched by the helper; only explicit user direction authorizes Codex to prepare a logged restart with a new decision record and preserved old state.

The control lock protects only short metadata writes. Never hold it during builds, searches or experiments. If a crash leaves `.control-lock`, identify the PID/time in `owner.json` and verify the process is not running and no second helper is active before Codex removes only that exact stale lock directory. Never steal a lock because a timeout elapsed. Regenerate status afterward and compare state to the newest notes for any interrupted transaction.

If a client starts in a different clone or a cloud sandbox, stop editing, record the location mismatch, and ask for the shared local project to be opened. Do not maintain two independent vaults and promise they will merge later.

## Boundaries for user involvement

Proceed with authorized local engineering, tests, notes and reversible fixes without repeatedly asking permission. Report only real access blockers, necessary login/elevation prompts, an explicit stop decision, public-release/disclosure decisions, or a proposed scope change after the month-one verdict. Do not schedule paid jobs, create subscriptions or incur unapproved external spending. Device capability is not used as a reason to dilute the specification; choose reproducible environments and fair test budgets.
