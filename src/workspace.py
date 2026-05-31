import shutil
from pathlib import Path


SOURCE_TASKS_DIR = Path("benchmark_tasks")
RUNS_DIR = Path("runs")
CURRENT_RUN_DIR = RUNS_DIR / "current_run"


def reset_run_workspace() -> Path:
    """
    Creates a fresh working copy of benchmark_tasks.

    The original benchmark_tasks folder stays unchanged.
    All repair attempts happen inside runs/current_run.
    """
    if CURRENT_RUN_DIR.exists():
        shutil.rmtree(CURRENT_RUN_DIR)

    CURRENT_RUN_DIR.mkdir(parents=True, exist_ok=True)

    for task_dir in SOURCE_TASKS_DIR.iterdir():
        if task_dir.is_dir() and task_dir.name.startswith(("task_", "tsk_")):
            shutil.copytree(task_dir, CURRENT_RUN_DIR / task_dir.name)

    return CURRENT_RUN_DIR