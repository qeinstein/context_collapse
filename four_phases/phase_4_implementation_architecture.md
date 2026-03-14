# Phase 4

Implementation Architecture

Goal of this phase: define the exact Python project structure before writing experiment code.

The point is to avoid building a messy script that becomes hard to extend, debug, or analyze.

This phase fixes:

* project structure
* module boundaries
* data flow
* model interface
* evaluation flow
* logging flow
* plotting / analysis outputs

The design has to stay simple enough for a normal laptop and explicit enough that I can swap models later without rewriting everything.

Implementation Principles

1. Keep everything modular.
   I do not want one giant notebook or one giant Python file.

2. Keep every stage explicit.
   Task generation, prompt building, model calling, scoring, logging, and plotting should be separate.

3. Avoid hidden abstractions.
   If a function transforms data, that transformation should be obvious from the code.

4. Make the experiment reproducible.
   I need deterministic task generation where possible and fixed run metadata.

5. Separate raw results from derived analysis.
   Raw trial logs should never be overwritten by analysis outputs.

Recommended Project Structure

I should structure the project like this:

```text
context-collapse/
├── data/
│   ├── tasks/
│   ├── runs/
│   └── analysis/
├── src/
│   ├── config.py
│   ├── task_defs.py
│   ├── task_gen.py
│   ├── noise_gen.py
│   ├── prompt_builder.py
│   ├── model_interface.py
│   ├── evaluator.py
│   ├── logger.py
│   ├── runner.py
│   └── analysis.py
├── notebooks/
│   └── exploratory_analysis.ipynb
├── main.py
├── requirements.txt
├── four_phases/
└── README.md

```

This is enough structure to keep the work clean without turning the project into framework theater.

What Each Part Does

`data/tasks/`

* stores generated base tasks
* keeps task generation separate from execution
* lets me inspect the task dataset directly

`data/runs/`

* stores raw trial logs from each run
* each experiment run should get its own file or folder

`data/analysis/`

* stores derived summaries, tables, and plots
* nothing here should be treated as raw ground truth

`src/config.py`

* central place for experiment settings
* model config
* noise levels
* task counts
* prompt settings
* file paths

`src/task_defs.py`

* defines task schemas
* keeps task-family structure explicit
* can use dataclasses or typed dictionaries

`src/task_gen.py`

* generates synthetic tasks for arithmetic, retrieval, logic, and instruction following
* outputs canonical task objects with expected answers

`src/noise_gen.py`

* generates random unrelated text
* generates semantically similar irrelevant text
* targets approximate lengths

`src/prompt_builder.py`

* takes a task + noise block + template settings
* returns the final prompt string

`src/model_interface.py`

* defines one clean function or class for calling the model
* should hide provider-specific details but not experiment logic

`src/evaluator.py`

* normalizes model outputs
* computes correctness and compliance
* assigns error categories where possible

`src/logger.py`

* writes structured trial records to disk
* should use append-safe formats

`src/runner.py`

* orchestrates the experiment
* creates conditions
* shuffles trials
* calls model
* evaluates response
* logs everything

`src/analysis.py`

* loads raw logs
* computes summaries
* generates tables and plots

`main.py`

* simple entry point to run the experiment or specific stages

`notebooks/exploratory_analysis.ipynb`

* optional inspection notebook
* should not be the primary execution path

Data Model

The architecture needs explicit objects for:

* tasks
* trial conditions
* model responses
* evaluated trial records

The easiest clean choice is to use Python `dataclasses`.

Reason:

* readable
* lightweight
* better than loose dictionaries everywhere
* no need for a heavy framework

Core Data Objects

Task Object

Fields should include:

* `task_id`
* `task_family`
* `task_text`
* `expected_answer`
* `allowed_answer_set` if relevant
* `compliance_rule`
* optional metadata such as difficulty or generation seed

Condition Object

Fields should include:

* `noise_type`
* `noise_size_target`
* `condition_label`

Trial Object

Fields should include:

