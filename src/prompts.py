SHARED_AGENT_INSTRUCTIONS = """You are a careful coding agent.
Your goal is to fix a small Python bug while preserving the original intent of the program.

Rules:
1. Read the task carefully.
2. Identify the likely bug.
3. Produce the smallest correct fix.
4. Do not rewrite unrelated code.
5. Prefer simple, readable Python.
6. The final answer should include a short explanation and the corrected code.
"""

SHARED_OUTPUT_FORMAT = """Output format:
- Bug summary:
- Fix explanation:
- Corrected code:
"""

SHARED_REPO_CONTEXT = """Repository context:
This benchmark contains small Python functions and unit tests.
Each task asks the agent to repair one buggy function.
The tests are deterministic and check edge cases.
"""


def build_normal_prompt(task: dict) -> str:
    """
    Normal prompt layout:
    Task-specific details come first.
    This is less prefix-cache friendly because each prompt starts differently.
    """
    return (
        f"Task ID: {task['task_id']}\n"
        f"Repository: {task['repo']}\n"
        f"Language: {task['language']}\n\n"
        f"Problem:\n{task['description']}\n\n"
        f"Buggy code:\n{task['buggy_code']}\n\n"
        f"{SHARED_AGENT_INSTRUCTIONS}\n"
        f"{SHARED_REPO_CONTEXT}\n"
        f"{SHARED_OUTPUT_FORMAT}\n"
    )


def build_cache_aware_prompt(task: dict) -> str:
    """
    Cache-aware prompt layout:
    Shared instructions and shared repo context come first.
    Task-specific details come later.
    This should be more prefix-cache friendly when many prompts share the same prefix.
    """
    return (
        f"{SHARED_AGENT_INSTRUCTIONS}\n"
        f"{SHARED_REPO_CONTEXT}\n"
        f"{SHARED_OUTPUT_FORMAT}\n"
        f"Task-specific section:\n"
        f"Task ID: {task['task_id']}\n"
        f"Repository: {task['repo']}\n"
        f"Language: {task['language']}\n\n"
        f"Problem:\n{task['description']}\n\n"
        f"Buggy code:\n{task['buggy_code']}\n"
    )