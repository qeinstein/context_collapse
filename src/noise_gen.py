import random
from typing import List

from src.task_defs import NoiseBlock, Task


UNRELATED_SENTENCES = [
    "The coastal trail curved around a quiet bay lined with black volcanic stone.",
    "A ceramic bowl can retain heat longer if it is warmed before serving soup.",
    "Migratory birds often adjust their routes in response to pressure shifts.",
    "The archive room used a manual indexing system organized by color and year.",
    "A telescope mount must remain stable to reduce blur during long exposures.",
    "Coffee cherries are processed differently depending on the desired flavor profile.",
    "The workshop table had scratch marks from years of repeated tool use.",
    "In dry weather, the upper soil layer may crack before deeper layers lose moisture.",
]


def _repeat_to_target(sentences: List[str], target_words: int) -> str:
    if target_words <= 0:
        return ""

    chunks: List[str] = []
    current_words = 0

    while current_words < target_words:
        sentence = random.choice(sentences)
        chunks.append(sentence)
        current_words += len(sentence.split())

    return " ".join(chunks)


def generate_random_unrelated_noise(target_words: int) -> NoiseBlock:
    text = _repeat_to_target(UNRELATED_SENTENCES, target_words)
    return NoiseBlock(
        noise_type="random_unrelated",
        target_size=target_words,
        text=text,
        actual_chars=len(text),
        actual_words=len(text.split()),
    )


def generate_similar_irrelevant_noise(task: Task, target_words: int) -> NoiseBlock:
    if task.task_family == "retrieval":
        base_sentences = [
            "Project Kestrel was launched in 2022 and used the codename VECTOR.",
            "Project Lumen was launched in 2021 and used the codename SUMMIT.",
            "Project Vanta was led by Maya Chen and used the codename EMBER.",
            "Project Juniper entered internal testing in 2023 with codename QUARRY.",
        ]
    elif task.task_family == "arithmetic":
        base_sentences = [
            "A previous calculation used 18, 7, and 4 in a separate accounting worksheet.",
            "An unrelated formula doubled a subtotal before subtracting a fixed charge.",
            "Another team computed values from a different table using independent inputs.",
        ]
    elif task.task_family == "logic":
        base_sentences = [
            "Lena is taller than Mark, and Mark is taller than Tobi in another example.",
            "In a separate ranking, Imani finished ahead of Kojo and behind Zara.",
            "A different age-ordering problem placed Rina above Seyi and below Tade.",
        ]
    elif task.task_family == "instruction":
        base_sentences = [
            "If the value is below 10, another unrelated system returns GAMMA.",
            "A separate control rule maps odd identifiers to DELTA under a different protocol.",
            "Another labeling scheme uses OMEGA for archived records and SIGMA for active ones.",
        ]
    else:
        raise ValueError(f"Unsupported task family for similar noise: {task.task_family}")

    text = _repeat_to_target(base_sentences, target_words)

    # Hard safety check against direct answer leakage.
    if task.expected_answer.lower() in text.lower():
        text = text.replace(task.expected_answer, "REDACTED")
        text = text.replace(task.expected_answer.lower(), "redacted")

    return NoiseBlock(
        noise_type="similar_irrelevant",
        target_size=target_words,
        text=text,
        actual_chars=len(text),
        actual_words=len(text.split()),
    )
