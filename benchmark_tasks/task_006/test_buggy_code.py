from buggy_code import average


def test_average_normal_list():
    assert average([2, 4, 6]) == 4


def test_average_single_value():
    assert average([10]) == 10


def test_average_empty_list():
    assert average([]) == 0