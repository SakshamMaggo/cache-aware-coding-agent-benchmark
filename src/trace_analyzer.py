import csv
import json
from pathlib import Path


TRACE_PATH = Path("results/repair_traces.jsonl")
OUTPUT_PATH = Path("results/attempt_results.csv")


def load_traces() -> list[dict]:
    if not TRACE_PATH.exists():
        raise FileNotFoundError("No repair traces found. Run repair_runner first.")

    traces = []

    with open(TRACE_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                traces.append(json.loads(line))

    return traces


def flatten_attempts(traces: list[dict]) -> list[dict]:
    rows = []

    for trace in traces:
        task_id = trace["task_id"]
        fixer = trace["fixer"]

        for attempt in trace.get("attempts", []):
            rows.append(
                {
                    "task_id": task_id,
                    "fixer": fixer,
                    "attempt": attempt["attempt"],
                    "passed": attempt["passed"],
                    "tests_passed": attempt["tests_passed"],
                    "tests_failed": attempt["tests_failed"],
                    "model": attempt.get("model", ""),
                    "model_latency_seconds": attempt.get("model_latency_seconds", ""),
                    "prompt_chars": attempt.get("prompt_chars", ""),
                    "output_chars": attempt.get("output_chars", ""),
                }
            )

    return rows


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    traces = load_traces()
    rows = flatten_attempts(traces)

    if not rows:
        raise ValueError("No repair attempts found in the trace file.")

    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved attempt results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()