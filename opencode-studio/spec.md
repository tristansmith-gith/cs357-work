# spec.md — Canvas Snapshot Diff Tool

This specification describes the artifact named by `CHARTER.md` (Definition of
Success). Items not settled by the charter or by the Q&A are tagged with
`[GUESS: ...]`; confirm or correct them before finalizing.

Derived mission (confirmed): a tool that compares two Canvas assignment
snapshots and writes a human-readable report of every change — dates,
descriptions, points, removals — grouped by assignment title.

## Feature summary

- Reads two Canvas assignment snapshots saved as HTML pages.
- Extracts structured assignment data from each snapshot (assignment title,
  due date, description text, point value — see inputs).
- Diffs the two snapshots by assignment title.
- Records: due-date changes, description edits, point adjustments, removed
  assignments, and added assignments.
- Writes a readable `.md` report listing every change, one block per affected
  assignment, headed by the assignment title.
- Reads input files only; never writes to or modifies either snapshot.
- Python 3, standard library only (`html.parser`, `argparse`, `unittest`).

## Entry point

```
python3 artifact/canvas_diff.py OLD_HTML NEW_HTML [-o OUT_MD]
```

- First positional argument = earlier snapshot; second = later snapshot.
  `[GUESS: script filename canvas_diff.py; change if you have a preferred name.]
- Default output path is `artifact/report.md` unless `-o` is given.
  `[GUESS: default filename report.md at the artifact/ path.]`
- Returns per the errors and exit codes section.

## Inputs table

| Name       | Required | Type   | Description                                                        | Origin / note                                     |
|------------|----------|--------|--------------------------------------------------------------------|----------------------------------------------------|
| `OLD_HTML` | yes      | path   | Earlier Canvas snapshot, HTML page(s) saved to disk.               | Supplied by the user as a CLI path; originals live outside the repo. **Read-only, never modified.** |
| `NEW_HTML` | yes      | path   | Later Canvas snapshot, same format as `OLD_HTML`.                  | As above.                                          |
| `-o OUT_MD`| no       | path   | Destination for the report. Defaults to `artifact/report.md`.      | Written fresh or overwritten each run.             |

- A "snapshot" is a directory, or a single HTML file, or a list of HTML files
  captured from the same Canvas course at one moment in time.
  `[GUESS: exact capture layout (one file per assignment vs. one overview
  page) is unknown until a real snapshot exists; the parser will target the
  common "assignment page" structure and be confirmed against a real capture.]`
- Per-change fields extracted from each assignment record: title, due date,
  description, points.
  `[GUESS: exact HTML selectors and the set of fields (e.g. available-until,
  submission type) are inferred from the four change kinds the charter names;
  extend the field list once a real snapshot is inspected.]`

## Outputs

- A single Markdown report (`OUT_MD`), human-readable, containing:
  - A header line stating the two snapshots compared and the run timestamp.
  - A one-line summary: N changed assignments, M removed, K added.
  - One section per changed, removed, or added assignment, headed `## <Title>`.
    For each affected assignment, bullet lines list each change, e.g.:
    `- Due date: Tue Mar 3 → Fri Mar 7` · `- Points: 25 → 30` ·
    `- Description edited` · `- Assignment removed` · `- Assignment added`.
  - When no changes are found: a single "No changes detected." line and a
    clean exit.
- Nothing else is written. The script writes to `OUT_MD` only; it never
  writes to either snapshot.
- `[GUESS: report has no guarantee of byte-stable ordering across runs beyond
  "grouped by assignment title"]`.

## Error behavior and exit codes

| Code | Meaning                                              | When                                          |
|------|------------------------------------------------------|-----------------------------------------------|
| 0    | Success.                                             | Diff completed; report written, changes found or none. |
| 1    | Processing / runtime error.                          | A snapshot exists but cannot be parsed (malformed/unreadable HTML, or an assignment record that cannot be resolved to a title). Message names the failing file. |
| 2    | Usage error.                                         | Missing `OLD_HTML`/`NEW_HTML`, nonexistent input path, bad/unwritable `OUT_MD` path, or an argument that cannot be interpreted. Usage text printed to stderr. |

- A snapshot may not exist → exit 2 (usage), no report file is created.
- A snapshot exists but is unreadable → exit 2. `[GUESS: I split
  "not found" (2) from "found but unparseable" (1); adjust if you want both to
  be 1.]`
- No changes detected → exit 0. The report is still written and states there
  were no changes.

## Testing criteria

Test runner: `python3 -m unittest discover -s artifact/tests`.
`[GUESS: unittest chosen for the stdlib-only constraint; fixtures are small
synthetic HTML files committed under artifact/tests/fixtures/; when a real
snapshot is available, replace fixtures with a sanitized real capture.]`

1. Identical snapshots: run on two copies of the same fixture → exit 0, and
   the report contains "No changes detected." with no per-assignment sections.
2. Single field change: fixture pair differing only in one assignment's point
   value → exit 0, report names the assignment and shows `Points: X → Y`
   (or only the changed field) and nothing else.
3. Removal and addition: fixture pair where one title appears only in the old
   snapshot and another only in the new → exit 0, report contains
   `Assignment removed` for the first and `Assignment added` for the second.
4. Missing input: run with a nonexistent `OLD_HTML` → exit 2, a usage message
   on stderr, and no report file written.
5. Unparseable snapshot: run where one fixture is deliberately malformed HTML
   (no assignment data resolvable) → exit 1, stderr names the failing file,
   and no partial report is written.

Each criterion is automated and runnable via the command above.
`[GUESS: criterion 5's "no partial report written" behavior — the tool writes
the report only after a fully successful parse.]`

## Files the agent may create or modify

- `artifact/canvas_diff.py` — the tool. `[GUESS: filename.]`
- `artifact/report.md` — default output report.
- Anything else under `artifact/`, e.g. `artifact/tests/`, fixture HTML, and
  any helper modules, per the MEMORY rule "artifact/ only".
- This file (`spec.md`) is created once and changed only by deliberate
  amendment, asked-for first.
- `.ai/MEMORY.md` may be appended to per the durable-memory rule when
  findings deserve recording. `[GUESS: MEMORY explicitly names this file's
  append-only rule, so appends do not violate the read-only zone.]`

## Files the agent must NOT touch

- The original Canvas snapshot files, wherever they live: identified as the
  paths passed to the tool, plus any copies or expanded folders under
  `sources/` if a repository copy is ever added. Read-only, never modified.
  (MEMORY.md rule: never modify the original Canvas snapshot files.)
- `CHARTER.md`, `AGENTS.md`, `.ai/` (except the MEMORY append above), `docs/`
  — read-only unless specifically asked.
- `transcripts/` — never edit.
- `opencode.json`, `README.md`, `START_HERE.md` — unchanged unless explicitly
  directed. `[GUESS: no charter/AGENTS rule names these; listed as
  out-of-scope for the artifact.]`