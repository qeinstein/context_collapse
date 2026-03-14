import json
from dataclasses import asdict
from pathlib import Path

from src.task_defs import TrialRecord


def append_trial_record(output_path: Path, trial_record: TrialRecord) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(trial_record), ensure_ascii=False) + "\n")
