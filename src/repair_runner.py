import csv
import json
import re
import subprocess
import time
import argparse
from pathlib import Path

from src.agent_backend import ModelServerFixer, RuleFixer, read_task_text
from src.workspace import reset_run_workspace


OUTPUT_PATH = Path("results/repair_results.csv")
TRACE_PATH = Path("results/repair_traces.jsonl")


def parse_pytest_counts(output: str) -> dict:
    failed_match = re.search(r"(\d+)\s+failed", output)
    passed_match = re.search(r"(\d+)\s+passed", output)

    failed = int(failed_match.group(1)) if failed_match else 0
    passed = int(passed_match.group(1)) if passed_match else 0

    return {
        "tests_passed": passed,
        "tests_failed": failed,
        "total_tests": passed + failed,
    }


def run_pytest(task_dir: Path) -> dict:
    start = time.perf_counter()

    result = subprocess.run(
        ["pytest", "-q"],
        cwd=task_dir,
        capture_output=True,
        text=True,
    )

    elapsed = time.perf_counter() - start
    output = result.stdout + "\n" + result.stderr
    counts = parse_pytest_counts(output)

    return {
        "passed": result.returncode == 0,
        "tests_passed": counts["tests_passed"],
        "tests_failed": counts["tests_failed"],
        "total_tests": counts["total_tests"],
        "runtime_seconds": round(elapsed, 4),
    }

def pick_fixer(name: str):
    if name == "rule":
        return RuleFixer()

    if name == "model":
        return ModelServerFixer()

    raise ValueError(f"Unknown fixer: {name}")
def write_trace(trace: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(TRACE_PATH, "a") as f:
        f.write(json.dumps(trace) + "\n")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if TRACE_PATH.exists():
        TRACE_PATH.unlink()
    parser = argparse.ArgumentParser()
    parser.add_argument(
    "--fixer",
    choices=["rule", "model"],
    default="rule",
    help="which fixer backend to use",
)
    args = parser.parse_args()
    run_dir = reset_run_workspace()
    fixer = pick_fixer(args.fixer)

    task_dirs = sorted(
        path for path in run_dir.iterdir()
        if path.is_dir() and path.name.startswith(("task_", "tsk_"))
    )

    rows = []

    for task_dir in task_dirs:
        print(f"Repairing {task_dir.name}...")

        code_path = task_dir / "buggy_code.py"
        task_text = read_task_text(task_dir)
        before_code = code_path.read_text()

        before = run_pytest(task_dir)

        fixed_code = fixer.fix(
            task_id=task_dir.name,
            task_text=task_text,
            buggy_code=before_code,
        )

        code_path.write_text(fixed_code)

        after_code = code_path.read_text()
        after = run_pytest(task_dir)

        write_trace(
            {
                "task_id": task_dir.name,
                "fixer": fixer.name,
                "before_passed": before["passed"],
                "after_passed": after["passed"],
                "before_code": before_code,
                "after_code": after_code,
            }
        )

        rows.append(
            {
                "task_id": task_dir.name,
                "before_passed": before["passed"],
                "before_tests_passed": before["tests_passed"],
                "before_tests_failed": before["tests_failed"],
                "after_passed": after["passed"],
                "after_tests_passed": after["tests_passed"],
                "after_tests_failed": after["tests_failed"],
                "after_total_tests": after["total_tests"],
                "repair_runtime_seconds": after["runtime_seconds"],
                "fixer": fixer.name,
            }
        )

    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved repair results to {OUTPUT_PATH}")
    print(f"Saved repair traces to {TRACE_PATH}")


if __name__ == "__main__":
    main()
