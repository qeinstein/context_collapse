from src.task_defs import NoiseBlock, Task


def build_prompt(task: Task, noise_block: NoiseBlock) -> str:
    noise_text = noise_block.text.strip()

    if noise_text:
        return (
            "You must solve the task using only the relevant task information. "
            "Ignore unrelated text.\n\n"
            f"{noise_text}\n\n"
            f"{task.task_text}\n\n"
            f"{task.compliance_rule}"
        )

    return (
        "You must solve the task using only the relevant task information.\n\n"
        f"{task.task_text}\n\n"
        f"{task.compliance_rule}"
    )
