# Project Memory

Append-only. Newest entries at the bottom. Each entry is dated and names what
a session that has never seen this project would need to know.

1. What is the artifact?          automation
2. Who is it for?                 me next month 
3. What may the agent touch?      artifact/ only
4. What is done, today?           it runs and one check passes
5. What must never happen?        The agent must never modify the original Canvas snapshot files.

## 2026-09-23 — Rubric exists; scope decisions pending
A testing rubric was created at artifact/rubric.md and artifact/rubric.json from
spec.md + system_prompt.txt only (18 criteria TC-01..TC-18, 9 prohibitions
PR-01..PR-09; weights sum 100; threshold 0.80; material rows fail outright).
Seven spec.md items are GUESS/too-vague and await user decisions before the
rubric and canvas_diff.py are final: (1) HTML capture layout/selectors,
(2) snapshot input forms (directory/file/list), (3) exit 1 vs 2 for an
existing-but-unreadable snapshot (spec.md:76 vs 80), (4) "no partial report"
behavior, (5) meaning of "human-readable" beyond the pinned header/summary/
sections, (6) section ordering beyond "grouped by title",
(7) whether the four fields (title, due date, description, points) are final scope.

## 2026-09-23 — All 7 spec decisions resolved; rubric updated (TC-19/TC-20 added)
Decisions D1-D7 are recorded in artifact/rubric.md: snapshots = real Canvas page
captures under snapshots/ (offline tool); one HTML file per positional (previous,
current); open/read failure → exit 2, readable-but-unparseable → exit 1; no
partial report; human-readable = pinned header/summary/sections/bullets; sections
sorted alphabetically by title; four fields final (title, due date, description,
points). rubric.json rebalanced to 29 rows, TC total 80 + PR 20 = 100.
OPEN ITEM found while inspecting: snapshots/Canvas_y26M09d23h21m04s59.html is
the Canvas DASHBOARD page (<title>Dashboard</title>), NOT the Assignments index
page. It has assignment To-Do items (title/points/status), recent-feedback
links, and "Due Date Changed" stream rows, but ZERO description text and no full
assignment list. The description field selectors cannot be pinned from this
file. A capture of /courses/<id>/assignments or individual assignment pages is
still needed before TC-11 and the parser can be finalized. Do not modify the
file under snapshots/.

## 2026-09-23 — D8: proof-of-concept scope, dashboard blockers resolved
User decision (recorded in artifact/rubric.md): ignore assignment descriptions
and ignore that a capture is not a full assignment list — this is a
proof-of-concept. Parser targets whatever assignments the Dashboard capture
renders (title, due date, points where present); no Description edited bullet
is produced. Selectors to pin: .ToDoSidebarItem__Title (title), the points
<li> ("N points") inside the To-Do item, dash dates where shown, stream
items. rubric.md TC-07/TC-10/TC-11 updated; rubric.json decisions object has
D1..D8. The Dashboard capture stays unmodified under snapshots/.

## 2026-09-24 — canvas_diff.py implemented; D9 rejects the stream fallback
artifact/canvas_diff.py (Python 3, stdlib only: html.parser, re, argparse)
is implemented and all 13 unittest cases pass via
`python3 -m unittest discover -s artifact/tests`. Parser is To-Do-only:
a record is one `.ToDoSidebarItem` whose anchor aria-label is
"Assignment, <Title>"; due date and points come from the <li> texts of
[data-testid=ToDoSidebarItem__InformationRow] ("N points", "Sep 24 at
11:59pm"); statuses like "Closed" mean that field is "not shown"; non-
assignment slugs (Announcement/Calendar Event) are ignored; duplicate
titles across the ~13x-self-duplicated real capture dedupe, first wins.
D9 (recorded in artifact/rubric.md + rubric.json, and CURRENT_TASK.md Q2):
the activity-stream fallback is REJECTED on charter value #1 (Correctness
over speed) — a "Due Date Changed" row carries the change timestamp, not the
due date or points, so stream records could only no-op, falsely "Assignment
removed" (rolling stream window), or mislabel "Assignment added". Report:
header (both paths + timestamp), "Summary: N changed, M removed, K added.",
alphabetical ## <Title> sections with "Due date: A → B" / "Points: X → Y" /
removed / added bullets, "No changes detected." when empty. Exits: 0 success,
1 reads-but-unparseable (failing file on stderr, no report), 2 usage/not-
found/unreadable/unwritable OUT_MD (usage on stderr). Smoke run: the real
capture as both OLD and NEW yields exit 0 and "No changes detected.", snapshot
hash unchanged. Real-capture parser test pins the 3 To-Do titles (Lab:
OpenCode Studio, Homework 3, Writing as Thinking - Week 5) — skipped if the
capture is absent.
