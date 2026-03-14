from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Task:
    task_id: str
    task_family: str
    task_text: str
    expected_answer: str
    compliance_rule: str
    allowed_answer_set: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Condition:
    noise_type: str
    noise_size_target: int
    condition_label: str


@dataclass
class NoiseBlock:
    noise_type: str
    target_size: int
    text: str
    actual_chars: int
    actual_words: int


@dataclass
class ModelResponse:
    raw_text: str
    latency_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    normalized_response: str
    parsed_answer: str
    is_correct: bool
    is_compliant: bool
    error_category: str
    response_chars: int
    response_words: int


@dataclass
class TrialRecord:
    trial_id: str
    run_id: str
    model_name: str
    task: Task
    condition: Condition
    noise_block: NoiseBlock
    prompt_text: str
    response: ModelResponse
    evaluation: EvaluationResult
    timestamp_utc: str
