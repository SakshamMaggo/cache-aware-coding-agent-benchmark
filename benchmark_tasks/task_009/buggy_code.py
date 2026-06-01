import json


def build_cache_key(messages):
    cleaned = []

    for message in messages:
        cleaned.append(message)

    return json.dumps(cleaned)