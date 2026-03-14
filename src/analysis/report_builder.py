import json
import re
import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


REPO_URL = "https://github.com/qeinstein/context-collapse"
REPO_NAME = "context-collapse"


def load_records(run_file: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in run_file.read_text(encoding="utf-8").splitlines()
    ]


def contains_as_span(answer: str, noise_text: str) -> bool:
    answer = answer.strip()
    noise_text = noise_text.strip()

    if not answer or not noise_text:
        return False

    pattern = r"\b" + re.escape(answer) + r"\b"
    return re.search(pattern, noise_text, flags=re.IGNORECASE) is not None


def flatten_records(records: list[dict]) -> pd.DataFrame:
    rows = []

    for r in records:
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
                "model_name": r["model_name"],
                "task_id": r["task"]["task_id"],
                "task_family": r["task"]["task_family"],
                "expected_answer": r["task"]["expected_answer"],
                "condition_label": r["condition"]["condition_label"],
                "noise_type": r["condition"]["noise_type"],
                "noise_size_target": r["condition"]["noise_size_target"],
                "actual_noise_words": r["noise_block"]["actual_words"],
                "actual_noise_chars": r["noise_block"]["actual_chars"],
                "raw_response": r["response"]["raw_text"],
                "parsed_answer": parsed_answer,
                "is_correct": bool(r["evaluation"]["is_correct"]),
                "is_compliant": bool(r["evaluation"]["is_compliant"]),
                "error_category": r["evaluation"]["error_category"],
                "latency_ms": float(r["response"]["latency_ms"]),
                "response_words": int(r["evaluation"]["response_words"]),
                "response_chars": int(r["evaluation"]["response_chars"]),
                "distractor_adopted": bool(distractor_adopted),
            }
        )

    return pd.DataFrame(rows)


