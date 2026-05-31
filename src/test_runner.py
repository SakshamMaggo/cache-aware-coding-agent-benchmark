import csv
import re
import subprocess
import time
from pathlib import Path


TASKS_DIR = Path("benchmark_tasks")
OUTPUT_PATH = Path("results/task_test_results.csv")


def parse_pytest_counts(output: str) -> dict:
    """
    Extracts simple pass/fail counts from pytest output.

    Examples:
    '3 failed in 0.02s'
    '1 failed, 2 passed in 0.02s'
    '3 passed in 0.02s'
    """
    failed_match = re.search(r"(\d+)\s+failed", output)
    passed_match = re.search(r"(\d+)\s+passed", output)

    failed = int(failed_match.group(1)) if failed_match else 0
    passed = int(passed_match.group(1)) if passed_match else 0

    return {
        "tests_passed": passed,
        "tests_failed": failed,
        "total_tests": passed + failed,
    }


def extract_short_failure(output: str) -> str:
    """
    Keeps only a short readable failure summary.
    """
    lines = output.splitlines()
    failed_lines = [line.strip() for line in lines if "FAILED" in line]

    if failed_lines:
        return " ; ".join(failed_lines[:3])

    if "passed" in output and "failed" not in output:
        return "all tests passed"

    return "check pytest output"


def run_pytest_for_task(task_dir: Path) -> dict:
    start = time.perf_counter()

    result = subprocess.run(
        ["pytest", "-q"],
        cwd=task_dir,
        capture_output=True,
        text=True,
    )

    end = time.perf_counter()
    output = result.stdout + "\n" + result.stderr

    counts = parse_pytest_counts(output)
    passed = result.returncode == 0

    return {
        "task_id": task_dir.name,
        "passed": passed,
        "tests_passed": counts["tests_passed"],
        "tests_failed": counts["tests_failed"],
        "total_tests": counts["total_tests"],
        "runtime_seconds": round(end - start, 4),
        "short_failure": extract_short_failure(output),
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    task_dirs = sorted(
        path for path in TASKS_DIR.iterdir()
        if path.is_dir() and path.name.startswith(("task_", "tsk_"))
    )

    if not task_dirs:
        raise FileNotFoundError("No task folders found inside benchmark_tasks/")

    rows = []

    for task_dir in task_dirs:
        print(f"Running tests for {task_dir.name}...")
        rows.append(run_pytest_for_task(task_dir))

    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved clean test results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()