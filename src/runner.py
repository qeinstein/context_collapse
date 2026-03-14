import uuid
from datetime import datetime, timezone

from src.evaluator import evaluate_task
from src.noise_gen import generate_random_unrelated_noise, generate_similar_irrelevant_noise
from src.prompt_builder import build_prompt
from src.task_defs import Condition, NoiseBlock, Task, TrialRecord


def make_noise(task: Task, condition: Condition) -> NoiseBlock:
    if condition.noise_size_target == 0:
        return NoiseBlock(
            noise_type="none",
            target_size=0,
            text="",
            actual_chars=0,
            actual_words=0,
        )

    if condition.noise_type == "random_unrelated":
        return generate_random_unrelated_noise(condition.noise_size_target)

    if condition.noise_type == "similar_irrelevant":
        return generate_similar_irrelevant_noise(task, condition.noise_size_target)

    raise ValueError(f"Unknown noise type: {condition.noise_type}")


def run_single_trial(task: Task, condition: Condition, model, run_id: str) -> TrialRecord:
    noise_block = make_noise(task, condition)
    prompt_text = build_prompt(task, noise_block)
    response = model.generate(prompt_text, task)
    evaluation = evaluate_task(task, response.raw_text)

    return TrialRecord(
        trial_id=str(uuid.uuid4()),
        run_id=run_id,
        model_name=getattr(model, "name", "unknown-model"),
        task=task,
        condition=condition,
        noise_block=noise_block,
        prompt_text=prompt_text,
        response=response,
        evaluation=evaluation,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
    )