* `trial_id`
* `run_id`
* `task_id`
* `task_family`
* `noise_type`
* `noise_size_target`
* `prompt_text`
* `expected_answer`

Evaluation Object

Fields should include:

* `raw_response`
* `normalized_response`
* `parsed_answer`
* `is_correct`
* `is_compliant`
* `error_category`
* `latency_ms`
* `response_chars`
* `response_words`

Why explicit objects matter

If I skip this and just pass dictionaries between functions, the project will still run, but it will be much easier to create silent bugs and much harder to refactor later.

Task Generation Design

Task generation should happen before the experiment run.

Decision:

* generate base tasks once
* save them to disk
* reuse the same task set across runs unless I explicitly regenerate

Reason:

* stable comparisons
* easier debugging
* reproducibility

What task generation should output

A structured JSON or JSONL file containing all base tasks.

Reason for JSON/JSONL:

* human-readable
* easy to inspect
* easy to reload

I do not need a database for this project.

That would be pointless complexity.

Noise Generation Design

Noise generation needs to be separate from task generation because the same base task will be paired with multiple noise conditions.

The noise generator should:

* accept a noise type
* accept a target size
* optionally accept task metadata for similar distractor generation
* return the actual noise text plus measured length stats

Important detail:
The similar-noise generator should not accidentally include the true answer.

That is a hard constraint.

If that happens, the condition becomes invalid.

So the generator must either:

* build distractors from alternative synthetic entities, or
* validate that the expected answer string is absent from the noise text

Prompt Builder Design

The prompt builder should be a pure function.

Inputs:

* task object
* noise text
* template config

Output:

* full prompt string

Reason:

* makes prompt construction deterministic and testable
* easy to debug prompt formatting independently of model calls

This module should also expose the fixed instruction template used across all trials.

I should not bury prompt strings inside the runner.

Model Interface Design

This is one of the most important architectural choices.

The model-calling layer must be generic enough to swap providers later.

Best design:
create a minimal adapter interface.

Something like:

* one base class or protocol
* one method: `generate(prompt: str) -> ModelResponse`

The interface should return:

* raw text
* latency metadata if available
* token metadata if available

Why this matters:

* lets me start with one provider
* lets me switch later to another API or local model
* keeps the runner independent of provider-specific syntax

API Model vs Local Model

API Model

Advantages:

* easier setup
* usually stronger models
* less laptop burden

Disadvantages:

* network latency noise
* cost
* provider nondeterminism

Local Model

Advantages:

* more control
* no network jitter
* easier repeated experimentation once installed

Disadvantages:

* laptop may be too weak
* smaller local models may underperform badly
* more setup complexity

Recommendation

For the first implementation, I should design the interface to support both, but start with **API-based execution** unless my laptop can run a decent local model comfortably.

The architecture should not assume one or the other.

Evaluator Design

The evaluator should be split into two layers.

Layer 1: family-specific parsing and scoring

* arithmetic scorer
* retrieval scorer
* logic scorer
* instruction-following scorer

Layer 2: shared evaluation wrapper

* calls the correct scorer based on task family
* returns standardized evaluation fields

Reason:

* shared output structure
* family-specific rules remain explicit

This is cleaner than stuffing all scoring rules into one giant conditional block in the runner.

Error Categorization Design

Some error categories can be assigned automatically.

Examples:

* correct but noncompliant
* incorrect but compliant
* unparseable output

Some will likely need heuristics or manual review.

Examples:

* distractor adoption
* instruction dilution
* reasoning failure

Recommendation:

* automate what is cleanly detectable
* leave a field for manual post-hoc correction or annotation

That means the evaluator can produce:

* `auto_error_category`
* `manual_error_category` optional later

This is better than pretending every error label can be assigned perfectly by code.

Logging Design

Raw logs should be append-only and structured.

Best choice:
use **JSONL** for per-trial logs.

Reason:

* one record per line
* append-friendly
* easy to inspect
* easy to load into pandas later
* better for irregular fields than CSV

I can later export CSV summaries if needed.

But the raw source of truth should be JSONL.

