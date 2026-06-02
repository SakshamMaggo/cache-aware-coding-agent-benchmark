from buggy_code import dedupe_prompt_blocks


def test_dedupes_same_block_with_extra_spaces():
    blocks = [
        "Fix the bug carefully.",
        "  Fix   the bug carefully.  ",
        "Return only the fixed code.",
    ]

    assert dedupe_prompt_blocks(blocks) == [
        "Fix the bug carefully.",
        "Return only the fixed code.",
    ]


def test_keeps_first_readable_version():
    blocks = [
        "Shared repo context",
        "shared repo context",
        "Task-specific details",
    ]

    assert dedupe_prompt_blocks(blocks) == [
        "Shared repo context",
        "Task-specific details",
    ]


def test_does_not_mutate_input():
    blocks = [
        "Fix the bug carefully.",
        "  Fix   the bug carefully.  ",
    ]

    dedupe_prompt_blocks(blocks)

    assert blocks == [
        "Fix the bug carefully.",
        "  Fix   the bug carefully.  ",
    ]


def test_keeps_different_blocks():
    blocks = [
        "Fix arithmetic bugs.",
        "Fix string bugs.",
        "Fix list bugs.",
    ]

    assert dedupe_prompt_blocks(blocks) == blocks