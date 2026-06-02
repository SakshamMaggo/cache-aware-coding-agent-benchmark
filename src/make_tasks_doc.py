import json
from pathlib import Path

from src.workspace import SOURCE_TASKS_DIR


OUTPUT_PATH = Path("docs/tasks.md")


def read_meta(task_dir: Path) -> dict:
    meta_path = task_dir / "metadata.json"

    if not meta_path.exists():
        return {
            "repo_group": "unknown",
            "bug_type": "unknown",
            "difficulty": "unknown",
        }

    with open(meta_path, "r") as f:
        return json.load(f)


def read_task_summary(task_dir: Path) -> str:
    task_path = task_dir / "task.md"

    if not task_path.exists():
        return ""

    text = task_path.read_text().strip()
    return " ".join(text.split())


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    task_dirs = sorted(
        path
        for path in SOURCE_TASKS_DIR.iterdir()
        if path.is_dir() and path.name.startswith(("task_", "tsk_"))
    )

    lines = [
        "# Task Set",
        "",
        "This file summarizes the current benchmark tasks.",
        "",
        "| task | group | bug type | difficulty | systems relevance | short description |",
        "|---|---|---|---|---|---|",
    ]

    for task_dir in task_dirs:
        meta = read_meta(task_dir)
        summary = read_task_summary(task_dir)

        lines.append(
            "| "
            f"{task_dir.name} | "
            f"{meta.get('repo_group', 'unknown')} | "
            f"{meta.get('bug_type', 'unknown')} | "
            f"{meta.get('difficulty', 'unknown')} | "
            f"{meta.get('systems_relevance', 'unknown')} | "
            f"{summary} |"
        )

    OUTPUT_PATH.write_text("\n".join(lines) + "\n")
    print(f"Saved task summary to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()