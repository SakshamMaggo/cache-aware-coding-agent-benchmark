from pathlib import Path


def get_python_files(paths):
    files = []

    for path in paths:
        path = Path(path)

        if path.suffix == "py":
            files.append(str(path))

    return files