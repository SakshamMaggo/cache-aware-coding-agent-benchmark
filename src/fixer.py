from pathlib import Path


def generate_rule_based_fix(task_id: str, buggy_code: str) -> str:
    """
    A tiny rule-based fixer for the first three toy tasks.

    This is not the final coding agent. It is a baseline that lets us test
    the full repair pipeline before adding real LLM calls.
    """
    if task_id in {"task_001", "tsk_001"}:
        return """def add_numbers(a, b):
    return a + b
"""

    if task_id in {"task_002", "tsk_002"}:
        return """def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
"""

    if task_id in {"task_003", "tsk_003"}:
        return """def is_palindrome(text):
    text = text.lower()
    return text == text[::-1]
"""
    if task_id in {"task_004", "tsk_004"}:
        return """def count_words(text):
    return len(text.split())
"""

    if task_id in {"task_005", "tsk_005"}:
        return """def find_max(nums):
    current = nums[0]
    for x in nums:
        if x > current:
            current = x
    return current
"""

    if task_id in {"task_006", "tsk_006"}:
        return """def average(nums):
    if not nums:
        return 0
    return sum(nums) / len(nums)
"""
    return buggy_code


def apply_fix_to_task(task_dir: Path) -> None:
    """
    Reads buggy_code.py and overwrites it with the generated fix.
    """
    task_id = task_dir.name
    code_path = task_dir / "buggy_code.py"

    if not code_path.exists():
        raise FileNotFoundError(f"Missing buggy_code.py in {task_dir}")

    buggy_code = code_path.read_text()
    fixed_code = generate_rule_based_fix(task_id, buggy_code)

    code_path.write_text(fixed_code)