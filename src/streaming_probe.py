import csv
import time
from pathlib import Path

from src.model_client import OpenAICompatibleModelClient


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


def run_streaming_probe() -> dict:
    model_client = OpenAICompatibleModelClient()
    prompt = build_probe_prompt()

    start = time.perf_counter()
    first_chunk_time = None
    output_parts = []

    stream = model_client.client.chat.completions.create(
        model=model_client.model,
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
        "model": model_client.model,
        "backend_type": model_client.backend_type,
        "base_url": model_client.base_url or "",
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
