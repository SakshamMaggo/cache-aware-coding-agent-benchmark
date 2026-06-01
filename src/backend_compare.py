import csv
import subprocess
from pathlib import Path

import pandas as pd


OUTPUT_PATH = Path("results/backend_comparison.csv")


def run_backend(fixer: str, max_attempts: int = 2) -> pd.DataFrame:
    cmd = [
        "python",
        "-m",
        "src.repair_runner",
        "--fixer",
        fixer,
        "--max-attempts",
        str(max_attempts),
    ]

    subprocess.run(cmd, check=True)

    df = pd.read_csv("results/repair_results.csv")
    df["backend_run"] = fixer
    return df


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    runs = []

    for fixer in ["none", "rule"]:
        print(f"Running backend: {fixer}")
        runs.append(run_backend(fixer))

    combined = pd.concat(runs, ignore_index=True)

    summary = (
        combined.groupby("backend_run")
        .agg(
            tasks=("task_id", "count"),
            pass_rate=("after_passed", "mean"),
            avg_attempts=("attempts_used", "mean"),
            failed_tests_after=("after_tests_failed", "sum"),
            total_fix_call_ms=("total_fix_call_ms", "sum"),
        )
        .reset_index()
    )

    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary.columns))
        writer.writeheader()
        writer.writerows(summary.to_dict("records"))

    print(f"Saved backend comparison to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()