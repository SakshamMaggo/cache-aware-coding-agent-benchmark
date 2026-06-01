from buggy_code import build_cache_key


def test_ignores_volatile_fields():
    messages_a = [
        {
            "role": "system",
            "content": "Fix the bug.",
            "request_id": "abc",
            "timestamp": "10:00",
        },
        {
            "role": "user",
            "content": "def add(a, b): return a - b",
        },
    ]

    messages_b = [
        {
            "role": "system",
            "content": "Fix the bug.",
            "request_id": "xyz",
            "timestamp": "11:30",
        },
        {
            "role": "user",
            "content": "def add(a, b): return a - b",
        },
    ]

    assert build_cache_key(messages_a) == build_cache_key(messages_b)


def test_normalizes_extra_whitespace():
    messages_a = [
        {"role": "system", "content": "Fix the bug."},
        {"role": "user", "content": "def add(a, b):\n    return a - b"},
    ]

    messages_b = [
        {"role": "system", "content": "  Fix   the bug.  "},
        {"role": "user", "content": "def add(a, b):\n\n    return a - b"},
    ]

    assert build_cache_key(messages_a) == build_cache_key(messages_b)


def test_different_content_gets_different_key():
    messages_a = [
        {"role": "system", "content": "Fix the bug."},
        {"role": "user", "content": "return a - b"},
    ]

    messages_b = [
        {"role": "system", "content": "Fix the bug."},
        {"role": "user", "content": "return a + b"},
    ]

    assert build_cache_key(messages_a) != build_cache_key(messages_b)


def test_does_not_mutate_input():
    messages = [
        {
            "role": "system",
            "content": "Fix the bug.",
            "request_id": "abc",
        }
    ]

    build_cache_key(messages)

    assert messages == [
        {
            "role": "system",
            "content": "Fix the bug.",
            "request_id": "abc",
        }
    ]