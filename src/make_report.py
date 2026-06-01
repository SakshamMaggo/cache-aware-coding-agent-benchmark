from pathlib import Path

import pandas as pd


DOC_PATH = Path("docs/latest_run.md")
EXPERIMENT_PATH = Path("results/experiment_results.csv")
BACKEND_PATH = Path("results/backend_comparison.csv")
REPAIR_PATH = Path("results/repair_results.csv")
ATTEMPT_PATH = Path("results/attempt_results.csv")


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run the benchmark first.")

    return pd.read_csv(path)


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
            "",
            "## Notes",
            "",
            "- The current repair backend is still the rule baseline.",
            "- The timing numbers are not real LLM inference timings yet.",
            "- The main useful result right now is that prompt layout and task order change prefix reuse a lot, even before using a real model backend.",
            "- A model-server run can use the same scripts later.",
            "",
        ]
    )

    DOC_PATH.write_text("\n".join(lines))
    print(f"Saved report to {DOC_PATH}")


if __name__ == "__main__":
    main()