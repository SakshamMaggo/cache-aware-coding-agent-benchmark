from pathlib import Path

from src.fixer import generate_rule_based_fix


class BaseFixer:
    name = "base"

    def fix(self, task_id: str, task_text: str, buggy_code: str) -> str:
        raise NotImplementedError("Every fixer needs its own fix method.")


class RuleFixer(BaseFixer):
    """
    Tiny baseline fixer for the first toy tasks.

    This is not meant to be smart. It just gives us a clean repair loop before
    plugging in an actual model backend later.
    """

    name = "rule_baseline"

    def fix(self, task_id: str, task_text: str, buggy_code: str) -> str:
        return generate_rule_based_fix(task_id, buggy_code)


def read_task_text(task_dir: Path) -> str:
    task_file = task_dir / "task.md"

    if not task_file.exists():
        return ""

    return task_file.read_text().strip()