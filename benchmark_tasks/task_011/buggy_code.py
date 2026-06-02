def dedupe_prompt_blocks(blocks):
    seen = set()
    result = []

    for block in blocks:
        if block not in seen:
            result.append(block)
            seen.add(block)

    return result