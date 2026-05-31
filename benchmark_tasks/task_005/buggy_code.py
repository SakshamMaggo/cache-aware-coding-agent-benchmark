def find_max(nums):
    current = 0
    for x in nums:
        if x > current:
            current = x
    return current