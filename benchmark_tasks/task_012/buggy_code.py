def group_tasks_for_cache(tasks):
    return sorted(tasks, key=lambda task: task["repo_group"])