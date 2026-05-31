from buggy_code import is_palindrome


def test_simple_palindrome():
    assert is_palindrome("madam") is True


def test_capitalized_palindrome():
    assert is_palindrome("Racecar") is True


def test_not_palindrome():
    assert is_palindrome("hello") is False