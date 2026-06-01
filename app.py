from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.express as px


st.set_page_config(
    page_title="Cache-Aware Coding Agent Benchmark",
    layout="wide",
)

LABELS = {
    "normal_random": "baseline",
    "cache_aware_random": "cache-aware",
    "cache_aware_grouped": "grouped cache-aware",
}


def clean_name(name: str) -> str:
    return LABELS.get(name, name)


st.title("Cache-Aware Coding Agent Benchmark")

st.markdown(
    """
A small systems benchmark for checking whether coding-agent prompts can be arranged
to make repeated inference calls more cache-friendly.

The current prototype compares a normal prompt layout against a cache-aware layout.
The cache-aware version puts repeated content first: instructions, output rules,
tool protocol, and repo context.

**Status:** local prototype with a dummy backend. Prefix-reuse scores are real.
Latency and TTFT are simulated for now.
"""
)

results_path = Path("results/dummy_cache_benchmark_results.csv")
experiment_results_path = Path("results/experiment_results.csv")
if not results_path.exists():
    st.warning("No results found yet. Run `python -m src.runner` first.")
    st.stop()

df = pd.read_csv(results_path)
df["run"] = df["experiment"].apply(clean_name)

summary = (
    df.groupby(["experiment", "run"])
    .agg(
        prefix_reuse=("cacheability_score", "mean"),
        latency=("latency_seconds", "mean"),
        ttft=("ttft_seconds", "mean"),
        tokens_per_sec=("tokens_per_second", "mean"),
        prompt_tokens=("prompt_tokens", "mean"),
    )
    .reset_index()
)

baseline = summary.loc[summary["experiment"] == "normal_random"].iloc[0]
cache_aware = summary.loc[summary["experiment"] == "cache_aware_random"].iloc[0]
grouped = summary.loc[summary["experiment"] == "cache_aware_grouped"].iloc[0]

reuse_gain = grouped["prefix_reuse"] / max(baseline["prefix_reuse"], 0.0001)

st.divider()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Baseline prefix reuse", f"{baseline['prefix_reuse']:.3f}")
c2.metric("Cache-aware prefix reuse", f"{cache_aware['prefix_reuse']:.3f}")
c3.metric("Grouped run prefix reuse", f"{grouped['prefix_reuse']:.3f}")
c4.metric("Reuse gain vs baseline", f"{reuse_gain:.1f}x")

st.caption(
    "Prefix reuse is a proxy for how much of each prompt starts the same way as earlier prompts."
)

st.divider()

left, right = st.columns([1.15, 1])

