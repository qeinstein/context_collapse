from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TASKS_DIR = DATA_DIR / "tasks"
RUNS_DIR = DATA_DIR / "runs"

RANDOM_SEED = 42

# TASK_COUNTS = {
#     "arithmetic": 10,
#     "retrieval": 10,
#     "logic": 10,
#     "instruction": 10,
# }

# For extension
TASK_COUNTS = {
    "arithmetic": 10,
    "retrieval": 50,
    "logic": 10,
    "instruction": 10,
}



# Still approximate word-count targets for now.
NOISE_LEVELS = [0, 250, 1000, 4000]
NOISE_TYPES = ["random_unrelated", "similar_irrelevant"]

MODEL_BACKEND = "openrouter"   #
MODEL_NAME = "openai/gpt-4.1-mini"  # replace if you want another OpenRouter model slug

TEMPERATURE = 0.0
MAX_TOKENS = 64
TOP_P = 1.0

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_SITE_URL = "http://localhost"
OPENROUTER_APP_NAME = "context-collapse-experiment"
