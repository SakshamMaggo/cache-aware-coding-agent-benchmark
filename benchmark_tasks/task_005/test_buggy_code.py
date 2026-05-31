from buggy_code import find_max


def test_positive_numbers():
    assert find_max([1, 4, 2]) == 4


def test_negative_numbers():
    assert find_max([-5, -2, -9]) == -2


def test_single_number():
    assert find_max([-7]) == -7