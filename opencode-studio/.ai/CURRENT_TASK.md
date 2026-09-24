# Current Task

## Active Subtask

Implement the full Canvas Snapshot Diff Tool as a proof of concept per
spec.md + rubric decisions D1-D8: `artifact/canvas_diff.py` (Python 3,
standard library only: `html.parser`, `argparse`, `unittest`) plus a unittest
suite and synthetic fixtures under `artifact/tests/`.

Scope decisions from the 2026-09-23 interview (D1-D8 context):

- Snapshots are real Canvas page captures under `snapshots/`, one HTML file
  per positional argument (previous, current); the tool is offline.
- Exit codes: not found / unreadable input or bad `OUT_MD` -> 2; exists but
  unparseable -> 1; success -> 0. Report is written only after a fully
  successful parse (never partial).
- Human-readable report = pinned header (two snapshots + run timestamp),
  one-line summary (N changed / M removed / K added), one `## <Title>`
  section per affected assignment with bullet lines; a single "No changes
  detected." line when nothing changed. Sections sorted alphabetically by
  title. Fields are the four the charter names: title, due date, description,
  points.
- D8 (proof-of-concept): assignment descriptions are ignored; no "Description
  edited" bullet is produced. The parser targets whatever the Dashboard
  capture renders.
- Q2: diffable assignment records come from To-Do sidebar items
  (`.ToDoSidebarItem` + `aria-label="Assignment, <Title>"` for title, the
  points `<li>` ("N points"), dash dates where shown). **Amended 2026-09-24
  (D9): the activity-stream-row fallback is REJECTED.** An "Assignment Due
  Date Changed" row carries the change timestamp, not the assignment's due
  date or points, so stream-derived records could only no-op, falsely read as
  `Assignment removed` (rolling stream window), or mislabel `Assignment added`.
  Rationale: charter value #1, Correctness over speed. The parser is To-Do-only;
  stream rows are never parsed into records.
- Q3: test fixtures are synthetic HTML modeled on the real Dashboard layout
  (To-Do sidebar, points `<li>`, dash dates, stream rows), sanitized for
  size, plus a deliberately malformed fixture for the exit-1 test. The real
  capture under `snapshots/` is never modified.
- Q4: a field the Dashboard does not render is shown as "not shown";
  missing~missing across the two snapshots is no change; shown->missing (or
  reverse) is reported as a change.
- Q5: after the suite passes, smoke-run the real tool with the real capture
  as BOTH OLD_HTML and NEW_HTML, expecting exit 0 and a "No changes detected."
  report.

## Completion Criteria

1. `artifact/canvas_diff.py` exists and is runnable via
   `python3 artifact/canvas_diff.py OLD_HTML NEW_HTML [-o OUT_MD]`.
2. Parser extracts, per assignment record: title (required), due date, points
   (where present), from the Dashboard To-Do + stream structure.
3. Diff by title produces bullets only for: due-date changes, point
   adjustments, assignment removed, assignment added. No description bullets.
4. Report matches the pinned D6 structure (header, summary, alphabetical
   `## <Title>` sections, bullets, "No changes detected." when empty); nothing
   else is written to disk except `OUT_MD`.
5. Exit codes honored: 0 success (changes or not); 1 exists-but-unparseable
   with the failing file named on stderr and no partial report; 2 usage/not-
   found/unwritable-path with usage text on stderr.
6. unittest suite passes: `python3 -m unittest discover -s artifact/tests`
   covering identical snapshots, single-field point change, removal + addition,
   missing input (exit 2, no report), malformed HTML (exit 1, no partial
   report).
7. Fixtures under `artifact/tests/fixtures/` are synthetic and Dashboard-
   modeled; the real snapshot under `snapshots/` is unmodified.
8. Smoke run: the real capture passed as both OLD and NEW yields exit 0 and a
   report containing "No changes detected."; script never writes to the
   snapshot.