from buggy_code import get_python_files


def test_finds_python_files():
    paths = ["app.py", "README.md", "src/main.py"]
    assert get_python_files(paths) == ["app.py", "src/main.py"]


def test_ignores_non_python_files():
    paths = ["notes.txt", "data.csv", "image.png"]
    assert get_python_files(paths) == []


def test_handles_uppercase_extension():
    paths = ["SCRIPT.PY", "module.py"]
    assert get_python_files(paths) == ["SCRIPT.PY", "module.py"]