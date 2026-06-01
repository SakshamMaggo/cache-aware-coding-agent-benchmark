from buggy_code import merge_counts


def test_merges_new_keys():
    left = {"a": 2}
    right = {"b": 3}

    assert merge_counts(left, right) == {"a": 2, "b": 3}


def test_adds_existing_counts():
    left = {"a": 2}
    right = {"a": 3}

    assert merge_counts(left, right) == {"a": 5}


def test_does_not_mutate_left_input():
    left = {"a": 2}
    right = {"a": 3}

    merge_counts(left, right)

    assert left == {"a": 2}