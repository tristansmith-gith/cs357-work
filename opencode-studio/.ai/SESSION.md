# Session Log

Append-only session journal. Newest entries at the bottom. Each dated entry:
Scope, Completed, what was deliberately not done, Validation, and exactly one
Next Safe Action. Append only: never rewrite or delete an existing entry.

## 2026-09-24 — Implement spec.md proof of concept (canvas_diff.py)

- **Scope:** Implement the Canvas Snapshot Diff Tool per spec.md + rubric
  decisions D1-D8 (D9 added this session): `artifact/canvas_diff.py`
  (Python 3, stdlib only), a unittest suite, and synthetic fixtures under
  `artifact/tests/`.
- **Completed:** To-Do-only Dashboard parser (title via `aria-label`,
  due date and points from the info-row `<li>`s); title-keyed diff; pinned
  Markdown report (header, summary, alphabetical sections, no-changes line);
  exit codes 0/1/2 with a no-partial-report guarantee; D9 recorded
  (activity-stream fallback rejected on Correctness over speed);
  `rubric.md`/`rubric.json` amended (D9, TC-11 reworded to To-Do scope);
  `CURRENT_TASK.md` Q2 amended; MEMORY.md entries appended; commit `72d3fc1`.
- **Deliberately did not do:** stream-fallback parsing (rejected, D9);
  `Description edited` bullets (D8, out of POC scope); any edit to the
  read-only files (`CHARTER.md`, `AGENTS.md`, `spec.md`, `docs/`,
  `transcripts/`, `snapshots/`, `opencode.json`, `README.md`,
  `START_HERE.md`); no deletion or cleanup of the untracked
  `artifact/__pycache__/` build residue.
- **Validation:** `python3 -m unittest discover -s artifact/tests` → 13/13 OK
  (includes a real-capture pinning test for the 3 To-Do titles, skipped if
  `snapshots/` is absent); `python3 -m py_compile artifact/canvas_diff.py` OK;
  smoke run of the real capture as both OLD and NEW → exit 0 with
  "No changes detected." and the snapshot's shasum unchanged before/after.
- **Next Safe Action:** clean up the loose end only — with the user's OK,
  delete the untracked `artifact/__pycache__/` residue or add `__pycache__`
  to `.gitignore`; the implementation task itself is complete and requires
  no further code work.

## 2026-09-24 — Cold-start kickoff: state reconciliation + residue cleanup

- **Scope:** Boot a fresh session via KICKOFF_PROMPT.txt: read the docs in
  order, report mission/current-task/repo-state, and take the next safe
  action. No feature work.
- **Completed:** Verified state against fresh git/test output (not memory).
  Found the docs' "fully committed" claim was wrong: `.ai/SESSION.md`,
  `docs/DECISION_LOG.md`, the MEMORY session-wrap append, the `START_HERE.md`
  entry-funnel content, the expanded 20-case test suite, and the new
  `dashboard_to_do.html` fixture were all uncommitted. With the user's OK:
  added `__pycache__/` + `*.pyc` to `.gitignore` and untracked the two
  bytecode files committed by the junk commit `bcd7fde` (commit `2724883`).
  A concurrent user process committed the swept-up handoff state as
  `4878873 "part 6 in progress"` (the four course files got included there
  despite the "handoff-only" choice — my UI choice was overridden by that
  process; nothing reverted).
- **Deliberately did not do:** create the missing `docs/ROADMAP.md` (docs/ is
  ask-gated); push the 2 unpushed commits (`4878873`, `2724883`); re-open the
  stream-fallback question (D9 stands); any code change to `canvas_diff.py`.
- **Validation:** `python3 -m unittest discover -s artifact/tests` → 20/20 OK
  at HEAD; smoke run (real capture as both OLD and NEW) → exit 0 with
  "No changes detected."; snapshot shasum `503cfe1…` unchanged; working tree
  clean at session end.
- **Next Safe Action:** with docs/ permission, create `docs/ROADMAP.md`
  (milestone status board) so the read order in START_HERE.md:3 and the
  kickoff matches reality; then optionally push the unpushed commits.