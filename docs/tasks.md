# Task Set

This file summarizes the current benchmark tasks.

| task | group | bug type | difficulty | short description |
|---|---|---|---|---|
| task_001 | math_utils | wrong_operator | easy | Fix the add_numbers function. It currently subtracts instead of adding. |
| task_002 | math_utils | loop_boundary | easy | Fix the factorial function. It gives the wrong answer for normal factorial inputs. |
| task_003 | string_utils | case_normalization | easy | Fix the palindrome checker. It should ignore capitalization. |
| task_004 | string_utils | whitespace_handling | easy | Fix the word counter. It should handle empty strings and multiple spaces correctly. |
| task_005 | list_utils | bad_initial_value | easy | Fix the max finder. It should work correctly when all numbers are negative. |
| task_006 | list_utils | empty_input | easy | Fix the average function. It should return 0 for an empty list instead of crashing. |
| task_007 | file_utils | extension_handling | medium | Fix the file filter. It should return Python files from a list of paths and should handle `.py` extensions case-insensitively. |
| task_008 | dict_utils | mutation_and_merge_logic | medium | Fix the count merger. It should combine two count dictionaries by adding counts for existing keys. It should not mutate the input dictionaries. |
| task_009 | cache_utils | cache_key_normalization | medium | Fix the cache-key builder. It should create a stable key for chat-style prompt messages. The key should ignore volatile fields such as `request_id` and `timestamp`, normalize repeated whitespace inside message content, and avoid mutating the input messages. |
| task_010 | trace_utils | retry_trace_aggregation | medium | Fix the attempt summarizer. It receives repair traces where each task has a list of attempts. It should count total tasks, count all attempts across tasks, and count a task as fixed if any of its attempts passed. It should also handle tasks with no attempts. |