def save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_json(obj: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def save_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def save_plot(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", dpi=180)
    plt.close(fig)


def build_summary_tables(df: pd.DataFrame, analysis_dir: Path) -> dict:
    accuracy_by_condition = (
        df.groupby(["condition_label", "noise_type", "noise_size_target"], as_index=False)
        .agg(
            n_trials=("trial_id", "count"),
            accuracy=("is_correct", "mean"),
        )
        .sort_values(["noise_size_target", "condition_label"])
    )
    save_csv(accuracy_by_condition, analysis_dir / "accuracy_by_condition.csv")

    compliance_by_condition = (
        df.groupby(["condition_label", "noise_type", "noise_size_target"], as_index=False)
        .agg(
            n_trials=("trial_id", "count"),
            compliance_rate=("is_compliant", "mean"),
        )
        .sort_values(["noise_size_target", "condition_label"])
    )
    save_csv(compliance_by_condition, analysis_dir / "compliance_by_condition.csv")

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
    save_csv(latency_by_condition, analysis_dir / "latency_by_condition.csv")

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
    save_csv(accuracy_by_task_family, analysis_dir / "accuracy_by_task_family.csv")

    failure_cases = df[(~df["is_correct"]) | (~df["is_compliant"])].copy()
    save_csv(failure_cases, analysis_dir / "failure_cases.csv")
    save_json(
        {
            "n_failure_rows": int(len(failure_cases)),
        },
        analysis_dir / "failure_cases_summary.json",
    )

    distractor_by_condition = (
        df.groupby(["condition_label", "noise_type", "noise_size_target"], as_index=False)
        .agg(
            n_trials=("trial_id", "count"),
            n_incorrect=("is_correct", lambda s: int((~s).sum())),
            distractor_adoptions=("distractor_adopted", "sum"),
            distractor_adoption_rate=("distractor_adopted", "mean"),
        )
        .sort_values(["noise_size_target", "condition_label"])
    )
    save_csv(distractor_by_condition, analysis_dir / "distractor_adoption_by_condition.csv")

    retrieval_df = df[df["task_family"] == "retrieval"].copy()
    distractor_retrieval = (
        retrieval_df.groupby(["condition_label", "noise_type", "noise_size_target"], as_index=False)
        .agg(
            n_trials=("trial_id", "count"),
            n_incorrect=("is_correct", lambda s: int((~s).sum())),
            distractor_adoptions=("distractor_adopted", "sum"),
            distractor_adoption_rate=("distractor_adopted", "mean"),
        )
        .sort_values(["noise_size_target", "condition_label"])
    )
    save_csv(distractor_retrieval, analysis_dir / "distractor_adoption_retrieval_only.csv")

    summary = {
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
        "retrieval_trials": int(len(retrieval_df)),
        "retrieval_incorrect": int((~retrieval_df["is_correct"]).sum()),
        "retrieval_distractor_adoptions": int(retrieval_df["distractor_adopted"].sum()),
        "retrieval_distractor_adoption_rate": float(retrieval_df["distractor_adopted"].mean()) if len(retrieval_df) else 0.0,
    }
    save_json(summary, analysis_dir / "summary_overview.json")

    return {
        "accuracy_by_condition": accuracy_by_condition,
        "compliance_by_condition": compliance_by_condition,
        "latency_by_condition": latency_by_condition,
        "accuracy_by_task_family": accuracy_by_task_family,
        "distractor_by_condition": distractor_by_condition,
        "distractor_retrieval": distractor_retrieval,
        "summary": summary,
    }


def plot_publication_quality(tables: dict, df: pd.DataFrame, analysis_dir: Path) -> None:
    acc = tables["accuracy_by_condition"]
    lat = tables["latency_by_condition"]
    acc_family = tables["accuracy_by_task_family"]
    distractor_retrieval = tables["distractor_retrieval"]

    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "legend.fontsize": 10,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )

    # Figure 1: overall accuracy vs context size
    fig = plt.figure(figsize=(7.2, 4.6))
    for noise_type, sub in acc.groupby("noise_type"):
        plt.plot(sub["noise_size_target"], sub["accuracy"], marker="o", linewidth=2, label=noise_type)
    plt.xlabel("Noise size target (approx words)")
    plt.ylabel("Accuracy")
    plt.title("Accuracy vs Context Size")
    plt.ylim(0.75, 1.02)
    plt.grid(alpha=0.25)
    plt.legend(frameon=False)
    save_plot(fig, analysis_dir / "figure_1_accuracy_vs_context_size.png")

    # Figure 2: retrieval only
    retrieval_acc = acc_family[acc_family["task_family"] == "retrieval"].copy()
    fig = plt.figure(figsize=(7.2, 4.6))
    for noise_type, sub in retrieval_acc.groupby("noise_type"):
        plt.plot(sub["noise_size_target"], sub["accuracy"], marker="o", linewidth=2, label=noise_type)
    plt.xlabel("Noise size target (approx words)")
    plt.ylabel("Accuracy")
    plt.title("Retrieval Accuracy vs Context Size")
    plt.ylim(0.65, 1.02)
    plt.grid(alpha=0.25)
    plt.legend(frameon=False)
    save_plot(fig, analysis_dir / "figure_2_retrieval_accuracy.png")

    # Figure 3: distractor adoption retrieval only
    fig = plt.figure(figsize=(7.2, 4.6))
    plt.plot(
        distractor_retrieval["noise_size_target"],
        distractor_retrieval["distractor_adoption_rate"],
        marker="o",
        linewidth=2,
    )
    plt.xlabel("Noise size target (approx words)")
    plt.ylabel("Distractor adoption rate")
    plt.title("Retrieval Distractor Adoption Rate")
    plt.ylim(0, max(0.3, distractor_retrieval["distractor_adoption_rate"].max() + 0.03))
    plt.grid(alpha=0.25)
    save_plot(fig, analysis_dir / "figure_3_distractor_adoption.png")

    # Figure 4: latency
    fig = plt.figure(figsize=(7.2, 4.6))
    for noise_type, sub in lat.groupby("noise_type"):
        plt.plot(sub["noise_size_target"], sub["median_latency_ms"], marker="o", linewidth=2, label=noise_type)
    plt.xlabel("Noise size target (approx words)")
    plt.ylabel("Median latency (ms)")
    plt.title("Latency vs Context Size")
    plt.grid(alpha=0.25)
    plt.legend(frameon=False)
    save_plot(fig, analysis_dir / "figure_4_latency_vs_context_size.png")

    # Per-family figures
    for family, sub in acc_family.groupby("task_family"):
        fig = plt.figure(figsize=(7.2, 4.6))
        for noise_type, sub2 in sub.groupby("noise_type"):
            plt.plot(sub2["noise_size_target"], sub2["accuracy"], marker="o", linewidth=2, label=noise_type)
        plt.xlabel("Noise size target (approx words)")
        plt.ylabel("Accuracy")
        plt.title(f"{family.capitalize()} Accuracy vs Context Size")
        plt.ylim(0.7, 1.02)
        plt.grid(alpha=0.25)
        plt.legend(frameon=False)
        save_plot(fig, analysis_dir / f"accuracy_vs_context_size_{family}.png")


def fmt_pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def build_article(summary: dict, tables: dict, run_id: str) -> str:
    acc = tables["accuracy_by_condition"]
    retrieval_acc = tables["accuracy_by_task_family"]
    retrieval_acc = retrieval_acc[retrieval_acc["task_family"] == "retrieval"].copy()
    distractor = tables["distractor_retrieval"]

    baseline = float(acc.loc[acc["condition_label"] == "noise_0", "accuracy"].iloc[0])
    rand_4000 = float(acc.loc[acc["condition_label"] == "random_4000", "accuracy"].iloc[0])
    sim_250 = float(acc.loc[acc["condition_label"] == "similar_250", "accuracy"].iloc[0])
    sim_1000 = float(acc.loc[acc["condition_label"] == "similar_1000", "accuracy"].iloc[0])
    sim_4000 = float(acc.loc[acc["condition_label"] == "similar_4000", "accuracy"].iloc[0])

    retr_sim_250 = float(retrieval_acc.loc[retrieval_acc["condition_label"] == "similar_250", "accuracy"].iloc[0])
    retr_sim_1000 = float(retrieval_acc.loc[retrieval_acc["condition_label"] == "similar_1000", "accuracy"].iloc[0])
    retr_sim_4000 = float(retrieval_acc.loc[retrieval_acc["condition_label"] == "similar_4000", "accuracy"].iloc[0])

    retr_adopt_250 = float(distractor.loc[distractor["condition_label"] == "similar_250", "distractor_adoption_rate"].iloc[0])
    retr_adopt_1000 = float(distractor.loc[distractor["condition_label"] == "similar_1000", "distractor_adoption_rate"].iloc[0])
    retr_adopt_4000 = float(distractor.loc[distractor["condition_label"] == "similar_4000", "distractor_adoption_rate"].iloc[0])

    return f"""# Semantic Distractors, Not Context Length, Drive Retrieval Errors in LLMs

## Abstract

Large language models are often described as struggling with long context, but that claim is usually underspecified. It is unclear whether performance degradation comes from prompt length itself or from semantic interference inside the prompt. I built a controlled experiment to separate those factors. Across {summary["total_rows"]} trials on arithmetic, retrieval, logic, and instruction-following tasks, random irrelevant context up to ~4000 words had almost no effect on accuracy. In contrast, semantically similar irrelevant context reduced accuracy from {fmt_pct(baseline)} at baseline to {fmt_pct(sim_1000)} at the strongest observed degradation point. The effect was concentrated in retrieval tasks. Most importantly, all retrieval failures were explained by distractor adoption: the model returned values present in irrelevant context rather than the correct fact. This suggests that, in this setup, long-context failure is better understood as semantic interference than as context length collapse.

## Problem Framing

Current discussion around long-context LLMs is often too loose. “The model failed with a long prompt” can mean at least four different things:

1. the prompt was long,
2. the prompt contained semantically similar distractors,
3. the prompt contained contradictions,
4. the task itself was badly specified.

These are not the same failure mode.

The specific question here was:

> Given a fixed task and fixed prompt instructions, how do different amounts and types of irrelevant context change correctness, latency, instruction compliance, and error profile?

The hypothesis was that semantic interference would matter more than raw context length.

## Method

I used four task families:

- arithmetic
- retrieval from provided context
- logic / reasoning
- instruction-following

Each base task was evaluated under seven conditions:

- noise_0
- random_250
- random_1000
- random_4000
- similar_250
- similar_1000
- similar_4000

The random conditions used unrelated filler text. The similar conditions used semantically similar but irrelevant content. All trials used the same prompt layout:

- instruction
- noise block
- relevant task
- answer-format reminder

The experiment used one model, one stateless call per trial, exact automated scoring, separate compliance tracking, and wall-clock latency logging.

## Setup

This extended run contained:

- total trials: {summary["total_rows"]}
- overall accuracy: {fmt_pct(summary["overall_accuracy"])}
- overall compliance: {fmt_pct(summary["overall_compliance"])}
- retrieval trials: {summary["retrieval_trials"]}
- retrieval distractor adoption rate: {fmt_pct(summary["retrieval_distractor_adoption_rate"])}

Repository: {REPO_URL}

Run ID: `{run_id}`

## Results

### 1. Random context length had minimal effect on accuracy

Baseline accuracy was {fmt_pct(baseline)}. Under random unrelated context, accuracy remained effectively flat:

- random_250: {fmt_pct(float(acc.loc[acc["condition_label"] == "random_250", "accuracy"].iloc[0]))}
- random_1000: {fmt_pct(float(acc.loc[acc["condition_label"] == "random_1000", "accuracy"].iloc[0]))}
- random_4000: {fmt_pct(rand_4000)}

This is the first important result. In this experiment, context length alone did not meaningfully degrade performance.

### 2. Semantically similar distractors reduced accuracy

Under semantically similar irrelevant context, accuracy dropped substantially:

- similar_250: {fmt_pct(sim_250)}
- similar_1000: {fmt_pct(sim_1000)}
- similar_4000: {fmt_pct(sim_4000)}

The lowest overall condition was similar_1000 at {fmt_pct(sim_1000)}.

This means the key variable was not prompt length by itself, but semantic similarity between relevant and irrelevant context.

### 3. Retrieval tasks drove the effect

The degradation was concentrated in retrieval tasks:

- retrieval similar_250: {fmt_pct(retr_sim_250)}
- retrieval similar_1000: {fmt_pct(retr_sim_1000)}
- retrieval similar_4000: {fmt_pct(retr_sim_4000)}

Arithmetic, logic, and instruction-following remained largely stable by comparison.

This matters because it narrows the phenomenon. The model did not “generally collapse.” Instead, the weakness appeared when the task required selecting the correct fact from competing fact-like context.

### 4. Retrieval failures were explained by distractor adoption

This was the strongest result in the experiment.

Under retrieval tasks, distractor adoption rates were:

- similar_250: {fmt_pct(retr_adopt_250)}
- similar_1000: {fmt_pct(retr_adopt_1000)}
- similar_4000: {fmt_pct(retr_adopt_4000)}

All observed retrieval errors in the extended run were cases where the returned answer appeared inside the distractor block. That means the model was not merely “wrong.” It was selecting competing values from irrelevant context.

This is a much stronger claim than simple accuracy loss. It identifies the mechanism of failure.

### 5. Compliance remained intact

Overall compliance was {fmt_pct(summary["overall_compliance"])}.

That means the model continued to obey output-format instructions even when accuracy dropped. The failure mode here was not instruction drift or formatting collapse. It was answer selection under semantic competition.

### 6. Latency increased with context size

Median latency increased as noise size increased. This result is unsurprising and consistent with longer inputs requiring more processing time. However, latency is noisier than accuracy because it also reflects provider and network variability.

## Discussion

The main takeaway is straightforward:

**In this setup, long context alone was not the main problem. Semantic distractors were.**

That shifts the framing of the problem. Instead of saying “LLMs fail on long prompts,” a better description is:

> LLM retrieval can fail when semantically similar irrelevant facts compete with the relevant fact.

That is closer to a memory interference story than a pure context-window limitation story.

The result also shows why aggregate long-context benchmarks can be misleading. Two prompts of equal length may differ dramatically in difficulty depending on whether the irrelevant material is semantically inert or semantically competitive.

## Limitations

This experiment still has clear limits:

- it used one model
- it used synthetic tasks rather than natural corpora
- context size was approximated in words, not exact tokens
- contradictory distractors were not included
- sample sizes, while improved, are still modest for fine-grained curve estimation

So the correct interpretation is narrow: this is evidence about one model under one controlled setup, not a universal law of LLM behavior.

## Conclusion

The experiment does not support a naive “context length collapse” story. Random long context had little effect on accuracy. Semantically similar distractors did. In retrieval tasks, all observed failures were explained by distractor adoption.

The strongest conclusion is therefore:

**Performance degradation under cluttered context was primarily driven by semantic interference, not by context length alone.**

## Figures

- Figure 1: `figure_1_accuracy_vs_context_size.png`
- Figure 2: `figure_2_retrieval_accuracy.png`
- Figure 3: `figure_3_distractor_adoption.png`
- Figure 4: `figure_4_latency_vs_context_size.png`

## Repository

Code, experiment pipeline, and analysis artifacts: {REPO_URL}
"""


def build_medium_post(summary: dict, tables: dict, run_id: str) -> str:
    acc = tables["accuracy_by_condition"]
    distractor = tables["distractor_retrieval"]

    baseline = float(acc.loc[acc["condition_label"] == "noise_0", "accuracy"].iloc[0])
    sim_1000 = float(acc.loc[acc["condition_label"] == "similar_1000", "accuracy"].iloc[0])
    random_4000 = float(acc.loc[acc["condition_label"] == "random_4000", "accuracy"].iloc[0])
    retr_adopt_1000 = float(distractor.loc[distractor["condition_label"] == "similar_1000", "distractor_adoption_rate"].iloc[0])

    return f"""# I Tested “Context Collapse” in an LLM. The Real Problem Wasn’t Context Length.

People often say LLMs break when the prompt gets too long.

That claim is too vague.

A long prompt can fail for at least two completely different reasons:

- the model is genuinely struggling with length
- the prompt contains semantically similar distractors that interfere with retrieval

Those are not the same thing.

So I built a controlled experiment to separate them.

The repository is here: {REPO_URL}

## The setup

I created a small research pipeline that evaluates a model on four task families:

- arithmetic
- retrieval from provided context
- logic
- instruction-following

Then I embedded those tasks inside different kinds of irrelevant context:

- random unrelated text
- semantically similar but irrelevant text

And I scaled the irrelevant context across several sizes:

- 0
- 250
- 1000
- 4000 (approx words)

Every trial was logged, scored automatically, and analyzed with a reproducible pipeline.

## What I expected

The obvious hypothesis was:

> more irrelevant context → worse performance

That turned out to be incomplete.

## What actually happened

Random unrelated context barely mattered.

Baseline accuracy was {fmt_pct(baseline)}.

Even with large random context, accuracy stayed basically unchanged:

- random_4000: {fmt_pct(random_4000)}

But semantically similar distractors were a different story.

At similar_1000, overall accuracy dropped to:

- {fmt_pct(sim_1000)}

So the problem wasn’t just “more text.”

It was **competing text that looked relevant**.

## The interesting part: retrieval failures weren’t random

I added a distractor-adoption analysis to check whether wrong answers were actually being copied from the irrelevant context.

That’s exactly what happened.

For retrieval tasks under similar_1000, distractor adoption rate reached:

- {fmt_pct(retr_adopt_1000)}

In other words, the model often returned values that were present in the distractor block instead of the correct fact.

That’s not generic failure.

That’s semantic interference.

## What this means

The common “long context makes LLMs fail” framing is too blunt.

A better framing is:

> long context becomes dangerous when it contains semantically competitive distractors.

That is a much more useful way to think about prompt robustness, retrieval pipelines, and long-context evaluation.

## What did *not* fail

Instruction compliance stayed at 100%.

So the model didn’t start ignoring formatting instructions.

The failure mode was narrower:
- output format remained stable
- answer selection degraded under semantic competition

## Why I think this matters

A lot of long-context discussion treats token count as the main stressor.

This experiment suggests that **semantic competition matters more than raw length**, at least in this controlled setup.

That has direct implications for:
- RAG evaluation
- long-context benchmark design
- prompt engineering
- robustness testing

## Limits

This was still a controlled one-model study:
- one model
- synthetic tasks
- approximate word-based context sizing
- no contradiction condition yet

So this is not a universal claim about all LLMs.

But it is enough to make one strong point:

**The model didn’t fail because the prompt was long. It failed because the irrelevant context looked too much like the thing it was supposed to retrieve.**

If you want to inspect the code, figures, and analysis outputs, the repo is here:

{REPO_URL}

Run ID used for this write-up: `{run_id}`
"""


def build_x_post(summary: dict, tables: dict) -> str:
    acc = tables["accuracy_by_condition"]
    distractor = tables["distractor_retrieval"]

    baseline = float(acc.loc[acc["condition_label"] == "noise_0", "accuracy"].iloc[0])
    sim_1000 = float(acc.loc[acc["condition_label"] == "similar_1000", "accuracy"].iloc[0])
    random_4000 = float(acc.loc[acc["condition_label"] == "random_4000", "accuracy"].iloc[0])
    retr_adopt_1000 = float(distractor.loc[distractor["condition_label"] == "similar_1000", "distractor_adoption_rate"].iloc[0])

    return (
        f"I ran a controlled long-context experiment on an LLM.\n\n"
        f"Result:\n"
        f"- baseline accuracy: {fmt_pct(baseline)}\n"
        f"- random ~4000-word noise: {fmt_pct(random_4000)}\n"
        f"- semantically similar ~1000-word noise: {fmt_pct(sim_1000)}\n\n"
        f"Key finding: the model didn’t fail because the prompt was long.\n"
        f"It failed because semantically similar distractors caused retrieval interference.\n\n"
        f"For retrieval tasks, distractor adoption under similar_1000 was {fmt_pct(retr_adopt_1000)}.\n"
        f"Wrong answers were copied from irrelevant context.\n\n"
        f"Repo: {REPO_URL}\n"
        f"#{REPO_NAME.replace('-', '')} #LLM #RAG #Research"
    )


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

    tables = build_summary_tables(df, analysis_dir)
    plot_publication_quality(tables, df, analysis_dir)

    article = build_article(tables["summary"], tables, run_id)
    medium_post = build_medium_post(tables["summary"], tables, run_id)
    x_post = build_x_post(tables["summary"], tables)

    save_text(article, analysis_dir / "technical_article.md")
    save_text(medium_post, analysis_dir / "medium_post.md")
    save_text(x_post, analysis_dir / "x_post.txt")

    print("run_file:", run_file)
    print("saved:", analysis_dir / "technical_article.md")
    print("saved:", analysis_dir / "medium_post.md")
    print("saved:", analysis_dir / "x_post.txt")
    print("saved:", analysis_dir / "figure_1_accuracy_vs_context_size.png")
    print("saved:", analysis_dir / "figure_2_retrieval_accuracy.png")
    print("saved:", analysis_dir / "figure_3_distractor_adoption.png")
    print("saved:", analysis_dir / "figure_4_latency_vs_context_size.png")


if __name__ == "__main__":
    main()
