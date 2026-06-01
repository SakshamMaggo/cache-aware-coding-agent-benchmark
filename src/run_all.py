import subprocess


COMMANDS = [
    ["python", "-m", "src.test_runner"],
    ["python", "-m", "src.repair_runner", "--fixer", "rule", "--max-attempts", "2"],
    ["python", "-m", "src.trace_analyzer"],
    ["python", "-m", "src.experiment_runner"],
    ["python", "-m", "src.backend_compare"],
    ["python", "-m", "src.make_tasks_doc"],
    ["python", "-m", "src.make_report"],
]


def main() -> None:
    for cmd in COMMANDS:
        print("")
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)

    print("")
    print("Done. Latest report is in docs/latest_run.md")


if __name__ == "__main__":
    main()