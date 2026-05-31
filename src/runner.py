import csv
from pathlib import Path

from src.backends import DummyBackend
from src.metrics import count_tokens, cacheability_score
from src.prompts import build_normal_prompt, build_cache_aware_prompt
from src.scheduler import random_order, cache_aware_order


TASKS = [
    {
        "task_id": "task_001",
        "repo": "toy_math_repo",
        "language": "python",
        "description": "Fix the add_numbers function. It currently subtracts instead of adding.",
        "buggy_code": "def add_numbers(a, b):\n    return a - b",
    },
    {
        "task_id": "task_002",
        "repo": "toy_math_repo",
        "language": "python",
        "description": "Fix the factorial function. It fails for input 0.",
        "buggy_code": "def factorial(n):\n    result = 1\n    for i in range(1, n):\n        result *= i\n    return result",
    },
    {
        "task_id": "task_003",
        "repo": "toy_string_repo",
        "language": "python",
        "description": "Fix the palindrome checker. It should ignore capitalization.",
        "buggy_code": "def is_palindrome(text):\n    return text == text[::-1]",
    },
    {
        "task_id": "task_004",
        "repo": "toy_string_repo",
        "language": "python",
        "description": "Fix the word counter. It should return 0 for an empty string.",
        "buggy_code": "def count_words(text):\n    return len(text.split(' '))",
    },
    {
        "task_id": "task_005",
        "repo": "toy_list_repo",
        "language": "python",
        "description": "Fix the max finder. It should handle negative numbers correctly.",
        "buggy_code": "def find_max(nums):\n    current = 0\n    for x in nums:\n        if x > current:\n            current = x\n    return current",
    },
    {
        "task_id": "task_006",
        "repo": "toy_list_repo",
        "language": "python",
        "description": "Fix the average function. It should avoid division by zero for empty lists.",
        "buggy_code": "def average(nums):\n    return sum(nums) / len(nums)",
    },
]


def run_experiment(experiment_name: str, prompt_style: str, ordering: str) -> list[dict]:
    backend = DummyBackend()
    previous_prompts = []
    rows = []

    if ordering == "random":
        ordered_tasks = random_order(TASKS)
    elif ordering == "cache_aware":
        ordered_tasks = cache_aware_order(TASKS)
    else:
        raise ValueError(f"Unknown ordering: {ordering}")

    for task in ordered_tasks:
        if prompt_style == "normal":
            prompt = build_normal_prompt(task)
        elif prompt_style == "cache_aware":
            prompt = build_cache_aware_prompt(task)
        else:
            raise ValueError(f"Unknown prompt style: {prompt_style}")

        prompt_tokens = count_tokens(prompt)
        cache_score = cacheability_score(prompt, previous_prompts)

        result = backend.generate(prompt)

        row = {
            "experiment": experiment_name,
            "task_id": task["task_id"],
            "repo": task["repo"],
            "language": task["language"],
            "prompt_style": prompt_style,
            "ordering": ordering,
            "backend": result["backend"],
            "prompt_tokens": prompt_tokens,
            "cacheability_score": cache_score,
            "latency_seconds": result["latency_seconds"],
            "ttft_seconds": result["ttft_seconds"],
            "tokens_per_second": result["tokens_per_second"],
            "simulated_pass": True,
        }

        rows.append(row)
        previous_prompts.append(prompt)

    return rows


def save_results(rows: list[dict], output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        raise ValueError("No rows to save.")

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    all_rows = []

    experiments = [
        ("normal_random", "normal", "random"),
        ("cache_aware_random", "cache_aware", "random"),
        ("cache_aware_grouped", "cache_aware", "cache_aware"),
    ]

    for experiment_name, prompt_style, ordering in experiments:
        rows = run_experiment(experiment_name, prompt_style, ordering)
        all_rows.extend(rows)

    output_path = "results/dummy_cache_benchmark_results.csv"
    save_results(all_rows, output_path)

    print(f"Saved {len(all_rows)} rows to {output_path}")


if __name__ == "__main__":
    main()