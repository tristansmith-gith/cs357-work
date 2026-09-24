# Rubric — Canvas Snapshot Diff Tool

Mission: a tool that compares two Canvas assignment snapshots and writes one
human-readable Markdown report of every change — due dates, description edits,
point adjustments, removals, additions — grouped by assignment title.

Every criterion below is drawn verbatim from `spec.md` or `system_prompt.txt`;
criteria added at TC-19/TC-20 and the clarifications applied to TC-11/TC-12/TC-13
come from the 2026-09-23 decisions (see [Decisions](#decisions)), which resolve
the spec's `[GUESS]` tags. Nothing is invented. Source references name the file
and lines where the requirement appears.

Scoring: each row has a weight (see `rubric.json`; weights sum to 100), a
Meets / Approaching / Does not meet rating, and a Material flag. A "Does not
meet" on a **Material** row fails the whole rubric regardless of score. The
overall pass requires a weighted score of at least **0.80** and no Material
failure.

## Testing criteria

| ID | Criterion (source) | Meets | Approaching | Does not meet | Material | How to verify |
|---|---|---|---|---|---|---|
| TC-01 | Identical snapshots: two copies of the same fixture produce exit 0, report contains `No changes detected.` with no per-assignment sections. (spec.md:93-94; 64-65; 83-84) | Exit 0; report has exactly the no-changes line and zero `## <Title>` sections. | Exit 0 and the phrase present, but the report carries extra content (stray section, blank lines beyond formatting). | Exit != 0, phrase absent, or any per-assignment section present. | Yes | `python3 -m unittest discover -s artifact/tests` criterion 1; or run the CLI on two identical fixtures and assert exit code + `grep` the report. |
| TC-02 | Single field change: fixture pair differing only in one assignment's point value → exit 0; report names the assignment and shows `Points: X → Y` and nothing else. (spec.md:95-97) | Exit 0; the assignment is named; `Points: X → Y` appears; no other change is reported. | Points change reported correctly plus harmless extra lines (e.g., header/summary that are section-agnostic). | Exit != 0, wrong/missing assignment name, or no `Points: X → Y` line. | Yes | unittest criterion 2. |
| TC-03 | Removal and addition: one title only in the old snapshot → `Assignment removed`; one title only in the new snapshot → `Assignment added`. (spec.md:98-100) | Exit 0; removed title marked `Assignment removed`; added title marked `Assignment added`. | Both detected but one label swapped, or one detected and the other missed. | Neither marked, or exit != 0. | Yes | unittest criterion 3. |
| TC-04 | Missing input: nonexistent `OLD_HTML` → exit 2, usage message on stderr, no report file written. (spec.md:101-102; 79) | Exit 2; usage text on stderr; no report file created. | Exit 2 and usage text, but an (empty) report file was created anyway. | Exit != 2, no usage text, or a report file written. | Yes | `python3 artifact/canvas_diff.py /nonexistent/html NEW.txt -o out.md; echo $?` → 2; check stderr; assert `out.md` absent. |
| TC-05 | Unparseable snapshot: one fixture is deliberately malformed HTML with no resolvable assignment data → exit 1; stderr names the failing file; no partial report written. (spec.md:103-105; 76; confirmed by decision D4) | Exit 1; stderr names the failing file; report file absent (nothing partial written). | Exit 1 and failing file named, but an empty or partial report file exists. | Exit != 1, silent failure, or wrong file named. | Yes | unittest criterion 5; run CLI on a malformed fixture and assert exit code, stderr text, and `OUT_MD` absence. |
| TC-06 | All criteria are automated and runnable via `python3 -m unittest discover -s artifact/tests`. (spec.md:88; 107) | The exact command runs and exercises every criterion with no failures. | Suite runs but needs a manual step/flag, or one case depends on a real capture instead of a fixture. | Command fails, crashes, or leaves a criterion untested/unpassable. | Yes | Run `python3 -m unittest discover -s artifact/tests`. |
| TC-07 | The diff records the change kinds the snapshot data supports: due-date changes, point adjustments, removed assignments, added assignments. Description-edit detection is out of scope in this proof of concept (decision D8; spec.md:17-18 names it for the full tool). | Each supported kind is detected and surfaced when its fixture is present. | Three of four supported kinds surface; or a kind is detected with a wrong label. | One or more supported change kinds are silently skipped. | Yes | Fixture pair per change kind; assert each appears in the report. |
| TC-08 | Report header line states the two snapshots compared and the run timestamp. (spec.md:57-58) | Header present, names both snapshot paths, and includes a timestamp. | Header present but omits one path or the timestamp. | No header line at all. | Yes | Run the tool and inspect the report's first content line. |
| TC-09 | One-line summary states N changed assignments, M removed, K added. (spec.md:59) | A summary line reports all three counts and they match the fixture diff. | Summary present but a count is wrong, or not all three (N/M/K) present. | No summary line. | Yes | Run on fixtures with known counts; assert the summary numbers. |
| TC-10 | One section per affected assignment headed `## <Title>`; bullet lines use the documented labels: `Due date: A → B`, `Points: X → Y`, `Assignment removed`, `Assignment added`. `Description edited` is not produced in this proof of concept (decision D8). (spec.md:60-63) | Sections headed, bullets formatted with the documented labels/arrows; nothing else per block. | Sections present but one bullet mislabeled or an arrow/format off. | Missing sections, unheaded bullets, or labels outside the documented set. | Yes | unittest + read `OUT_MD` output. |
| TC-11 | Per-assignment structured fields extracted: title, due date, point value, pinned against the real capture in `snapshots/`. Assignment descriptions are ignored in this proof of concept (decision D8). (spec.md:16; 49-50; decisions D1/D7/D8) | All three fields extracted for every assignment the capture renders, using selectors confirmed against that real HTML; records with no shown due date/points handled without error. | Fields extracted for only a subset of the assignments a capture shows. | A required field is never extracted from any capture, or parsing relies on guessed, unconfirmed selectors. | Yes | Parse `snapshots/Canvas_*.html`; assert title, due date, point value where the page shows them. |
| TC-12 | Exit codes exactly per table: 0 success, 1 processing/runtime (parse failure), 2 usage error. Boundary: a snapshot that cannot be opened/read → 2; a snapshot that opens/reads but cannot be parsed → 1. (spec.md:71-77; 79-82; decision D3) | All specified scenarios return their listed code, including open-failure→2 and parse-failure→1. | Codes correct in tested scenarios; an untested table row remains. | A specified scenario returns the wrong exit code, or open-failure and parse-failure are conflated. | Yes | Assert `$?` across the TC-01…TC-05 scenarios, a missing path, a permission-denied file, and a readable-but-malformed file. |
| TC-13 | CLI shape and order: `python3 artifact/canvas_diff.py OLD_HTML NEW_HTML [-o OUT_MD]`; each snapshot is a single HTML file; first positional = previous snapshot; second = current. (spec.md:25-31; decision D2) | Invocable exactly as documented; each positional is one HTML file; first arg is the earlier snapshot. | Runs but OLD/NEW semantics inverted, or accepts only paths, not HTML files. | Different argument shape or order. | Yes | Run the documented command on a pair with a known change; confirm old→new direction. |
| TC-14 | Default output path is `artifact/report.md` when `-o` is omitted. (spec.md:32) | Report written to `artifact/report.md`. | Report written but to a different default path (still valid output). | No default; errors without `-o`. | No | Run without `-o`; check `artifact/report.md`. |
| TC-15 | Python 3, standard library only (`html.parser`, `argparse`, `unittest`). (spec.md:22; system_prompt:16) | Imports only Python 3 stdlib modules and the stated trio drives parse/CLI/test. | Stdlib only but an extra stdlib module replaces one of the named trio. | Any third-party dependency. | Yes | Inspect imports in `artifact/canvas_diff.py` and helpers; `python3 -m py_compile`. |
| TC-16 | A single Markdown report file at `OUT_MD`; nothing else is written. (spec.md:55-57; 66) | Exactly one `.md` file produced per run, at `OUT_MD`. | One file produced but wrong extension, or a temp file left behind and cleaned. | Multiple output files, non-Markdown output, or output elsewhere. | Yes | `ls`/`git status` around a run; run in a read-only CWD to catch strays. |
| TC-17 | `OUT_MD` is written fresh or overwritten each run. (spec.md:42) | Rerunning replaces the prior report in place. | Overwrites in place but leaves a stale copy elsewhere. | Refuses to overwrite, or leaves `*_old`/`*_new`/backup copies. | No | Run twice on different inputs; confirm one file, current content, no backups. |
| TC-18 | Whenever a bug is fixed, add a regression test that would have caught it. (system_prompt:46) | Every bug-fix commit includes a regression test that fails on the old code. | Most fixes covered; one fix lacks a test or the test is untracked. | A fix landed with no regression test. | No | `git log` of bug-fix commits; check `artifact/tests` for the matching regression. |
| TC-19 | Per-assignment sections are sorted alphabetically by title within the report. (decision D6; resolves spec.md:68-69) | `## <Title>` sections appear in ASCII alphanumeric order of title. | Order correct but tie/case handling unspecified and consistent. | Sections in arbitrary or reversed order. | No | Extract `## ` headings from `OUT_MD`; assert sorted by title. |
| TC-20 | The tool operates fully offline on local snapshot files; it never connects to Canvas or reads a live server. (spec.md:21; decision D1) | No network access attempted; run succeeds with networking disabled. | Only local files are parsed; no network code path exists but none exercised. | Any attempted network connection or remote read. | Yes | Run with network disabled (sandbox/offline); inspect code for `urlopen`, `http`, `socket` imports. |

## Prohibitions

| ID | Prohibition (source) | Meets | Approaching | Does not meet | Material | How to verify |
|---|---|---|---|---|---|---|
| PR-01 | Never modify, delete, or overwrite the original Canvas snapshot files (the `OLD_HTML`/`NEW_HTML` paths passed to the tool, the captures under `snapshots/`, and any copies under `sources/`). (spec.md:21; 124-128; system_prompt:25; 38-39; decision D1) | Input hashes identical before/after every run; the tool opens inputs read-only. | A file was touched and fully reverted; no persistent change. | Any modification, deletion, or overwrite of an input path, `snapshots/` capture, or `sources/` copy. | Yes | `shasum` inputs before and after a run; `git status` clean for inputs/`snapshots/`/`sources/`. |
| PR-02 | Never edit, delete, or create anything under `transcripts/`. (spec.md:131; system_prompt:40) | No change under `transcripts/` at any point. | An attempted edit occurred and was reverted; no lasting change. | Any change under `transcripts/`. | Yes | `git status`; `git log -- transcripts/`. |
| PR-03 | `CHARTER.md`, `AGENTS.md`, `spec.md`, `.ai/` (except the MEMORY append), `docs/` are read-only unless asked. (spec.md:129-130; system_prompt:40-41) | No unapproved write to any of these; the only `.ai/` write is the MEMORY append. | A file touched and reverted; no lasting diff. | An unapproved edit persists. | No | `git status`; `git diff` against HEAD. |
| PR-04 | `opencode.json`, `README.md`, `START_HERE.md` unchanged unless explicitly directed. (spec.md:132) | None modified without explicit direction. | Touched and reverted; no lasting diff. | A change persists without direction. | No | `git diff` against HEAD. |
| PR-05 | The tool writes to `OUT_MD` only; nothing else is written anywhere, including on error. (spec.md:66-67; system_prompt:30) | One run creates/modifies exactly one file: `OUT_MD`. Parse errors also leave no files behind. | Writes `OUT_MD` plus an incidental temp file that is removed automatically. | Writes anything beyond `OUT_MD` (logs, caches, snapshot copies). | Yes | `git status` + directory scan before/after a run, including an error run. |
| PR-06 | `.ai/MEMORY.md` changes are limited to appending a dated entry, newest at the bottom; never rewrite/delete an existing entry. (spec.md:119-121; system_prompt:26) | Diff of MEMORY is a single dated append at the bottom. | Append out of position (not bottom) or missing a date. | Existing entries rewritten or deleted. | No | `git diff` of `.ai/MEMORY.md`. |
| PR-07 | No code comments unless asked. (system_prompt:31) | No `#` comments in artifact code. | One or two incidental comments. | Pervasive comments across `artifact/*.py`. | No | `grep` for `#` in `artifact/*.py`. |
| PR-08 | Never print, log, or store secrets; on credential failure stop, report which command failed and what it said, and do not retry in a loop. (system_prompt:42-43) | No secret material in code, commits, logs, or output; credential failure reports the command + message once, then stops. | A secret-like value appeared once and was removed/rotated; or a single retry before stopping. | Secrets printed/logged/committed, or silent infinite retries. | Yes | `git log -p` review; grep for token patterns; observe a credential-failure scenario. |
| PR-09 | Everything under `sources/` and `snapshots/` is immutable — never edited, only read. (spec.md:127; system_prompt:25; decision D1) | Nothing under `sources/` or `snapshots/` created, edited, or deleted. | A file created accidentally then removed; no lasting trace. | Any persistent change under `sources/` or `snapshots/`. | Yes | `git status`; `ls -R sources/ snapshots/`; hash comparison. |

## Decisions

Resolved 2026-09-23. These settle the `[GUESS]` tags in `spec.md` (per spec.md:5)
and feed the criteria above. `spec.md` itself remains read-only until amended.

- **D1 — Capture source and selectors.** Snapshots are real HTML captures of
  rendered Canvas pages, provided as local fixture files under `snapshots/`;
  the tool never connects to Canvas and operates offline. Selectors are pinned
  against these real captures (TC-11, TC-20). The only capture present today
  (`snapshots/Canvas_y26M09d23h21m04s59.html`) is the **Dashboard** page
  (`<title>Dashboard</title>`). Per D8, the parser targets whatever assignments
  that page renders (To-Do items, stream/recent-activity entries) and does not
  need description text or a full assignment index.
- **D2 — Snapshot input form.** Each snapshot is a single HTML file; the two
  positionals are `OLD_HTML` (previous) and `NEW_HTML` (current). No directory
  or list input.
- **D3 — Read vs. parse failures.** Exit 2 when an input file cannot be
  opened/read (missing path, permission, I/O); exit 1 when the file reads but
  cannot be parsed into assignment records.
- **D4 — No partial report.** If processing fails, no report (partial or
  otherwise) is written (backs TC-05).
- **D5 — Human-readable.** No requirements beyond the pinned header, summary,
  `## <Title>` sections, and bullet lines.
- **D6 — Ordering.** Keep the sections in their defined order; within the
  report, sort assignments alphabetically by title (TC-19).
- **D7 — Final field scope.** Exactly four fields: title, due date,
  description, points. No additional Canvas fields.
- **D8 — Proof of concept (2026-09-23 amendment to D1/D7).** Ignore assignment
  descriptions and ignore that a capture is not a full assignment list. The POC
  parses whatever assignments the capture shows (title, due date, points where
  present) and does not emit `Description edited` changes. Description-edit
  detection and full-list parsing stay in scope for the full tool (spread
  across TC-07/TC-10/TC-11).

Weights, Material flags, and the 0.80 threshold in `rubric.json` are proposals
and can be adjusted on request.