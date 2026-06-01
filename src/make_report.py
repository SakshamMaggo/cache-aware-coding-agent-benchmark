from pathlib import Path

import pandas as pd


DOC_PATH = Path("docs/latest_run.md")
EXPERIMENT_PATH = Path("results/experiment_results.csv")
BACKEND_PATH = Path("results/backend_comparison.csv")
REPAIR_PATH = Path("results/repair_results.csv")
ATTEMPT_PATH = Path("results/attempt_results.csv")

MODEL_REPAIR_PATH = Path("examples/sample_model_repair_results.csv")
MODEL_ATTEMPT_PATH = Path("examples/sample_model_attempt_results.csv")
MODEL_EXPERIMENT_PATH = Path("examples/sample_model_experiment_results.csv")

def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run the benchmark first.")

    return pd.read_csv(path)


def add_model_sample(lines: list[str]) -> None:
    if not MODEL_REPAIR_PATH.exists() or not MODEL_ATTEMPT_PATH.exists():
        return
def add_model_experiment_sample(lines: list[str]) -> None:
    if not MODEL_EXPERIMENT_PATH.exists():
        return

    model_exp_df = pd.read_csv(MODEL_EXPERIMENT_PATH)

    summary = (
        model_exp_df.groupby("experiment")
        .agg(
            tasks=("task_id", "count"),
            pass_rate=("after_passed", "mean"),
            recent_reuse=("recent_prefix_reuse", "mean"),
            avg_latency=("model_latency_seconds", "mean"),
        )
        .reset_index()
    )

    lines.extend(
        [
            "",
            "## Model prompt experiment sample",
            "",
            "| run | tasks | pass rate | recent reuse | avg model call time |",
            "|---|---:|---:|---:|---:|",
        ]
    )

    for _, row in summary.iterrows():
        lines.append(
            "| "
            f"{row['experiment']} | "
            f"{int(row['tasks'])} | "
            f"{pct(row['pass_rate'])} | "
            f"{row['recent_reuse']:.3f} | "
            f"{row['avg_latency']:.2f}s |"
        )

    lines.extend(
        [
            "",
            "This sample is saved under `examples/sample_model_experiment_results.csv`. It is not run in CI because it needs a private API key.",
        ]
    )
    model_repair_df = pd.read_csv(MODEL_REPAIR_PATH)
    model_attempt_df = pd.read_csv(MODEL_ATTEMPT_PATH)

    model_name = model_repair_df["model"].iloc[0]
    total_tasks = len(model_repair_df)
    fixed_tasks = int(model_repair_df["after_passed"].sum())

    avg_latency = model_attempt_df["model_latency_seconds"].mean()
    avg_prompt_chars = model_attempt_df["prompt_chars"].mean()
    avg_output_chars = model_attempt_df["output_chars"].mean()

    lines.extend(
        [
            "",
            "## Model sample run",
            "",
            f"- model: {model_name}",
            f"- fixed tasks: {fixed_tasks}/{total_tasks}",
            f"- avg model call time: {avg_latency:.2f} seconds",
            f"- avg prompt chars: {avg_prompt_chars:.1f}",
            f"- avg output chars: {avg_output_chars:.1f}",
            "",
            "This sample is saved under `examples/`. It is not run in CI because it needs a private API key.",
        ]
    )


def main() -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)

    exp_df = read_csv(EXPERIMENT_PATH)
    backend_df = read_csv(BACKEND_PATH)
    repair_df = read_csv(REPAIR_PATH)
    attempt_df = read_csv(ATTEMPT_PATH)

    exp_summary = (
        exp_df.groupby("experiment")
        .agg(
            recent_reuse=("recent_prefix_reuse", "mean"),
            best_reuse=("best_prefix_reuse", "mean"),
            pass_rate=("after_passed", "mean"),
            avg_prompt_tokens=("prompt_tokens", "mean"),
        )
        .reset_index()
    )

    lines = [
        "# Latest Run",
        "",
        "This is a quick summary from the latest local run.",
        "",
        "## Prompt layout",
        "",
        "| run | recent reuse | best reuse | pass rate | avg prompt tokens |",
        "|---|---:|---:|---:|---:|",
    ]

    for _, row in exp_summary.iterrows():
        lines.append(
            "| "
            f"{row['experiment']} | "
            f"{row['recent_reuse']:.3f} | "
            f"{row['best_reuse']:.3f} | "
            f"{pct(row['pass_rate'])} | "
            f"{row['avg_prompt_tokens']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Backend comparison",
            "",
            "| backend | tasks | pass rate | avg attempts | failed tests after |",
            "|---|---:|---:|---:|---:|",
        ]
    )

    for _, row in backend_df.iterrows():
        lines.append(
            "| "
            f"{row['backend_run']} | "
            f"{int(row['tasks'])} | "
            f"{pct(row['pass_rate'])} | "
            f"{row['avg_attempts']:.2f} | "
            f"{int(row['failed_tests_after'])} |"
        )

    total_tasks = len(repair_df)
    fixed_tasks = int(repair_df["after_passed"].sum())
    attempt_rows = len(attempt_df)
    max_attempts_used = int(repair_df["attempts_used"].max())

    lines.extend(
        [
            "",
            "## Repair run",
            "",
            f"- fixed tasks: {fixed_tasks}/{total_tasks}",
            f"- attempt rows logged: {attempt_rows}",
            f"- max attempts used by any task: {max_attempts_used}",
        ]
    )

    add_model_sample(lines)
    add_model_experiment_sample(lines)
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- The default local run still uses the rule baseline.",
            "- The model sample run is saved separately, so CI does not need a private API key.",
            "- The main useful result right now is that prompt layout and task order change prefix reuse a lot.",
            "- The next serious step is to test the same setup on less toy-like repair tasks.",
            "",
        ]
    )

    DOC_PATH.write_text("\n".join(lines))
    print(f"Saved report to {DOC_PATH}")


if __name__ == "__main__":
    main()