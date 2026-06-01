from pathlib import Path

from src.experiment_runner import order_tasks, read_task_meta, repo_group


def test_read_task_meta_reads_repo_group(tmp_path):
    task_dir = tmp_path / "task_001"
    task_dir.mkdir()

    meta_file = task_dir / "metadata.json"
    meta_file.write_text('{"repo_group": "math_utils"}')

    meta = read_task_meta(task_dir)

    assert meta["repo_group"] == "math_utils"


def test_read_task_meta_has_default_when_missing(tmp_path):
    task_dir = tmp_path / "task_999"
    task_dir.mkdir()

    meta = read_task_meta(task_dir)

    assert meta["repo_group"] == "misc_utils"


def test_repo_group_uses_metadata(tmp_path):
    task_dir = tmp_path / "task_003"
    task_dir.mkdir()
    (task_dir / "metadata.json").write_text('{"repo_group": "string_utils"}')

    assert repo_group(task_dir) == "string_utils"


def test_grouped_order_uses_repo_group_then_task_number(tmp_path):
    names_and_groups = [
        ("task_005", "list_utils"),
        ("task_001", "math_utils"),
        ("task_004", "string_utils"),
        ("task_002", "math_utils"),
    ]

    task_dirs = []

    for name, group in names_and_groups:
        task_dir = tmp_path / name
        task_dir.mkdir()
        (task_dir / "metadata.json").write_text(f'{{"repo_group": "{group}"}}')
        task_dirs.append(task_dir)

    ordered = order_tasks(task_dirs, "grouped")
    ordered_names = [path.name for path in ordered]

    assert ordered_names == ["task_005", "task_001", "task_002", "task_004"]