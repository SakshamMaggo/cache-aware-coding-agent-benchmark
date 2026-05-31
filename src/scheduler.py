def random_order(tasks: list[dict]) -> list[dict]:
    """
    Keeps the default task order.
    Later we can add true randomization with a seed.
    """
    return list(tasks)


def cache_aware_order(tasks: list[dict]) -> list[dict]:
    """
    Groups tasks by repository and language.
    The idea: similar tasks should share longer prompt prefixes/context,
    improving possible KV-cache reuse.
    """
    return sorted(tasks, key=lambda task: (task["repo"], task["language"], task["task_id"]))