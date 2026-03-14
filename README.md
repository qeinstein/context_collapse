# Context Collapse: LLM Performance under Semantic Interference

A research framework designed to investigate how Large Language Models (LLMs) handle increasing amounts of irrelevant context, specifically distinguishing between the effects of **raw context length** and **semantic interference**.

## Overview

"Context Collapse" occurs when a model's performance on a specific task degrades as the input prompt grows. This project aims to answer: *Does the model fail because the prompt is long, or because the irrelevant context contains "distractors" that look like the target information?*

### Key Hypotheses
- **H1:** Raw context length (random unrelated text) has a minimal impact on accuracy for modern LLMs.
- **H2:** Semantic similarity between the task and the irrelevant context drives significant performance degradation (distractor adoption).
- **H3:** Retrieval tasks are more susceptible to context collapse than reasoning or arithmetic tasks.

## Experimental Design

The framework evaluates models across a grid of conditions:

### 1. Task Families
- **Arithmetic:** Multi-step math problems.
- **Retrieval:** Extracting specific facts from a cluttered context.
- **Logic:** Reasoning through deductive or inductive problems.
- **Instruction Following:** Adhering to strict formatting and behavioral constraints.

### 2. Noise Conditions
- **Control:** 0 tokens of noise.
- **Random Unrelated:** Noise blocks of 250, 1000, and 4000 words using unrelated text.
- **Similar Irrelevant:** Noise blocks of 250, 1000, and 4000 words using semantically similar but incorrect distractors.

### 3. Metrics
- **Correctness:** Automated scoring of answer accuracy.
- **Compliance:** Binary check for adherence to output format (e.g., "answer in one word").
- **Latency:** Wall-clock time per trial.
- **Distractor Adoption:** Detects if the model's incorrect answer was sourced from the noise block.

## Getting Started

### Installation
1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure your `.env` file with `OPENROUTER_API_KEY`.

### Running Experiments
To run a full experimental suite:
```bash
python main.py
```
This generates a unique Run ID (UUID) and saves raw results to `data/runs/<uuid>.jsonl`.

### Analysis & Reporting
To generate a full analysis report (plots, CSVs, and summary articles) for the most recent run:
```bash
python -m src.analysis.report_builder --run latest
```
Outputs are saved to `data/analysis/<uuid>/`.

## Project Structure

- `src/`: Core logic for task generation, model interfacing, and evaluation.
- `src/analysis/`: Statistical tools and report generators.
- `data/`:
    - `tasks/`: Generated task definitions.
    - `runs/`: Raw JSONL experimental data.
    - `analysis/`: Processed metrics and visualization artifacts.
- `four_phases/`: Research documentation (Questions, Design, Specs, Architecture).

## License

MIT
