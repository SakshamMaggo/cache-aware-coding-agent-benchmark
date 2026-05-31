import time
from difflib import SequenceMatcher

try:
    import tiktoken
except ImportError:
    tiktoken = None


def now_seconds() -> float:
    return time.perf_counter()


def count_tokens(text: str) -> int:
    """
    Approximate token counting.
    Uses tiktoken if available; falls back to rough word-based approximation.
    """
    if tiktoken is not None:
        try:
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except Exception:
            pass

    # Rough fallback: 1 token ~= 0.75 words / punctuation chunks
    return max(1, int(len(text.split()) * 1.3))


def shared_prefix_chars(a: str, b: str) -> int:
    """
    Counts exact matching characters from the start of two strings.
    Prefix caching benefits from identical prefixes, so exact prefix overlap matters.
    """
    limit = min(len(a), len(b))
    i = 0
    while i < limit and a[i] == b[i]:
        i += 1
    return i


def cacheability_score(prompt: str, previous_prompts: list[str]) -> float:
    """
    Measures how much of this prompt's beginning is shared with earlier prompts.
    Score is between 0 and 1.
    """
    if not previous_prompts or not prompt:
        return 0.0

    best_prefix = max(shared_prefix_chars(prompt, old_prompt) for old_prompt in previous_prompts)
    return round(best_prefix / len(prompt), 4)


def similarity_score(a: str, b: str) -> float:
    """
    General text similarity, not prefix-specific.
    Useful for diagnostics but less important than exact prefix overlap.
    """
    return round(SequenceMatcher(None, a, b).ratio(), 4)