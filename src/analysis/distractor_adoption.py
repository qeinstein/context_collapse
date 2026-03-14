import json
import re
import argparse
from pathlib import Path

import pandas as pd


def load_records(run_file: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in run_file.read_text(encoding="utf-8").splitlines()
    ]


def normalize_text(text: str) -> str:
    return text.strip().lower()


def contains_as_span(answer: str, noise_text: str) -> bool:
    """
    Conservative substring/span check.
    Uses word-boundary style matching when possible.
    """
    answer = answer.strip()
    noise_text = noise_text.strip()

    if not answer or not noise_text:
        return False

    pattern = r"\b" + re.escape(answer) + r"\b"
    return re.search(pattern, noise_text, flags=re.IGNORECASE) is not None


def flatten_records(records: list[dict]) -> pd.DataFrame:
    rows = []

    for r in records:
        raw_response = r["response"]["raw_text"]
        normalized_response = r["evaluation"]["normalized_response"]
        parsed_answer = r["evaluation"]["parsed_answer"]
        noise_text = r["noise_block"]["text"]

        distractor_adopted = (
            (not r["evaluation"]["is_correct"])
            and bool(parsed_answer.strip())
            and contains_as_span(parsed_answer, noise_text)
        )

        rows.append(
            {
                "trial_id": r["trial_id"],
                "run_id": r["run_id"],
                "task_id": r["task"]["task_id"],
                "task_family": r["task"]["task_family"],
                "condition_label": r["condition"]["condition_label"],
                "noise_type": r["condition"]["noise_type"],
                "noise_size_target": r["condition"]["noise_size_target"],
                "expected_answer": r["task"]["expected_answer"],
                "raw_response": raw_response,
                "normalized_response": normalized_response,
                "parsed_answer": parsed_answer,
                "noise_text": noise_text,
                "is_correct": bool(r["evaluation"]["is_correct"]),
                "is_compliant": bool(r["evaluation"]["is_compliant"]),
                "error_category": r["evaluation"]["error_category"],
                "distractor_adopted": bool(distractor_adopted),
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

    # Full per-trial table
    save_csv(df, analysis_dir / "distractor_adoption_per_trial.csv")

    # Overall by condition
    adoption_by_condition = (
        df.groupby(["condition_label", "noise_type", "noise_size_target"], as_index=False)
        .agg(
            n_trials=("trial_id", "count"),
            n_incorrect=("is_correct", lambda s: int((~s).sum())),
            distractor_adoptions=("distractor_adopted", "sum"),
            distractor_adoption_rate=("distractor_adopted", "mean"),
        )
        .sort_values(["noise_size_target", "condition_label"])
    )
    save_csv(adoption_by_condition, analysis_dir / "distractor_adoption_by_condition.csv")

    # Best view: retrieval only
    retrieval_df = df[df["task_family"] == "retrieval"].copy()

    adoption_by_condition_retrieval = (
        retrieval_df.groupby(["condition_label", "noise_type", "noise_size_target"], as_index=False)
        .agg(
            n_trials=("trial_id", "count"),
            n_incorrect=("is_correct", lambda s: int((~s).sum())),
            distractor_adoptions=("distractor_adopted", "sum"),
            distractor_adoption_rate=("distractor_adopted", "mean"),
        )
        .sort_values(["noise_size_target", "condition_label"])
    )
    save_csv(
        adoption_by_condition_retrieval,
        analysis_dir / "distractor_adoption_retrieval_only.csv",
    )

    # Per family
    adoption_by_family = (
        df.groupby(["task_family", "condition_label", "noise_type", "noise_size_target"], as_index=False)
        .agg(
            n_trials=("trial_id", "count"),
            n_incorrect=("is_correct", lambda s: int((~s).sum())),
            distractor_adoptions=("distractor_adopted", "sum"),
            distractor_adoption_rate=("distractor_adopted", "mean"),
        )
        .sort_values(["task_family", "noise_size_target", "condition_label"])
    )
    save_csv(adoption_by_family, analysis_dir / "distractor_adoption_by_family.csv")

    summary = {
        "run_file": str(run_file),
        "total_trials": int(len(df)),
        "total_incorrect": int((~df["is_correct"]).sum()),
        "total_distractor_adoptions": int(df["distractor_adopted"].sum()),
        "overall_distractor_adoption_rate": float(df["distractor_adopted"].mean()),
        "retrieval_trials": int(len(retrieval_df)),
        "retrieval_incorrect": int((~retrieval_df["is_correct"]).sum()) if len(retrieval_df) else 0,
        "retrieval_distractor_adoptions": int(retrieval_df["distractor_adopted"].sum()) if len(retrieval_df) else 0,
        "retrieval_distractor_adoption_rate": float(retrieval_df["distractor_adopted"].mean()) if len(retrieval_df) else 0.0,
    }

    with (analysis_dir / "distractor_adoption_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("run_file:", run_file)
    print("saved:", analysis_dir / "distractor_adoption_per_trial.csv")
    print("saved:", analysis_dir / "distractor_adoption_by_condition.csv")
    print("saved:", analysis_dir / "distractor_adoption_retrieval_only.csv")
    print("saved:", analysis_dir / "distractor_adoption_by_family.csv")
    print("saved:", analysis_dir / "distractor_adoption_summary.json")


if __name__ == "__main__":
    main()
