Fix the cache-aware task grouper.

It should group tasks by repo group while preserving the original order inside each group. Tasks without a repo group should be placed last. The function should not mutate the input list.