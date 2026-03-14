# Phase 3

Evaluation and Logging Design

Goal of this phase: define exactly how outputs will be evaluated and recorded before writing implementation code.

This phase fixes:

* scoring rules
* compliance rules
* latency measurement
* error taxonomy
* logging schema

Evaluation Principle

The experiment prioritizes **exact automated evaluation**.

Rules:

* each task has a canonical answer
* correctness must be machine-checkable
* manual review is reserved for error categorization

Primary Metrics

The following variables are recorded for every trial.

Accuracy
Latency
Instruction Compliance
Output Length
Error Category

Metric strength ranking

Strongest: accuracy
Strong: latency
Moderate: compliance
Weak but useful: output length
Interpretive: error category

Scoring Rules

Arithmetic

Expected output: integer number

Correct if normalized response equals expected number.

Normalization:

* trim whitespace
* remove code fences if present

Strict rule: integer match only.

Examples
Expected: 35
Accepted: "35"
Rejected: "The answer is 35"
Rejected: "35.0"

Retrieval

Expected output: canonical answer string.

Correct if normalized response equals expected answer.

Normalization:

* trim whitespace
* case-insensitive comparison

Compliance is evaluated separately.

Example
Expected: HARBOR
Correct: harbor
Noncompliant: "The codename is HARBOR"

Logic

Expected output: one entity label.

Correct if normalized answer equals expected entity.

Normalization:

* trim whitespace
* case-insensitive comparison

Instruction Following

Expected output: exactly one token from an allowed set.

Correct only if the response matches the expected token exactly.

Examples
Allowed set: {ALPHA, BETA}

Accepted: BETA
Rejected: beta
Rejected: "The answer is BETA"

Instruction Compliance

Compliance is measured separately from correctness.

Possible outcomes

Correct and compliant
Correct but noncompliant
Incorrect but compliant
Incorrect and noncompliant

Compliance is recorded as a binary variable.

1 = compliant
0 = noncompliant

Latency Measurement

Latency is measured as wall-clock request time.

Definition

Time from immediately before sending the model request
until the complete response is received.

Recorded unit: milliseconds

Noise sources:

* network jitter
* server load
* runtime variability

Mitigation:

* randomized trial order
* consistent settings
* analyze median latency

Output Length

For every response record:

* character count
* word count

Purpose:

* detect verbosity drift
* detect instruction-following breakdown

Error Taxonomy

Manual error categories used for secondary analysis.

    E0 No error

    E1 Correct but noncompliant
    Correct content but formatting violation.

    E2 Incorrect but compliant
    Correct format but wrong answer.

    E3 Distractor adoption
    Answer copied from irrelevant context.

    E4 Instruction dilution
    Model follows instructions implied in distractor text.

    E5 Partial extraction
    Incomplete answer.

    E6 Reasoning failure
    Arithmetic or logical reasoning mistake.

    E7 Unparseable output
    Response cannot be evaluated.

    E8 Other

Error Labeling Policy

    Primary scoring is automated.

    Manual labeling is performed for incorrect responses.

Pilot stage:

    label all incorrect responses.

Full experiment:

    label either all incorrect responses or a stratified sample.

Trial Logging Schema

Every trial produces one record containing:

    Identifiers
    trial_id
    run_id
    timestamp

Condition metadata
    model_name
    task_family
    task_id
    noise_type
    noise_size_target

Prompt information
    noise_text
    task_text
    full_prompt

Ground truth
    expected_answer
    allowed_answer_set

Model output
    raw_response
    normalized_response
    parsed_answer

Evaluation
    is_correct
    is_compliant
    error_category

Performance
    latency_ms
    response_chars
    response_words

Generation settings
    temperature
    max_tokens
    top_p

Derived Metrics

From the logged trials the analysis stage will compute:

    accuracy by task × noise type × noise size
    compliance rate by condition
    median latency by condition
    average output length by condition
    error-category distribution

Pilot Success Criteria

The pilot is successful if:

* scoring works automatically
* compliance is meaningfully distinct from correctness
* latency values are recorded reliably
* task difficulty is not extreme
* failures reveal interpretable patterns

The pilot fails if:

* outputs are frequently unparseable
* scoring rules require manual fixes
* tasks are trivial or impossible
* compliance and correctness collapse into the same metric

Phase 3 Output

Phase 3 is complete when scoring rules, compliance rules, latency measurement, and logging schema are fixed.

The next phase is implementation architecture and experiment code.
