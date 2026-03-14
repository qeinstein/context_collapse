from src.task_defs import EvaluationResult, Task


def normalize_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```") and text.endswith("```"):
        text = text.strip("`").strip()

    return text


def evaluate_task(task: Task, raw_response: str) -> EvaluationResult:
    normalized = normalize_text(raw_response)
    parsed_answer = normalized

    response_words = len(raw_response.split())
    response_chars = len(raw_response)

    if task.task_family == "arithmetic":
        is_correct = parsed_answer == task.expected_answer
        is_compliant = parsed_answer.isdigit()

    elif task.task_family in {"retrieval", "logic"}:
        is_correct = parsed_answer.lower() == task.expected_answer.lower()
        is_compliant = ("\n" not in parsed_answer) and (len(parsed_answer.split()) <= 3)

    elif task.task_family == "instruction":
        allowed = task.allowed_answer_set or []
        is_correct = parsed_answer == task.expected_answer
        is_compliant = parsed_answer in allowed and len(parsed_answer.split()) == 1

    else:
        is_correct = False
        is_compliant = False

    if parsed_answer == "":
        error_category = "E7"
    elif is_correct and is_compliant:
        error_category = "E0"
    elif is_correct and not is_compliant:
        error_category = "E1"
    elif not is_correct and is_compliant:
        error_category = "E2"
    else:
        error_category = "E8"

    return EvaluationResult(
        normalized_response=normalized,
        parsed_answer=parsed_answer,
        is_correct=is_correct,
        is_compliant=is_compliant,
        error_category=error_category,
        response_chars=response_chars,
        response_words=response_words,
    )
