import json
import argparse
from pathlib import Path

import pandas as pd


def load_records(run_file: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in run_file.read_text(encoding="utf-8").splitlines()
    ]


def flatten_records(records: list[dict]) -> pd.DataFrame:
    rows = []

    for r in records:
        rows.append(
            {
                "trial_id": r["trial_id"],
                "run_id": r["run_id"],
                "model_name": r["model_name"],
                "task_id": r["task"]["task_id"],
                "task_family": r["task"]["task_family"],
                "expected_answer": r["task"]["expected_answer"],
                "condition_label": r["condition"]["condition_label"],
                "noise_type": r["condition"]["noise_type"],
                "noise_size_target": r["condition"]["noise_size_target"],
                "actual_noise_words": r["noise_block"]["actual_words"],
                "actual_noise_chars": r["noise_block"]["actual_chars"],
                "is_correct": bool(r["evaluation"]["is_correct"]),
                "is_compliant": bool(r["evaluation"]["is_compliant"]),
                "error_category": r["evaluation"]["error_category"],
                "latency_ms": float(r["response"]["latency_ms"]),
                "response_words": int(r["evaluation"]["response_words"]),
                "response_chars": int(r["evaluation"]["response_chars"]),
            }
        )

    return pd.DataFrame(rows)


def save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run",
        type=str,
        default="latest",
        help="Run file path or 'latest'",
    )
    args = parser.parse_args()

    if args.run == "latest":
        run_file = sorted(Path("data/runs").glob("*.jsonl"))[-1]
    else:
        run_file = Path(args.run)

    records = load_records(run_file)
    df = flatten_records(records)

    run_id = run_file.stem
    analysis_dir = Path("data/analysis") / run_id
    analysis_dir.mkdir(parents=True, exist_ok=True)

    # Accuracy by exact condition
    accuracy_by_condition = (
        df.groupby(["condition_label", "noise_type", "noise_size_target"], as_index=False)
        .agg(
            n_trials=("trial_id", "count"),
            accuracy=("is_correct", "mean"),
        )
        .sort_values(["noise_size_target", "condition_label"])
    )

    # Compliance by exact condition
    compliance_by_condition = (
        df.groupby(["condition_label", "noise_type", "noise_size_target"], as_index=False)
        .agg(
            n_trials=("trial_id", "count"),
            compliance_rate=("is_compliant", "mean"),
        )
        .sort_values(["noise_size_target", "condition_label"])
    )

    # Latency by exact condition
    latency_by_condition = (
        df.groupby(["condition_label", "noise_type", "noise_size_target"], as_index=False)
        .agg(
            n_trials=("trial_id", "count"),
            mean_latency_ms=("latency_ms", "mean"),
            median_latency_ms=("latency_ms", "median"),
            min_latency_ms=("latency_ms", "min"),
            max_latency_ms=("latency_ms", "max"),
        )
        .sort_values(["noise_size_target", "condition_label"])
    )

    # Accuracy by task family and condition
    accuracy_by_task_family = (
        df.groupby(
            ["task_family", "condition_label", "noise_type", "noise_size_target"],
            as_index=False,
        )
        .agg(
            n_trials=("trial_id", "count"),
            accuracy=("is_correct", "mean"),
            compliance_rate=("is_compliant", "mean"),
            mean_latency_ms=("latency_ms", "mean"),
            median_latency_ms=("latency_ms", "median"),
        )
        .sort_values(["task_family", "noise_size_target", "condition_label"])
    )

    # High-level overview
    overview = {
        "run_file": str(run_file),
        "run_id": run_id,
        "total_rows": int(len(df)),
        "total_correct": int(df["is_correct"].sum()),
        "total_incorrect": int((~df["is_correct"]).sum()),
        "total_compliant": int(df["is_compliant"].sum()),
        "total_noncompliant": int((~df["is_compliant"]).sum()),
        "overall_accuracy": float(df["is_correct"].mean()),
        "overall_compliance": float(df["is_compliant"].mean()),
        "mean_latency_ms": float(df["latency_ms"].mean()),
        "median_latency_ms": float(df["latency_ms"].median()),
        "task_families": sorted(df["task_family"].unique().tolist()),
        "conditions": sorted(df["condition_label"].unique().tolist()),
    }

    save_csv(accuracy_by_condition, analysis_dir / "accuracy_by_condition.csv")
    save_csv(compliance_by_condition, analysis_dir / "compliance_by_condition.csv")
    save_csv(latency_by_condition, analysis_dir / "latency_by_condition.csv")
    save_csv(accuracy_by_task_family, analysis_dir / "accuracy_by_task_family.csv")

    with (analysis_dir / "summary_overview.json").open("w", encoding="utf-8") as f:
        json.dump(overview, f, indent=2)

    print("run_file:", run_file)
    print("saved:", analysis_dir / "accuracy_by_condition.csv")
    print("saved:", analysis_dir / "compliance_by_condition.csv")
    print("saved:", analysis_dir / "latency_by_condition.csv")
    print("saved:", analysis_dir / "accuracy_by_task_family.csv")
    print("saved:", analysis_dir / "summary_overview.json")


if __name__ == "__main__":
    main()
