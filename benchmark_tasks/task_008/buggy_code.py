def merge_counts(left, right):
    result = left

    for key, value in right.items():
        result[key] = value

    return result