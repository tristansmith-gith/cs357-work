import csv

from agent import run_agent, load_config, TOOLS
from task_set import TASKS

RESULTS_PATH = "results.csv"
FIELDNAMES = ["id", "goal", "answer", "passed", "steps"]


def main():
    config = load_config()
    rows = []

    for task in TASKS:
        print(f"\n=== Task: {task['id']} ===")
        try:
            answer, steps, reason = run_agent(task["goal"], config, TOOLS)
        except Exception as e:
            answer, steps, reason = f"[evaluate:error] {e}", 0, "error"

        try:
            passed = bool(task["check"](answer))
        except Exception as e:
            print(f"[evaluate:check] {task['id']}: {e}")
            passed = False

        rows.append({
            "id": task["id"],
            "goal": task["goal"],
            "answer": answer,
            "passed": passed,
            "steps": steps,
        })
        print(f"Result: {task['id']} passed={passed} steps={steps} ({reason})")

    with open(RESULTS_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    passed_count = sum(1 for row in rows if row["passed"])
    print(f"\n{passed_count}/{len(rows)} tasks passed. Wrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