Each run should produce:

* one run metadata file
* one JSONL trial log file

Run metadata should include:

* run_id
* timestamp
* model name
* settings
* dataset file used
* prompt template version

This matters for reproducibility.

Runner Design

The runner is the orchestration layer.

Its responsibilities:

1. load base tasks
2. construct all conditions
3. create trial list
4. shuffle order
5. generate noise for each condition
6. build prompt
7. call model
8. evaluate output
9. log result immediately

Important design rule:
log every trial immediately after evaluation.

Reason:
If the run crashes halfway through, I should not lose everything.

A bad design would keep results only in memory until the end.

I should not do that.

Failure Handling

The runner should handle failures explicitly.

Possible failures:

* API timeout
* malformed response
* empty response
* interruption during run

Design decision:
Every failed trial should still produce a log record with:

* failure status
* failure type
* partial metadata

Reason:
Silent missing trials will ruin analysis.

Missingness has to be visible.

Analysis Module Design

The analysis module should operate only on saved raw logs.

Inputs:

* trial JSONL file(s)

Outputs:

* summary tables
* aggregated CSVs if useful
* plots

Core outputs to generate later:

* accuracy vs noise size by task family
* compliance vs noise size by task family
* latency vs noise size by task family
* random vs similar distractor comparison
* error-category distribution plots

This module should not call the model.

That separation is important.

Why Not Use a Notebook as the Main Pipeline

Because notebooks are bad as the primary execution path for this kind of experiment.

Problems:

* state leakage
* hard-to-reproduce execution order
* hidden variables
* annoying for long batch runs

Notebook use is acceptable only for:

* quick inspection
* exploratory plotting
* debugging specific outputs

The main experiment should run from Python scripts.

Configuration Design

All experiment settings should live in one place.

Config should include:

* task counts
* noise sizes
* prompt template version
* generation settings
* file paths
* random seed
* model selection

Reason:
I do not want hardcoded settings spread across five files.

That is how experiments become irreproducible.

Minimal Execution Flow

The clean execution flow should be:

1. generate base tasks
2. save base tasks
3. build all trial conditions
4. shuffle trial order
5. for each trial:

   * generate noise
   * build prompt
   * call model
   * evaluate response
   * log trial record
6. after run ends:

   * load logs
   * compute summaries
   * generate plots

This is the exact experiment pipeline.

What I Should Not Do

I should not:

* write everything in one file
* hardcode prompts inside the runner
* mix raw logs with processed summaries
* score outputs manually during generation
* delay logging until the end of the run
* couple analysis code directly to model-calling code
* design the system around one provider’s SDK details

Those choices would make later extension painful.

Recommended Tech Choices

Python version

* Python 3.10+ is sufficient

Core libraries

* `dataclasses` or standard library typing
* `json` / `jsonlines` style writing
* `pathlib`
* `time`
* `random`
* `pandas`
* `matplotlib`

Why these choices:

* standard and lightweight
* enough for structured experiments
* no unnecessary framework overhead

Optional libraries later

* tokenizer library for exact token counts
* scipy/statsmodels for significance testing

Not necessary for the first implementation pass.

Phase 4 Decision Summary

Project Structure

* separate source code, raw data, runs, and analysis outputs

Core Modules

* config
* task definitions
* task generation
* noise generation
* prompt builder
* model interface
* evaluator
* logger
* runner
* analysis

Data Objects

* explicit task, condition, trial, and evaluation objects

Raw Logging Format

* JSONL per trial
* separate run metadata file

Execution Style

* script-first, notebook-second

Model Interface

* generic adapter so models can be swapped later

Critical Design Rules

* generate base tasks once and save them
* keep prompt construction pure and separate
* log every trial immediately
* preserve raw logs as source of truth
* run analysis only from saved logs

Phase 4 Output

Phase 4 is complete when the architecture is fixed and I know exactly what files and modules I need before writing code.

The next phase is Phase 5: implement the project skeleton and write the first runnable code for task generation, noise generation, prompt construction, and the experiment runner.
