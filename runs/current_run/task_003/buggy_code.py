def is_palindrome(text):
    text = text.lower()
    return text == text[::-1]
