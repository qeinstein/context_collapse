import json
import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


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
                "task_id": r["task"]["task_id"],
                "task_family": r["task"]["task_family"],
                "condition_label": r["condition"]["condition_label"],
                "noise_type": r["condition"]["noise_type"],
                "noise_size_target": r["condition"]["noise_size_target"],
                "is_correct": bool(r["evaluation"]["is_correct"]),
                "is_compliant": bool(r["evaluation"]["is_compliant"]),
                "latency_ms": float(r["response"]["latency_ms"]),
            }
        )

    return pd.DataFrame(rows)


def save_plot(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", dpi=160)
    plt.close(fig)


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

    # -------- accuracy vs context size by noise type --------
    acc = (
        df.groupby(["noise_type", "noise_size_target"], as_index=False)
        .agg(accuracy=("is_correct", "mean"))
        .sort_values(["noise_type", "noise_size_target"])
    )

    fig = plt.figure(figsize=(7, 4.5))
    for noise_type, sub in acc.groupby("noise_type"):
        plt.plot(sub["noise_size_target"], sub["accuracy"], marker="o", label=noise_type)
    plt.xlabel("Noise size target")
    plt.ylabel("Accuracy")
    plt.title("Accuracy vs Context Size")
    plt.ylim(0, 1.05)
    plt.legend()
    save_plot(fig, analysis_dir / "accuracy_vs_context_size.png")

    # -------- latency vs context size by noise type --------
    lat = (
        df.groupby(["noise_type", "noise_size_target"], as_index=False)
        .agg(median_latency_ms=("latency_ms", "median"))
        .sort_values(["noise_type", "noise_size_target"])
    )

    fig = plt.figure(figsize=(7, 4.5))
    for noise_type, sub in lat.groupby("noise_type"):
        plt.plot(sub["noise_size_target"], sub["median_latency_ms"], marker="o", label=noise_type)
    plt.xlabel("Noise size target")
    plt.ylabel("Median latency (ms)")
    plt.title("Latency vs Context Size")
    plt.legend()
    save_plot(fig, analysis_dir / "latency_vs_context_size.png")

    # -------- condition-level accuracy bar chart --------
    acc_condition = (
        df.groupby(["condition_label"], as_index=False)
        .agg(accuracy=("is_correct", "mean"))
        .sort_values("condition_label")
    )

    fig = plt.figure(figsize=(9, 4.5))
    plt.bar(acc_condition["condition_label"], acc_condition["accuracy"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Accuracy")
    plt.title("Accuracy by Condition")
    plt.ylim(0, 1.05)
    save_plot(fig, analysis_dir / "accuracy_by_condition.png")

    # -------- accuracy by task family --------
    acc_family = (
        df.groupby(["task_family", "noise_type", "noise_size_target"], as_index=False)
        .agg(accuracy=("is_correct", "mean"))
        .sort_values(["task_family", "noise_type", "noise_size_target"])
    )

    for family, sub in acc_family.groupby("task_family"):
        fig = plt.figure(figsize=(7, 4.5))
        for noise_type, sub2 in sub.groupby("noise_type"):
            plt.plot(sub2["noise_size_target"], sub2["accuracy"], marker="o", label=noise_type)
        plt.xlabel("Noise size target")
        plt.ylabel("Accuracy")
        plt.title(f"Accuracy vs Context Size — {family}")
        plt.ylim(0, 1.05)
        plt.legend()
        save_plot(fig, analysis_dir / f"accuracy_vs_context_size_{family}.png")

    # -------- compliance by condition --------
    comp = (
        df.groupby(["condition_label"], as_index=False)
        .agg(compliance_rate=("is_compliant", "mean"))
        .sort_values("condition_label")
    )

    fig = plt.figure(figsize=(9, 4.5))
    plt.bar(comp["condition_label"], comp["compliance_rate"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Compliance rate")
    plt.title("Compliance by Condition")
    plt.ylim(0, 1.05)
    save_plot(fig, analysis_dir / "compliance_by_condition.png")

    print("run_file:", run_file)
    print("saved:", analysis_dir / "accuracy_vs_context_size.png")
    print("saved:", analysis_dir / "latency_vs_context_size.png")
    print("saved:", analysis_dir / "accuracy_by_condition.png")
    print("saved:", analysis_dir / "compliance_by_condition.png")
    for family in sorted(df["task_family"].unique()):
        print("saved:", analysis_dir / f"accuracy_vs_context_size_{family}.png")


if __name__ == "__main__":
    main()
