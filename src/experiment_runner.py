import csv
import shutil
import time
from pathlib import Path

from src.agent_backend import RuleFixer, read_task_text
from src.metrics import cacheability_score, count_tokens
from src.prompts import build_cache_aware_prompt, build_normal_prompt
from src.workspace import SOURCE_TASKS_DIR


OUTPUT_PATH = Path("results/experiment_results.csv")
RUNS_DIR = Path("runs/experiments")


def get_task_dirs() -> list[Path]:
    return sorted(
        path
        for path in SOURCE_TASKS_DIR.iterdir()
        if path.is_dir() and path.name.startswith(("task_", "tsk_"))
    )


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
        return task_dirs

    if order_mode == "grouped":
        return sorted(task_dirs, key=lambda path: path.name)

    raise ValueError(f"Unknown order mode: {order_mode}")


def build_prompt(task_dir: Path, prompt_mode: str) -> str:
    task_text = read_task_text(task_dir)
    buggy_code = (task_dir / "buggy_code.py").read_text()

    task = {
        "task_id": task_dir.name,
        "repo": "toy_repair_benchmark",
        "language": "python",
        "description": task_text,
        "buggy_code": buggy_code,
    }

    if prompt_mode == "normal":
        return build_normal_prompt(task)

    if prompt_mode == "cache_aware":
        return build_cache_aware_prompt(task)

    raise ValueError(f"Unknown prompt mode: {prompt_mode}")


def run_pytest(task_dir: Path) -> bool:
    import subprocess

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
) -> list[dict]:
    run_dir = make_run_workspace(experiment_name)
    fixer = RuleFixer()

    task_dirs = sorted(
        path
        for path in run_dir.iterdir()
        if path.is_dir() and path.name.startswith(("task_", "tsk_"))
    )
    task_dirs = order_tasks(task_dirs, order_mode)

    rows = []
    previous_prompts = []

    for position, task_dir in enumerate(task_dirs, start=1):
        code_path = task_dir / "buggy_code.py"
        task_text = read_task_text(task_dir)
        before_code = code_path.read_text()

        prompt = build_prompt(task_dir, prompt_mode)
        prompt_tokens = count_tokens(prompt)
        prefix_reuse = cacheability_score(prompt, previous_prompts)

        before_passed = run_pytest(task_dir)

        start = time.perf_counter()
        fixed_code = fixer.fix(
            task_id=task_dir.name,
            task_text=task_text,
            buggy_code=before_code,
        )
        fix_time = time.perf_counter() - start

        code_path.write_text(fixed_code)
        after_passed = run_pytest(task_dir)

        rows.append(
            {
                "experiment": experiment_name,
                "task_id": task_dir.name,
                "position": position,
                "prompt_mode": prompt_mode,
                "order_mode": order_mode,
                "fixer": fixer.name,
                "before_passed": before_passed,
                "after_passed": after_passed,
                "prompt_tokens": prompt_tokens,
                "prefix_reuse": prefix_reuse,
                "fix_call_seconds": round(fix_time, 5),
                "output_chars": len(fixed_code),
            }
        )

        previous_prompts.append(prompt)

    return rows


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    experiments = [
        {
            "experiment_name": "normal_original",
            "prompt_mode": "normal",
            "order_mode": "original",
        },
        {
            "experiment_name": "cache_original",
            "prompt_mode": "cache_aware",
            "order_mode": "original",
        },
        {
            "experiment_name": "cache_grouped",
            "prompt_mode": "cache_aware",
            "order_mode": "grouped",
        },
    ]

    all_rows = []

    for experiment in experiments:
        print(f"Running {experiment['experiment_name']}...")
        rows = run_one_experiment(**experiment)
        all_rows.extend(rows)

    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Saved experiment results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()