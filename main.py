import random
import uuid

from src.config import RANDOM_SEED, MODEL_BACKEND, RUNS_DIR, TASKS_DIR
from src.logger import append_trial_record
from src.model_interface import DummyModel, OpenRouterModel
from src.runner import run_single_trial
from src.task_defs import Condition, Task
from src.task_gen import build_pilot_task_set, save_tasks


def get_model():
    if MODEL_BACKEND == "dummy":
        return DummyModel()
    if MODEL_BACKEND == "openrouter":
        return OpenRouterModel()
    raise ValueError(f"Unsupported MODEL_BACKEND: {MODEL_BACKEND}")


def build_pilot_conditions() -> list[Condition]:
    return [
        Condition(noise_type="random_unrelated", noise_size_target=0, condition_label="noise_0"),
        Condition(noise_type="random_unrelated", noise_size_target=250, condition_label="random_250"),
        Condition(noise_type="random_unrelated", noise_size_target=1000, condition_label="random_1000"),
        Condition(noise_type="random_unrelated", noise_size_target=4000, condition_label="random_4000"),
        Condition(noise_type="similar_irrelevant", noise_size_target=250, condition_label="similar_250"),
        Condition(noise_type="similar_irrelevant", noise_size_target=1000, condition_label="similar_1000"),
        Condition(noise_type="similar_irrelevant", noise_size_target=4000, condition_label="similar_4000"),
    ]


def build_trial_grid(tasks: list[Task], conditions: list[Condition]) -> list[tuple[Task, Condition]]:
    trials: list[tuple[Task, Condition]] = []
    for task in tasks:
        for condition in conditions:
            trials.append((task, condition))
    return trials


def main() -> None:
    random.seed(RANDOM_SEED)

    tasks = build_pilot_task_set()
    tasks_path = TASKS_DIR / "pilot_tasks.json"
    save_tasks(tasks, tasks_path)

    conditions = build_pilot_conditions()
    trials = build_trial_grid(tasks, conditions)
    random.shuffle(trials)

    model = get_model()
    run_id = str(uuid.uuid4())
    output_path = RUNS_DIR / f"{run_id}.jsonl"

    print(f"Running {len(trials)} trials...")
    print(f"Model backend: {MODEL_BACKEND}")
    print(f"Run ID: {run_id}")

    for idx, (task, condition) in enumerate(trials, start=1):
        record = run_single_trial(task, condition, model, run_id)
        append_trial_record(output_path, record)

        print(
            f"[{idx}/{len(trials)}] "
            f"task_id={task.task_id} "
            f"family={task.task_family} "
            f"condition={condition.condition_label} "
            f"correct={record.evaluation.is_correct} "
            f"compliant={record.evaluation.is_compliant} "
            f"latency_ms={record.response.latency_ms:.2f}"
        )

    print(f"\nSaved tasks to: {tasks_path}")
    print(f"Saved run log to: {output_path}")


if __name__ == "__main__":
    main()
