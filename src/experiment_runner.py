import argparse
import csv
import json
import shutil
import subprocess
import time
from pathlib import Path

from src.agent_backend import ModelServerFixer, RuleFixer, read_task_text
from src.metrics import cacheability_score, count_tokens
from src.prompts import build_normal_prompt
from src.workspace import SOURCE_TASKS_DIR


CONFIG_PATH = Path("configs/experiments.json")
OUTPUT_PATH = Path("results/experiment_results.csv")
RUNS_DIR = Path("runs/experiments")


def load_experiments() -> list[dict]:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    return config["experiments"]


def get_task_dirs() -> list[Path]:
    return sorted(
        path
        for path in SOURCE_TASKS_DIR.iterdir()
        if path.is_dir() and path.name.startswith(("task_", "tsk_"))
    )


def task_number(task_id: str) -> int:
    return int(task_id.split("_")[-1])


def read_task_meta(task_dir: Path) -> dict:
    meta_path = task_dir / "metadata.json"

    if not meta_path.exists():
        return {
            "repo_group": "misc_utils",
            "bug_type": "unknown",
            "difficulty": "unknown",
        }

    with open(meta_path, "r") as f:
        return json.load(f)


def repo_group(task_dir: Path) -> str:
    meta = read_task_meta(task_dir)
    return meta.get("repo_group", "misc_utils")


def repo_context(group: str) -> str:
    contexts = {
        "math_utils": (
            "Repository context:\n"
            "This repo has small math helper functions. Bugs are usually simple "
            "edge cases, off-by-one issues, or wrong arithmetic.\n"
        ),
        "string_utils": (
            "Repository context:\n"
            "This repo has small string helpers. Bugs usually involve whitespace, "
            "case handling, normalization, or basic parsing.\n"
        ),
        "list_utils": (
            "Repository context:\n"
            "This repo has list and collection helpers. Bugs usually involve empty "
            "inputs, negative values, or aggregation logic.\n"
        ),
        "file_utils": (
            "Repository context:\n"
            "This repo has file and path helpers. Bugs usually involve extension "
            "checks, path handling, or simple filtering.\n"
        ),
        "dict_utils": (
            "Repository context:\n"
            "This repo has dictionary helpers. Bugs usually involve merge logic, "
            "mutation, defaults, or count updates.\n"
        ),
        "misc_utils": (
            "Repository context:\n"
            "This repo has small Python utility functions with deterministic tests.\n"
        ),
    }

    return contexts.get(group, contexts["misc_utils"])


def make_run_workspace(experiment_name: str) -> Path:
    run_dir = RUNS_DIR / experiment_name

    if run_dir.exists():
        shutil.rmtree(run_dir)

    run_dir.mkdir(parents=True, exist_ok=True)

    for task_dir in get_task_dirs():
        shutil.copytree(task_dir, run_dir / task_dir.name)

    return run_dir


def order_tasks(task_dirs: list[Path], order_mode: str) -> list[Path]:
    if order_mode == "original":
        mixed_order = [1, 3, 5, 7, 2, 4, 6, 8]
        rank = {task_num: i for i, task_num in enumerate(mixed_order)}

        return sorted(
            task_dirs,
            key=lambda path: rank.get(task_number(path.name), 999),
        )

    if order_mode == "grouped":
        return sorted(
            task_dirs,
            key=lambda path: (repo_group(path), task_number(path.name)),
        )

    raise ValueError(f"Unknown order mode: {order_mode}")


def build_cache_prompt(task_dir: Path) -> str:
    task_text = read_task_text(task_dir)
    buggy_code = (task_dir / "buggy_code.py").read_text()
    group = repo_group(task_dir)

    return (
        "Fix the Python function below.\n"
        "Keep the fix small and do not rewrite unrelated code.\n\n"
        "Output format:\n"
        "- Bug summary\n"
        "- Fixed code\n\n"
        f"{repo_context(group)}\n"
        "Task-specific section:\n"
        f"Task ID: {task_dir.name}\n"
        f"Repository group: {group}\n"
        "Language: python\n\n"
        f"Problem:\n{task_text}\n\n"
        f"Buggy code:\n{buggy_code}\n"
    )


def build_cache_prompt_no_repo(task_dir: Path) -> str:
    task_text = read_task_text(task_dir)
    buggy_code = (task_dir / "buggy_code.py").read_text()
    group = repo_group(task_dir)

    return (
        "Fix the Python function below.\n"
        "Keep the fix small and do not rewrite unrelated code.\n\n"
        "Output format:\n"
        "- Bug summary\n"
        "- Fixed code\n\n"
        "Task-specific section:\n"
        f"Task ID: {task_dir.name}\n"
        f"Repository group: {group}\n"
        "Language: python\n\n"
        f"Problem:\n{task_text}\n\n"
        f"Buggy code:\n{buggy_code}\n"
    )


