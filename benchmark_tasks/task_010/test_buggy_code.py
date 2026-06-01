from buggy_code import summarize_attempts


def test_counts_fixed_task_when_later_attempt_passes():
    traces = [
        {
            "task_id": "task_001",
            "attempts": [
                {"attempt": 1, "passed": False},
                {"attempt": 2, "passed": True},
            ],
        }
    ]

    assert summarize_attempts(traces)["fixed_tasks"] == 1


def test_counts_all_attempts():
    traces = [
        {
            "task_id": "task_001",
            "attempts": [
                {"attempt": 1, "passed": False},
                {"attempt": 2, "passed": True},
            ],
        },
        {
            "task_id": "task_002",
            "attempts": [
                {"attempt": 1, "passed": True},
            ],
        },
    ]

    assert summarize_attempts(traces)["total_attempts"] == 3


def test_handles_task_with_no_attempts():
    traces = [
        {
            "task_id": "task_001",
            "attempts": [],
        }
    ]

    assert summarize_attempts(traces) == {
        "total_tasks": 1,
        "fixed_tasks": 0,
        "total_attempts": 0,
    }


def test_counts_failed_task_correctly():
    traces = [
        {
            "task_id": "task_001",
            "attempts": [
                {"attempt": 1, "passed": False},
                {"attempt": 2, "passed": False},
            ],
        }
    ]

    assert summarize_attempts(traces)["fixed_tasks"] == 0