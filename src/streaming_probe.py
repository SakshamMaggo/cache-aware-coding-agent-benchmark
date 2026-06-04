import csv
import os
import time
from pathlib import Path

from openai import OpenAI

from src.env_loader import load_env


OUTPUT_PATH = Path("results/streaming_probe.csv")


def build_probe_prompt() -> str:
    return (
        "Fix this Python function and return only the corrected code.\n\n"
        "Task:\n"
        "The function should remove duplicate prompt blocks. Blocks should be "
        "compared after lowercasing and normalizing whitespace, but the first "
        "readable version should be preserved in the output.\n\n"
        "Buggy code:\n"
        "def dedupe_prompt_blocks(blocks):\n"
        "    seen = set()\n"
        "    result = []\n\n"
        "    for block in blocks:\n"
        "        if block not in seen:\n"
        "            result.append(block)\n"
        "            seen.add(block)\n\n"
        "    return result\n"
    )


def make_client() -> tuple[OpenAI, str]:
    load_env()

    model = os.getenv("MODEL_NAME", "local-code-model")
    api_key = os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("MODEL_BASE_URL") or os.getenv("OPENAI_BASE_URL") or None

    if not api_key:
        raise ValueError("Set MODEL_API_KEY in your local .env file first.")

    client = OpenAI(api_key=api_key, base_url=base_url)
    return client, model


def run_streaming_probe() -> dict:
    client, model = make_client()
    prompt = build_probe_prompt()

    start = time.perf_counter()
    first_chunk_time = None
    output_parts = []

    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        stream=True,
    )

    for chunk in stream:
        if not chunk.choices:
            continue

        piece = chunk.choices[0].delta.content

        if not piece:
            continue

        now = time.perf_counter()

        if first_chunk_time is None:
            first_chunk_time = now

        output_parts.append(piece)

    end = time.perf_counter()

    output = "".join(output_parts)
    total_latency = end - start

    if first_chunk_time is None:
        time_to_first_chunk = total_latency
    else:
        time_to_first_chunk = first_chunk_time - start

    generation_time = max(total_latency - time_to_first_chunk, 0.000001)
    chars_per_second = len(output) / generation_time

    return {
        "model": model,
        "prompt_chars": len(prompt),
        "time_to_first_chunk_seconds": round(time_to_first_chunk, 4),
        "total_latency_seconds": round(total_latency, 4),
        "output_chars": len(output),
        "chars_per_second_after_first_chunk": round(chars_per_second, 2),
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    row = run_streaming_probe()

    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)

    print(f"Saved streaming probe to {OUTPUT_PATH}")
    print(row)


if __name__ == "__main__":
    main()