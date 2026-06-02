from buggy_code import group_tasks_for_cache


def test_groups_by_repo_group():
    tasks = [
        {"task_id": "task_003", "repo_group": "string_utils"},
        {"task_id": "task_001", "repo_group": "math_utils"},
        {"task_id": "task_002", "repo_group": "math_utils"},
    ]

    grouped = group_tasks_for_cache(tasks)

    assert [task["task_id"] for task in grouped] == [
        "task_001",
        "task_002",
        "task_003",
    ]


def test_keeps_original_order_inside_same_group():
    tasks = [
        {"task_id": "task_002", "repo_group": "math_utils"},
        {"task_id": "task_001", "repo_group": "math_utils"},
        {"task_id": "task_004", "repo_group": "string_utils"},
    ]

    grouped = group_tasks_for_cache(tasks)

    assert [task["task_id"] for task in grouped] == [
        "task_002",
        "task_001",
        "task_004",
    ]


def test_missing_group_goes_last():
    tasks = [
        {"task_id": "task_001", "repo_group": "math_utils"},
        {"task_id": "task_999"},
        {"task_id": "task_003", "repo_group": "string_utils"},
    ]

    grouped = group_tasks_for_cache(tasks)

    assert [task["task_id"] for task in grouped] == [
        "task_001",
        "task_003",
        "task_999",
    ]


def test_does_not_mutate_input():
    tasks = [
        {"task_id": "task_003", "repo_group": "string_utils"},
        {"task_id": "task_001", "repo_group": "math_utils"},
    ]

    original = [task.copy() for task in tasks]

    group_tasks_for_cache(tasks)

    assert tasks == original