def build_prompt(task_dir: Path, prompt_mode: str) -> str:
    task_text = read_task_text(task_dir)
    buggy_code = (task_dir / "buggy_code.py").read_text()
    group = repo_group(task_dir)

    task = {
        "task_id": task_dir.name,
        "repo": group,
        "language": "python",
        "description": task_text,
        "buggy_code": buggy_code,
    }

    if prompt_mode == "normal":
        return build_normal_prompt(task)

    if prompt_mode == "cache_aware":
        return build_cache_prompt(task_dir)

    if prompt_mode == "cache_no_repo":
        return build_cache_prompt_no_repo(task_dir)

    raise ValueError(f"Unknown prompt mode: {prompt_mode}")


def pick_fixer(name: str):
    if name == "rule":
        return RuleFixer()

    if name == "model":
        return ModelServerFixer()

    raise ValueError(f"Unknown fixer: {name}")


def run_pytest(task_dir: Path) -> bool:
    result = subprocess.run(
        ["pytest", "-q"],
        cwd=task_dir,
        capture_output=True,
        text=True,
    )

    return result.returncode == 0


def run_one_experiment(
    experiment_name: str,
    prompt_mode: str,
    order_mode: str,
    fixer_name: str,
    max_tasks: int | None,
) -> list[dict]:
    run_dir = make_run_workspace(experiment_name)
    fixer = pick_fixer(fixer_name)

    task_dirs = sorted(
        path
        for path in run_dir.iterdir()
        if path.is_dir() and path.name.startswith(("task_", "tsk_"))
    )
    task_dirs = order_tasks(task_dirs, order_mode)

    if max_tasks is not None:
        task_dirs = task_dirs[:max_tasks]

    rows = []
    previous_prompts = []

    for position, task_dir in enumerate(task_dirs, start=1):
        code_path = task_dir / "buggy_code.py"
        task_text = read_task_text(task_dir)
        before_code = code_path.read_text()
        meta = read_task_meta(task_dir)

        prompt = build_prompt(task_dir, prompt_mode)
        prompt_tokens = count_tokens(prompt)

        best_prefix_reuse = cacheability_score(prompt, previous_prompts)
        recent_prefix_reuse = cacheability_score(prompt, previous_prompts[-1:])

        before_passed = run_pytest(task_dir)

        start = time.perf_counter()
        fixed_code = fixer.fix(
            task_id=task_dir.name,
            task_text=task_text,
            buggy_code=before_code,
        )
        fix_time = time.perf_counter() - start

        call_info = getattr(fixer, "last_call", {})

        code_path.write_text(fixed_code)
        after_passed = run_pytest(task_dir)

        rows.append(
            {
                "experiment": experiment_name,
                "task_id": task_dir.name,
                "repo_group": meta.get("repo_group", "misc_utils"),
                "bug_type": meta.get("bug_type", "unknown"),
                "difficulty": meta.get("difficulty", "unknown"),
                "position": position,
                "prompt_mode": prompt_mode,
                "order_mode": order_mode,
                "fixer": fixer.name,
                "model": call_info.get("model", ""),
                "before_passed": before_passed,
                "after_passed": after_passed,
                "prompt_tokens": prompt_tokens,
                "best_prefix_reuse": best_prefix_reuse,
                "recent_prefix_reuse": recent_prefix_reuse,
                "fix_call_ms": round(fix_time * 1000, 4),
                "model_latency_seconds": call_info.get("latency_seconds", ""),
                "model_prompt_chars": call_info.get("prompt_chars", ""),
                "model_output_chars": call_info.get("output_chars", ""),
                "output_chars": len(fixed_code),
            }
        )

        previous_prompts.append(prompt)

    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixer",
        choices=["rule", "model"],
        default="rule",
        help="which fixer backend to use",
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=None,
        help="maximum number of tasks per experiment",
    )
    args = parser.parse_args()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_rows = []

    for experiment in load_experiments():
        experiment_name = experiment["name"]

        print(f"Running {experiment_name} with {args.fixer} fixer...")

        rows = run_one_experiment(
            experiment_name=experiment_name,
            prompt_mode=experiment["prompt_mode"],
            order_mode=experiment["order_mode"],
            fixer_name=args.fixer,
            max_tasks=args.max_tasks,
        )
        all_rows.extend(rows)

    if not all_rows:
        raise ValueError("No experiment rows were generated.")

    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Saved experiment results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()