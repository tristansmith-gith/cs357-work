#!/usr/bin/env python3
"""Compare two Canvas Dashboard assignment snapshots and write one Markdown
report of every change (due dates, points, removals, additions), grouped by
assignment title. Offline tool: Python 3, standard library only."""

import argparse
import datetime
import html.parser
import os
import re
import sys
from dataclasses import dataclass

NOT_SHOWN = "not shown"


class SnapshotError(Exception):
    def __init__(self, path, message, exit_code):
        super().__init__(message)
        self.path = path
        self.message = message
        self.exit_code = exit_code


@dataclass
class Assignment:
    title: str
    due: str = NOT_SHOWN
    points: str = NOT_SHOWN


POINTS_RE = re.compile(
    r"^\s*(\d+(?:\.\d+)?)\s*points\s*$",
    re.IGNORECASE,
)
DUE_STRIP_RE = re.compile(r"^\s*Due\s+", re.IGNORECASE)
MONTH = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May"
    r"|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?"
    r"|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)
DATE_RE = re.compile(
    r"^\s*(?:Due\s+)?" + MONTH + r"\s+\d{1,2}(?:\s*(?:,|at)\s*\d{4})?\b",
    re.IGNORECASE,
)


class DashboardParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._stack = []
        self._current = None
        self._records = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").split())
        self._stack.append({"tag": tag, "classes": classes, "buffer": None})
        if tag == "div" and "ToDoSidebarItem" in classes and self._current is None:
            self._current = {
                "title": None,
                "svg_label": None,
                "lis": [],
                "depth": len(self._stack),
            }
            return
        if self._current is None:
            return
        if tag == "svg":
            label = attrs.get("label")
            if label:
                self._current["svg_label"] = label
        elif tag == "a":
            aria = attrs.get("aria-label")
            if aria and aria.startswith("Assignment, "):
                self._current["title"] = aria[len("Assignment, "):].strip()
        elif tag == "li":
            self._stack[-1]["buffer"] = []

    def handle_data(self, data):
        if self._current is not None and self._stack and self._stack[-1]["buffer"] is not None:
            self._stack[-1]["buffer"].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        top = self._stack[-1] if self._stack else None
        if top is not None and top["buffer"] is not None and self._current is not None:
            text = " ".join("".join(top["buffer"]).split())
            if text:
                self._current["lis"].append(text)
        if (
            tag == "div"
            and top is not None
            and top.get("tag") == "div"
            and "ToDoSidebarItem" in top.get("classes", ())
            and self._current is not None
            and len(self._stack) == self._current["depth"]
        ):
            self._finalize_item()
        if top is not None:
            self._stack.pop()

    def _finalize_item(self):
        item = self._current
        self._current = None
        title = item["title"]
        if title is None:
            if item["svg_label"] == "Assignment":
                raise ValueError("assignment record without a resolvable title")
            return
        assignment = Assignment(title=title)
        for text in item["lis"]:
            points = POINTS_RE.match(text)
            if points and assignment.points == NOT_SHOWN:
                assignment.points = points.group(1)
            elif DATE_RE.match(text) and assignment.due == NOT_SHOWN:
                assignment.due = DUE_STRIP_RE.sub("", text).strip()
        self._records.append(assignment)

    def records(self):
        seen = {}
        for assignment in self._records:
            seen.setdefault(assignment.title, assignment)
        return list(seen.values())


def parse_records(html_text):
    parser = DashboardParser()
    parser.feed(html_text)
    return parser.records()


def parse_snapshot(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            html_text = handle.read()
    except OSError as exc:
        raise SnapshotError(path, f"cannot read {path}: {exc}", 2) from exc
    except UnicodeDecodeError as exc:
        raise SnapshotError(path, f"cannot parse {path}: {exc}", 1) from exc
    try:
        records = parse_records(html_text)
    except (ValueError, AssertionError, RecursionError) as exc:
        raise SnapshotError(path, f"cannot parse {path}: {exc}", 1) from exc
    if not records:
        raise SnapshotError(path, f"no assignment data in {path}", 1)
    return records


def build_report(old_path, new_path, old_records, new_records):
    old = {a.title: a for a in old_records}
    new = {a.title: a for a in new_records}
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    changed = [t for t in old if t in new and (old[t].due != new[t].due or old[t].points != new[t].points)]
    removed = [t for t in old if t not in new]
    added = [t for t in new if t not in old]
    lines = [
        f"Canvas Snapshot Diff: {old_path} → {new_path} at {timestamp}",
        "",
        f"Summary: {len(changed)} changed assignments, {len(removed)} removed, {len(added)} added.",
        "",
    ]
    if not changed and not removed and not added:
        lines.append("No changes detected.")
    else:
        for title in sorted(set(changed) | set(removed) | set(added)):
            lines.append(f"## {title}")
            if title in changed:
                if old[title].due != new[title].due:
                    lines.append(f"- Due date: {old[title].due} → {new[title].due}")
                if old[title].points != new[title].points:
                    lines.append(f"- Points: {old[title].points} → {new[title].points}")
            elif title in removed:
                lines.append("- Assignment removed")
            else:
                lines.append("- Assignment added")
            lines.append("")
    return "\n".join(lines) + "\n"


def default_output_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "report.md")


def usage_error(argument_parser, message):
    print(f"error: {message}", file=sys.stderr)
    argument_parser.print_usage(sys.stderr)
    return 2


def main(argv=None):
    argument_parser = argparse.ArgumentParser(
        prog="canvas_diff",
        description="Compare two Canvas Dashboard assignment snapshots and write a Markdown change report.",
        usage="%(prog)s OLD_HTML NEW_HTML [-o OUT_MD]",
    )
    argument_parser.add_argument("old_html", help="earlier Canvas snapshot: one HTML file")
    argument_parser.add_argument("new_html", help="later Canvas snapshot: one HTML file")
    argument_parser.add_argument(
        "-o",
        "--output",
        default=default_output_path(),
        help="report output path (default: %(default)s)",
    )
    args = argument_parser.parse_args(argv)

    records = []
    for path in (args.old_html, args.new_html):
        try:
            records.append(parse_snapshot(path))
        except SnapshotError as exc:
            if exc.exit_code == 2:
                return usage_error(argument_parser, exc.message)
            print(f"error: {exc.message}", file=sys.stderr)
            return exc.exit_code

    report = build_report(args.old_html, args.new_html, records[0], records[1])
    try:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(report)
    except OSError as exc:
        return usage_error(argument_parser, f"cannot write report to {args.output}: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())