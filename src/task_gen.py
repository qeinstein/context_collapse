import json
import random
from pathlib import Path
from typing import List

from src.config import RANDOM_SEED, TASK_COUNTS
from src.task_defs import Task


def generate_arithmetic_tasks(n: int) -> List[Task]:
    tasks: List[Task] = []

    for i in range(n):
        a = random.randint(2, 20)
        b = random.randint(2, 20)
        c = random.randint(2, 20)

        expr = f"(({a} + {b}) * 2) - {c}"
        answer = str(((a + b) * 2) - c)

        tasks.append(
            Task(
                task_id=f"arith_{i + 1:03d}",
                task_family="arithmetic",
                task_text=f"Compute: {expr}",
                expected_answer=answer,
                compliance_rule="Return only the final number.",
                metadata={"template": "double_sum_minus_c"},
            )
        )

    return tasks


def generate_retrieval_tasks(n: int) -> List[Task]:
    tasks: List[Task] = []

    project_names = [
        "Oriole",
        "Lumen",
        "Kestrel",
        "Vanta",
        "Pillar",
        "Juniper",
        "Nimbus",
        "Aster",
        "Falcon",
        "Atlas",
    ]
    codenames = [
        "HARBOR",
        "CINDER",
        "SOLACE",
        "EMBER",
        "NOVA",
        "AURORA",
        "VECTOR",
        "SUMMIT",
        "ECHO",
        "QUARRY",
    ]
    leads = [
        "Nia Okafor",
        "Tomi Adeyemi",
        "Maya Chen",
        "Ibrahim Bello",
        "Ava Singh",
        "Lena Park",
        "David Cole",
        "Zainab Yusuf",
        "Noah Grant",
        "Sara Kim",
    ]

    for i in range(n):
        project = project_names[i % len(project_names)]
        codename = codenames[i % len(codenames)]
        lead = leads[i % len(leads)]
        year = 2020 + (i % 5)

        passage = (
            f"Project {project} was launched in {year}. "
            f"Its internal codename was {codename}. "
            f"The lead engineer was {lead}."
        )
        question = f"What was the internal codename of Project {project}?"

        tasks.append(
            Task(
                task_id=f"retr_{i + 1:03d}",
                task_family="retrieval",
                task_text=f"Passage: {passage}\nQuestion: {question}",
                expected_answer=codename,
                compliance_rule="Return only the codename.",
                metadata={"project": project, "year": year, "lead": lead},
            )
        )

    return tasks


def generate_logic_tasks(n: int) -> List[Task]:
    tasks: List[Task] = []
    names = ["Ava", "Ben", "Chidi", "Dami", "Esi", "Femi"]

    for i in range(n):
        rotated = names[i % len(names):] + names[: i % len(names)]
        a, b, c = rotated[:3]

        task_text = (
            f"{a} is older than {b}.\n"
            f"{b} is older than {c}.\n"
            "Who is the oldest?"
        )

        tasks.append(
            Task(
                task_id=f"logic_{i + 1:03d}",
                task_family="logic",
                task_text=task_text,
                expected_answer=a,
                compliance_rule="Return only the name.",
                metadata={"template": "transitive_age"},
            )
        )

    return tasks


def generate_instruction_tasks(n: int) -> List[Task]:
    tasks: List[Task] = []

    for i in range(n):
        value = random.randint(1, 99)
        expected = "ALPHA" if value % 2 == 0 else "BETA"

        task_text = (
            "If the number is even, answer ALPHA. "
            "If the number is odd, answer BETA.\n"
            f"Number: {value}"
        )

        tasks.append(
            Task(
                task_id=f"instr_{i + 1:03d}",
                task_family="instruction",
                task_text=task_text,
                expected_answer=expected,
                compliance_rule="Return exactly one token: ALPHA or BETA.",
                allowed_answer_set=["ALPHA", "BETA"],
                metadata={"value": value},
            )
        )

    return tasks


def save_tasks(tasks: List[Task], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump([task.__dict__ for task in tasks], f, indent=2, ensure_ascii=False)


def build_pilot_task_set() -> List[Task]:
    random.seed(RANDOM_SEED)

    tasks: List[Task] = []
    tasks.extend(generate_arithmetic_tasks(TASK_COUNTS["arithmetic"]))
    tasks.extend(generate_retrieval_tasks(TASK_COUNTS["retrieval"]))
    tasks.extend(generate_logic_tasks(TASK_COUNTS["logic"]))
    tasks.extend(generate_instruction_tasks(TASK_COUNTS["instruction"]))

    return tasks
