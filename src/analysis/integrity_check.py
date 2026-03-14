import json
import argparse
from collections import Counter
# from pathlib import Path
from pathlib import Path
import json



def load_records(run_file: Path):
    return [
        json.loads(line)
        for line in run_file.read_text(encoding="utf-8").splitlines()
    ]


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run",
        type=str,
        default="latest",
        help="Run file path or 'latest'"
    )

    args = parser.parse_args()

    if args.run == "latest":
        run_file = sorted(Path("data/runs").glob("*.jsonl"))[-1]
    else:
        run_file = Path(args.run)

    records = load_records(run_file)

    print("run_file:", run_file)
    print("rows:", len(records))

    correct = sum(r["evaluation"]["is_correct"] for r in records)
    compliant = sum(r["evaluation"]["is_compliant"] for r in records)

    print("correct:", correct)
    print("compliant:", compliant)

    family_counts = Counter(r["task"]["task_family"] for r in records)
    condition_counts = Counter(r["condition"]["condition_label"] for r in records)
    task_counts = Counter(r["task"]["task_id"] for r in records)

    print("\nFamily counts")
    print(dict(sorted(family_counts.items())))

    print("\nCondition counts")
    print(dict(sorted(condition_counts.items())))

    print("\nUnique tasks:", len(task_counts))
    print("Min task repeats:", min(task_counts.values()))
    print("Max task repeats:", max(task_counts.values()))

    incorrect = [r for r in records if not r["evaluation"]["is_correct"]]
    noncompliant = [r for r in records if not r["evaluation"]["is_compliant"]]

    print("\nIncorrect rows:", len(incorrect))
    print("Noncompliant rows:", len(noncompliant))

    run_id = run_file.stem

    analysis_dir = Path("data/analysis") / run_id
    analysis_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "run_file": str(run_file),
        "rows": len(records),
        "correct": correct,
        "compliant": compliant,
        "family_counts": dict(sorted(family_counts.items())),
        "condition_counts": dict(sorted(condition_counts.items())),
        "unique_tasks": len(task_counts),
        "min_task_repeats": min(task_counts.values()),
        "max_task_repeats": max(task_counts.values()),
        "incorrect_rows": len(incorrect),
        "noncompliant_rows": len(noncompliant),
    }

    output_file = analysis_dir / "integrity_summary.json"

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\nSaved summary to:", output_file)



if __name__ == "__main__":
    main()
