# Agent Contract

## What this project is
A Canvas Snapshot Diff Tool: compare two Canvas assignment snapshots
(`OLD_HTML`, `NEW_HTML`) and write one human-readable Markdown report of every
change — due dates, description edits, point adjustments, removals, additions —
grouped by assignment title. Built as `artifact/canvas_diff.py`, Python 3,
standard library only.

## Read-first files
Before doing anything else, read, in order: `CHARTER.md`, `spec.md`, then
`.ai/MEMORY.md`. State the project mission in one sentence before proposing any
action. When this file and `CHARTER.md` disagree, the charter wins.

## Zones the agent may and may not edit
- May edit: everything under `artifact/` (the tool, tests, fixtures, reports).
- Read-only, ask before editing: `CHARTER.md`, `AGENTS.md`, `spec.md`, `.ai/`, `docs/`.
- Read-only, never modify: the original Canvas snapshot files — the `OLD_HTML` /
  `NEW_HTML` paths passed to the tool, and any copies placed under `sources/`.
- Never edit: everything under `transcripts/`.

## Confirmation gates
Each gate names an operation and the path it acts on. Operations not listed
here require confirmation before they run (see `opencode.json`).

| Operation | Applies to | Gate |
|---|---|---|
| Edit or create any file, or run `python3 artifact/canvas_diff.py OLD_HTML NEW_HTML [-o OUT_MD]` (writes only to `OUT_MD`) | `artifact/` | Allow, no confirmation |
| Append a dated entry, newest at bottom | `.ai/MEMORY.md` | Allow, no confirmation |
| Run `git pull`, `git add`, `git commit`, `git push`, `git log`, `git change` | this repository | Allow, no confirmation |
| Run `gh auth status` | GitHub, once per session | Allow, no confirmation |
| Run `gh repo create`, `gh repo clone`, `gh issue create`, `gh pr create`, `gh pr review` | GitHub | Ask before running |
| Edit (write or overwrite) | `CHARTER.md`, `AGENTS.md`, `spec.md` | Ask before editing |
| Create or edit any file | under `docs/` | Ask before editing |
| Edit any file other than the `MEMORY.md` append | under `.ai/` | Ask before editing |
| Edit or delete any file | under `transcripts/` | Never, no exception |
| Modify any file | the `OLD_HTML` / `NEW_HTML` inputs, or copies under `sources/` | Never, no exception |

## Durable memory rules
When you learn something a fresh session could not know, append it to
`.ai/MEMORY.md` under a dated heading, newest entry at the bottom. Append only:
never rewrite or delete an existing entry.

## Escalation rule
1. Reach for `gh` first for anything GitHub-side (creating and cloning
   repositories, issues, pull requests, reviews). Confirm once per session with
   `gh auth status`.
2. Fall back to `git` for what it does on its own (pull, add, commit, push,
   log, change). Say in your next message that you fell back, and why.
3. If both fail, stop and ask. A push that prompts for a password, or a 401 or
   403 from either tool, means there is no working credential here. Tell which
   command failed and quote what it said. Do not switch the remote between HTTPS
   and SSH, do not ask to paste a token into a file, and do not retry in a loop.
4. Never ask for a token, key, or password, and never print one in your output.
   If a task needs a secret, stop and say which environment variable should hold
   it, then assume it is set. If you find a credential in a file, do not repeat
   it back: say where it is and that it should be moved and rotated.
5. When a session window, context limit, quota limit, or time limit is
   approaching, stop new work and prepare a clean handoff.