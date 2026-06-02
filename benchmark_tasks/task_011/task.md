Fix the prompt block deduper.

It should remove repeated prompt blocks even when whitespace or casing differs. It should keep the first readable version of each block and should not mutate the input list.