import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ARTIFACT_DIR = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ARTIFACT_DIR / "tests" / "fixtures"
TOOL_PATH = ARTIFACT_DIR / "canvas_diff.py"
SNAPSHOT_DIR = ARTIFACT_DIR.parent / "snapshots"
SNAPSHOT = next(SNAPSHOT_DIR.glob("Canvas_*.html"), None) if SNAPSHOT_DIR.exists() else None

sys.path.insert(0, str(ARTIFACT_DIR))

import canvas_diff


def run_tool(old, new, out_path):
    return subprocess.run(
        [sys.executable, str(TOOL_PATH), str(old), str(new), "-o", str(out_path)],
        capture_output=True,
        text=True,
    )


class CanvasDiffCliTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.out_path = Path(self.tmpdir.name) / "out.md"

    def read_report(self):
        return self.out_path.read_text(encoding="utf-8")

    def base(self):
        return FIXTURES_DIR / "base.html"

    def test_identical_snapshots_no_changes(self):
        base = self.base()
        result = run_tool(base, base, self.out_path)
        self.assertEqual(result.returncode, 0)
        report = self.read_report()
        self.assertIn("No changes detected.", report)
        self.assertNotIn("## ", report)

    def test_single_points_change(self):
        result = run_tool(self.base(), FIXTURES_DIR / "points_changed.html", self.out_path)
        self.assertEqual(result.returncode, 0)
        report = self.read_report()
        self.assertIn("Summary: 1 changed assignments, 0 removed, 0 added.", report)
        self.assertIn("## Alpha", report)
        self.assertIn("- Points: 10 → 30", report)
        self.assertNotIn("Due date", report)
        self.assertNotIn("## Beta", report)

    def test_removal_and_addition(self):
        result = run_tool(self.base(), FIXTURES_DIR / "removed_added.html", self.out_path)
        self.assertEqual(result.returncode, 0)
        report = self.read_report()
        self.assertIn("Summary: 0 changed assignments, 1 removed, 1 added.", report)
        self.assertIn("## Beta", report)
        self.assertIn("- Assignment removed", report)
        self.assertIn("## Delta", report)
        self.assertIn("- Assignment added", report)
        self.assertNotIn("## Alpha", report)
        self.assertLess(report.index("## Beta"), report.index("## Delta"))

    def test_missing_input_exits_2_and_writes_nothing(self):
        missing = Path(self.tmpdir.name) / "missing.html"
        for old, new in ((missing, self.base()), (self.base(), missing)):
            with self.subTest(old=str(old), new=str(new)):
                result = run_tool(old, new, self.out_path)
                self.assertEqual(result.returncode, 2)
                self.assertIn("usage", result.stderr.lower())
                self.assertFalse(self.out_path.exists())

    def test_malformed_snapshot_exits_1_and_names_file(self):
        malformed = FIXTURES_DIR / "malformed.html"
        for old, new in ((self.base(), malformed), (malformed, self.base())):
            with self.subTest(old=str(old), new=str(new)):
                result = run_tool(old, new, self.out_path)
                self.assertEqual(result.returncode, 1)
                self.assertIn("malformed", result.stderr)
                self.assertFalse(self.out_path.exists())

    def test_unwritable_output_exits_2(self):
        result = run_tool(self.base(), self.base(), Path(self.tmpdir.name))
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage", result.stderr.lower())

    def test_due_date_not_shown_transition(self):
        result = run_tool(self.base(), FIXTURES_DIR / "due_gone.html", self.out_path)
        self.assertEqual(result.returncode, 0)
        report = self.read_report()
        self.assertIn("## Alpha", report)
        self.assertIn("- Due date: Sep 24 at 11:59pm → not shown", report)
        self.assertNotIn("- Points:", report)

    @unittest.skipIf(SNAPSHOT is None, "real Canvas capture not present")
    def test_snapshot_is_never_modified(self):
        before = SNAPSHOT.read_bytes()
        result = run_tool(SNAPSHOT, SNAPSHOT, self.out_path)
        after = SNAPSHOT.read_bytes()
        self.assertEqual(result.returncode, 0)
        self.assertIn("No changes detected.", self.read_report())
        self.assertEqual(before, after)


class ParserUnitTests(unittest.TestCase):
    def test_assignment_item_extracts_title_due_points(self):
        html_text = (
            '<div class="ToDoSidebarItem">'
            '<svg label="Assignment"></svg>'
            '<div class="ToDoSidebarItem__Title">'
            '<a aria-label="Assignment, Essay One">Essay One</a>'
            "</div>"
            '<ul data-testid="ToDoSidebarItem__InformationRow">'
            "<li>25 points</li><li>Sep 24 at 11:59pm</li>"
            "</ul>"
            "</div>"
        )
        records = canvas_diff.parse_records(html_text)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].title, "Essay One")
        self.assertEqual(records[0].points, "25")
        self.assertEqual(records[0].due, "Sep 24 at 11:59pm")

    def test_non_assignment_items_are_ignored(self):
        html_text = (
            '<div class="ToDoSidebarItem">'
            '<svg label="Announcement"></svg>'
            '<div class="ToDoSidebarItem__Title">'
            '<a aria-label="Announcement, Welcome">Welcome</a>'
            "</div>"
            "</div>"
            '<div class="ToDoSidebarItem">'
            '<svg label="Calendar Event"></svg>'
            '<div class="ToDoSidebarItem__Title">'
            '<a aria-label="Calendar Event, Class Meeting">Class Meeting</a>'
            "</div>"
            "</div>"
        )
        self.assertEqual(canvas_diff.parse_records(html_text), [])

    def test_duplicate_titles_dedupe_first_wins(self):
        html_text = (
            '<div class="ToDoSidebarItem"><a aria-label="Assignment, Alpha"></a>'
            "<li>10 points</li></div>"
            '<div class="ToDoSidebarItem"><a aria-label="Assignment, Alpha"></a>'
            "<li>99 points</li></div>"
        )
        records = canvas_diff.parse_records(html_text)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].points, "10")

    def test_unresolvable_assignment_record_raises(self):
        html_text = '<div class="ToDoSidebarItem"><svg label="Assignment"></svg></div>'
        with self.assertRaises(ValueError):
            canvas_diff.parse_records(html_text)

    @unittest.skipIf(SNAPSHOT is None, "real Canvas capture not present")
    def test_real_capture_maps_to_expected_records(self):
        records = canvas_diff.parse_snapshot(str(SNAPSHOT))
        by_title = {r.title: r for r in records}
        self.assertEqual(
            set(by_title),
            {"Lab: OpenCode Studio", "Homework 3", "Writing as Thinking - Week 5"},
        )
        self.assertEqual(by_title["Lab: OpenCode Studio"].points, "100")
        self.assertEqual(by_title["Lab: OpenCode Studio"].due, "Sep 24 at 11:59pm")
        self.assertEqual(by_title["Homework 3"].points, "not shown")
        self.assertEqual(by_title["Homework 3"].due, "Sep 23 at 11:59pm")
        self.assertEqual(by_title["Writing as Thinking - Week 5"].points, "10")
        self.assertEqual(by_title["Writing as Thinking - Week 5"].due, "not shown")


if __name__ == "__main__":
    unittest.main()