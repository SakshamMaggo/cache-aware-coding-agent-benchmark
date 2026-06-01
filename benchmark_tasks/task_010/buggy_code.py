def summarize_attempts(traces):
    total_tasks = len(traces)
    fixed_tasks = 0
    total_attempts = 0

    for trace in traces:
        attempts = trace.get("attempts", [])
        total_attempts += 1

        if attempts[0]["passed"]:
            fixed_tasks += 1

    return {
        "total_tasks": total_tasks,
        "fixed_tasks": fixed_tasks,
        "total_attempts": total_attempts,
    }