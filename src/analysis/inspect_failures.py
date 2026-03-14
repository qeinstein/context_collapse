import json
import csv
import argparse
from pathlib import Path


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

    bad = [
        r for r in records
        if (not r["evaluation"]["is_correct"])
        or (not r["evaluation"]["is_compliant"])
    ]

    run_id = run_file.stem
    analysis_dir = Path("data/analysis") / run_id
    analysis_dir.mkdir(parents=True, exist_ok=True)

    # Save full structured failures as JSON
    json_output = analysis_dir / "failure_cases.json"
    with json_output.open("w", encoding="utf-8") as f:
        json.dump(bad, f, indent=2, ensure_ascii=False)

    # Save a flattened CSV view for quick inspection
    csv_output = analysis_dir / "failure_cases.csv"
    with csv_output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "task_id",
                "task_family",
                "condition_label",
                "noise_type",
                "noise_size_target",
                "expected_answer",
                "raw_response",
                "normalized_response",
                "is_correct",
                "is_compliant",
                "error_category",
                "latency_ms",
            ],
        )
        writer.writeheader()

        for r in bad:
            writer.writerow(
                {
                    "task_id": r["task"]["task_id"],
                    "task_family": r["task"]["task_family"],
                    "condition_label": r["condition"]["condition_label"],
                    "noise_type": r["condition"]["noise_type"],
                    "noise_size_target": r["condition"]["noise_size_target"],
                    "expected_answer": r["task"]["expected_answer"],
                    "raw_response": r["response"]["raw_text"],
                    "normalized_response": r["evaluation"]["normalized_response"],
                    "is_correct": r["evaluation"]["is_correct"],
                    "is_compliant": r["evaluation"]["is_compliant"],
                    "error_category": r["evaluation"]["error_category"],
                    "latency_ms": r["response"]["latency_ms"],
                }
            )

    print("run_file:", run_file)
    print("bad_rows:", len(bad))
    print("saved_json:", json_output)
    print("saved_csv:", csv_output)

    # Print a short preview too
    for r in bad[:10]:
        print("=" * 80)
        print("task_id:", r["task"]["task_id"])
        print("family:", r["task"]["task_family"])
        print("condition:", r["condition"]["condition_label"])
        print("expected:", r["task"]["expected_answer"])
        print("raw_response:", repr(r["response"]["raw_text"]))
        print("normalized:", repr(r["evaluation"]["normalized_response"]))
        print("correct:", r["evaluation"]["is_correct"])
        print("compliant:", r["evaluation"]["is_compliant"])
        print("error_category:", r["evaluation"]["error_category"])


if __name__ == "__main__":
    main()