with left:
    st.subheader("Prefix reuse")
    fig = px.bar(
        summary,
        x="prefix_reuse",
        y="run",
        orientation="h",
        text=summary["prefix_reuse"].round(3),
        labels={"prefix_reuse": "prefix reuse score", "run": ""},
        title="Cache-aware layouts create more reusable prompt prefixes",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=330,
        showlegend=False,
        xaxis_range=[0, 1],
        margin=dict(l=20, r=40, t=55, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("What this means")
    st.markdown(
        """
The baseline prompt starts with task-specific details, so every request begins differently.

The cache-aware prompt starts with shared instructions and repo context. This creates
much more overlap at the beginning of the prompt.

That matters because prefix caching and KV-cache reuse work best when many requests
share the same starting tokens.
"""
    )

st.divider()

left, right = st.columns([1.15, 1])

with left:
    st.subheader("Latency check")
    fig2 = px.bar(
        summary,
        x="latency",
        y="run",
        orientation="h",
        text=summary["latency"].round(4),
        labels={"latency": "seconds", "run": ""},
        title="Simulated latency, just to test the pipeline",
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(
        height=330,
        showlegend=False,
        margin=dict(l=20, r=40, t=55, b=20),
    )
    st.plotly_chart(fig2, use_container_width=True)

with right:
    st.subheader("Metrics")
    st.markdown(
        """
**TTFT** means *time to first token*.  
Unit: **seconds**.

Right now, TTFT and latency are simulated because the backend is fake.  
In the next version, these will come from real model calls.
"""
    )

st.divider()

st.subheader("Summary table")

display = summary[
    ["run", "prefix_reuse", "latency", "ttft", "tokens_per_sec", "prompt_tokens"]
].rename(
    columns={
        "run": "Run",
        "prefix_reuse": "Prefix reuse",
        "latency": "Latency, simulated",
        "ttft": "TTFT, simulated",
        "tokens_per_sec": "Tokens/sec, simulated",
        "prompt_tokens": "Prompt tokens",
    }
)

st.dataframe(display, use_container_width=True, hide_index=True)

st.subheader("Run log")

raw = df[
    [
        "task_id",
        "repo",
        "prompt_style",
        "ordering",
        "backend",
        "prompt_tokens",
        "cacheability_score",
        "latency_seconds",
        "ttft_seconds",
        "tokens_per_second",
    ]
].rename(
    columns={
        "task_id": "Task",
        "repo": "Repo",
        "prompt_style": "Prompt",
        "ordering": "Order",
        "backend": "Backend",
        "prompt_tokens": "Prompt tokens",
        "cacheability_score": "Prefix reuse",
        "latency_seconds": "Latency",
        "ttft_seconds": "TTFT",
        "tokens_per_second": "Tokens/sec",
    }
)

st.dataframe(raw, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Prompt layout experiment")

if experiment_results_path.exists():
    exp_df = pd.read_csv(experiment_results_path)

    exp_summary = (
        exp_df.groupby("experiment")
        .agg(
            avg_prefix_reuse=("prefix_reuse", "mean"),
            pass_rate=("after_passed", "mean"),
            avg_prompt_tokens=("prompt_tokens", "mean"),
            avg_fix_call_seconds=("fix_call_seconds", "mean"),
        )
        .reset_index()
    )

    label_map = {
        "normal_original": "normal prompt",
        "cache_original": "cache-aware prompt",
        "cache_grouped": "cache-aware grouped",
    }

    exp_summary["run"] = exp_summary["experiment"].map(label_map)

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Normal avg prefix reuse",
        f"{exp_summary.loc[exp_summary['experiment'] == 'normal_original', 'avg_prefix_reuse'].iloc[0]:.3f}",
    )
    c2.metric(
        "Cache-aware avg prefix reuse",
        f"{exp_summary.loc[exp_summary['experiment'] == 'cache_original', 'avg_prefix_reuse'].iloc[0]:.3f}",
    )
    c3.metric(
        "Repair pass rate",
        f"{exp_summary['pass_rate'].mean():.0%}",
    )

    fig_exp = px.bar(
        exp_summary,
        x="avg_prefix_reuse",
        y="run",
        orientation="h",
        text=exp_summary["avg_prefix_reuse"].round(3),
        labels={"avg_prefix_reuse": "average prefix reuse", "run": ""},
        title="Cache-aware prompt layout creates much more shared prefix",
    )
    fig_exp.update_traces(textposition="outside")
    fig_exp.update_layout(
        height=320,
        showlegend=False,
        xaxis_range=[0, 1],
        margin=dict(l=20, r=40, t=55, b=20),
    )
    st.plotly_chart(fig_exp, use_container_width=True)

    st.caption(
        "This experiment compares normal prompting against a cache-aware layout. The current backend is still the rule baseline, so the useful signal here is prefix structure and whether repair success stays unchanged."
    )

    st.dataframe(
        exp_summary.rename(
            columns={
                "run": "Run",
                "avg_prefix_reuse": "Avg prefix reuse",
                "pass_rate": "Pass rate",
                "avg_prompt_tokens": "Avg prompt tokens",
                "avg_fix_call_seconds": "Avg fix call time",
            }
        )[["Run", "Avg prefix reuse", "Pass rate", "Avg prompt tokens", "Avg fix call time"]],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No experiment results found yet. Run `python -m src.experiment_runner` first.")
st.subheader("Code task test results")

test_results_path = Path("results/task_test_results.csv")

if test_results_path.exists():
    test_df = pd.read_csv(test_results_path)

    total_tasks = len(test_df)
    passed_tasks = int(test_df["passed"].sum())
    failed_tasks = total_tasks - passed_tasks
    pass_rate = passed_tasks / total_tasks if total_tasks else 0

    tests_passed = int(test_df["tests_passed"].sum())
    tests_failed = int(test_df["tests_failed"].sum())
    total_tests = int(test_df["total_tests"].sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tasks", total_tasks)
    c2.metric("Passed", passed_tasks)
    c3.metric("Failed", failed_tasks)
    c4.metric("Pass rate", f"{pass_rate:.0%}")

    c5, c6, c7 = st.columns(3)
    c5.metric("Unit tests passed", tests_passed)
    c6.metric("Unit tests failed", tests_failed)
    c7.metric("Total unit tests", total_tests)

    clean_test_df = test_df.rename(
        columns={
            "task_id": "Task",
            "passed": "Passed",
            "tests_passed": "Tests passed",
            "tests_failed": "Tests failed",
            "total_tests": "Total tests",
            "runtime_seconds": "Runtime, seconds",
            "short_failure": "Failure summary",
        }
    )

    st.dataframe(clean_test_df, use_container_width=True, hide_index=True)

    st.caption(
    "These are the original buggy tasks. The repair section below shows whether the fixer can turn them into passing tasks."
    )
else:
    st.info("No task test results found yet. Run `python -m src.test_runner` first.")
st.divider()

st.subheader("Repair run")

repair_results_path = Path("results/repair_results.csv")

if repair_results_path.exists():
    repair_df = pd.read_csv(repair_results_path)

    total_repairs = len(repair_df)
    fixed_tasks = int(repair_df["after_passed"].sum())
    repair_rate = fixed_tasks / total_repairs if total_repairs else 0

    before_failed = int(repair_df["before_tests_failed"].sum())
    after_failed = int(repair_df["after_tests_failed"].sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Repair attempts", total_repairs)
    c2.metric("Fixed after repair", fixed_tasks)
    c3.metric("Repair rate", f"{repair_rate:.0%}")
    c4.metric("Failed tests", f"{before_failed} → {after_failed}")

repair_columns = [
    "task_id",
    "fixer",
    "model",
    "model_latency_seconds",
    "prompt_chars",
    "output_chars",
    "before_passed",
    "before_tests_failed",
    "after_passed",
    "after_tests_failed",
    "repair_runtime_seconds",
]

available_repair_columns = [
    col for col in repair_columns if col in repair_df.columns
]

clean_repair_df = repair_df[available_repair_columns].rename(
    columns={
        "task_id": "Task",
        "fixer": "Fixer",
        "model": "Model",
        "model_latency_seconds": "Fix call time, seconds",
        "prompt_chars": "Prompt chars",
        "output_chars": "Output chars",
        "before_passed": "Passed before",
        "before_tests_failed": "Failed tests before",
        "after_passed": "Passed after",
        "after_tests_failed": "Failed tests after",
        "repair_runtime_seconds": "Pytest time after repair",
    }
)

st.dataframe(clean_repair_df, use_container_width=True, hide_index=True)

st.caption(
        "This first repair run uses a small rule-based fixer. It is only a baseline to test the repair loop. Later, this gets replaced by a real LLM/coding-agent backend."
    )
trace_path = Path("results/repair_traces.jsonl")

if trace_path.exists():
        st.markdown("#### Repair traces")

        traces = []
        with open(trace_path, "r") as f:
            for line in f:
                traces.append(json.loads(line))

        selected_task = st.selectbox(
            "Choose a task to inspect",
            [trace["task_id"] for trace in traces],
        )

        selected_trace = next(
            trace for trace in traces if trace["task_id"] == selected_task
        )

        left, right = st.columns(2)

        with left:
            st.markdown("**Before repair**")
            st.code(selected_trace["before_code"], language="python")

        with right:
            st.markdown("**After repair**")
            st.code(selected_trace["after_code"], language="python")
else:
    st.info("No repair results found yet. Run `python -m src.repair_runner` first.")
st.subheader("Next milestones")

st.markdown(
    """
1. Replace the dummy backend with real model calls.
2. Add real code-repair tasks with unit tests.
3. Measure pass rate, retries, latency, TTFT, and tokens/sec.
4. Add vLLM/SGLang-compatible serving.
5. Compare normal prompting, cache-aware prompting, and grouped scheduling.
"""
)