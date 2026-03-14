# Phase 2

Experimental Design

Goal of this phase: convert the research framing into an exact experiment specification that is small, controlled, and executable on a normal laptop.

In this phase I fix:

* task families
* noise families
* context sizes
* prompt layout
* sample size
* trial structure
* randomization
* repetition strategy

The objective is to eliminate ambiguity before implementation so that the code measures something interpretable rather than automating a vague setup.

Model Strategy

Decision: use **one model only** for the first experiment.

Reason:

* cleaner causal interpretation
* lower complexity
* easier debugging
* avoids mixing model comparison with context interference effects

Tradeoff:

* stronger internal validity
* weaker external generalization

Acceptable conclusion later:
"In this setup this model showed degradation under certain context conditions."

Unacceptable conclusion:
"All LLMs behave this way."

Task Families

All tasks must have exact answers and minimal ambiguity.

Arithmetic

Definition: short arithmetic expressions requiring a single numeric answer.

Format:

* 2–4 operations
* integers only
* parentheses allowed
* output must be the final number only

Example:
Compute: ((14 + 8) * 2) - 9

Expected answer: 35

Why this format:

* exact automated scoring
* isolates numerical reasoning
* distractor numbers can interfere measurably

Item count: 20 tasks

Retrieval From Provided Context

Definition: a synthetic passage contains a fact that must be retrieved.

Structure:

* fictional entities
* 3–5 attributes
* exactly one queried attribute

Example passage:
Project Oriole was launched in 2021. Its internal codename was HARBOR. The lead engineer was Nia Okafor.

Question:
What was the internal codename of Project Oriole?

Expected answer: HARBOR

Reason for synthetic passages:

* prevents world knowledge leakage
* forces in-context retrieval

Item count: 20 tasks

Logic / Reasoning

Definition: small transitive reasoning tasks.

Format:

* 3–5 entities
* relational constraints
* exact answer required

Example:
Ava is older than Ben.
Ben is older than Chidi.
Who is the oldest?

Answer: Ava

Reason:

* includes reasoning without ambiguity
* easy evaluation

Item count: 15 tasks

Instruction Following

Definition: tasks where the main challenge is following formatting instructions.

Format:

* simple rule
* small input
* output must be exactly one token from a predefined set

Example:
If the number is even, answer ALPHA. If odd, answer BETA.
Return exactly one token.

Input: 17

Expected answer: BETA

Reason:

* tests instruction dilution under distraction

Item count: 20 tasks

Task Generation Strategy

Decision: generate synthetic templated tasks rather than using benchmark datasets.

Reasons:

* full control over ground truth
* reproducible
* avoids contamination
* easier scoring

Noise Types

Two noise types are used in the first experiment.

Random Unrelated Text

Definition: text unrelated to the task topic.

Purpose:

* baseline irrelevance condition
* tests raw context length burden

Examples:

* unrelated descriptive paragraphs
* unrelated technical explanations

Semantically Similar but Irrelevant Text

Definition: text structurally similar to the task but referring to different entities or values.

Example:
If the real task concerns Project Oriole, distractors describe Project Lumen or Project Kestrel with similar attributes.

Purpose:

* tests interference rather than just length

Noise Types Excluded From First Experiment

Contradictory Text
Reason: introduces conflicting evidence rather than pure irrelevance.

Repeated Text
Reason: less informative than semantic distractors for the first study.

Context Sizes

Four levels of irrelevant context are tested.

Levels:
0 tokens
~250 tokens
~1000 tokens
~4000 tokens

These values refer to **irrelevant context only**, not total prompt size.

Reason for spacing:

* baseline
* mild clutter
* moderate clutter
* heavy clutter

Prompt Layout

The prompt structure is fixed across all trials.

Instruction
Noise block
Relevant task
Answer format reminder

Example template:

You must solve the task using only the relevant task information. Ignore unrelated text.

[NOISE BLOCK]

[TASK BLOCK]

Return only the required answer.

Reason:

* keeps structure constant
* forces retrieval through clutter

Trial Structure

Each base task is evaluated under 7 conditions.

Conditions:

0 noise
250 random
1000 random
4000 random
250 similar
1000 similar
4000 similar

At zero noise the noise type is meaningless, so only one baseline condition exists.

Sampling Plan

Task counts:
Arithmetic: 20
Retrieval: 20
Logic: 15
Instruction-following: 20

Total base tasks: 75

Total trials:
75 × 7 = 525 trials

Pilot Version

Pilot task counts:
Arithmetic: 10
Retrieval: 10
Logic: 10
Instruction-following: 10

Total tasks: 40

Total trials:
40 × 7 = 280 trials

Purpose of pilot:

* debug prompts
* validate scoring
* confirm task difficulty

Randomization

Procedure:

* generate every task-condition pair
* build full trial list
* shuffle order
* execute in randomized order

Reason:
prevents time-based confounds such as server load changes.

Repetition Strategy

For the first experiment:

* one run per task-condition pair

Reason:

* manageable runtime
* item diversity already reduces variance

Future extension:
repeat a subset of conditions to estimate stochastic variability.

Controlled Variables

These remain fixed across all trials:

* model
* prompt layout
* task templates
* generation settings
* context levels
* stateless calls

Relevant task information always appears **after the noise block** in this experiment.

