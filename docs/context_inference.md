# Semantic Distractors, Not Context Length, Drive Retrieval Errors in LLMs

## Abstract

Large language models are often described as struggling with long context, but that claim is usually underspecified. It is unclear whether performance degradation comes from prompt length itself or from semantic interference inside the prompt. I built a controlled experiment to separate those factors. Across 560 trials on arithmetic, retrieval, logic, and instruction-following tasks, random irrelevant context up to ~4000 words had almost no effect on accuracy. In contrast, semantically similar irrelevant context reduced accuracy from 98.8% at baseline to 82.5% at the strongest observed degradation point. The effect was concentrated in retrieval tasks. Most importantly, all retrieval failures were explained by distractor adoption: the model returned values present in irrelevant context rather than the correct fact. This suggests that, in this setup, long-context failure is better understood as semantic interference than as context length collapse.

## Problem Framing

Current discussion around long-context LLMs is often too loose. “The model failed with a long prompt” can mean at least four different things:

1. the prompt was long,
2. the prompt contained semantically similar distractors,
3. the prompt contained contradictions,
4. the task itself was badly specified.

These are not the same failure mode.

The specific question here was:

> Given a fixed task and fixed prompt instructions, how do different amounts and types of irrelevant context change correctness, latency, instruction compliance, and error profile?

The hypothesis was that semantic interference would matter more than raw context length.

## Method

I used four task families:

- arithmetic
- retrieval from provided context
- logic / reasoning
- instruction-following

Each base task was evaluated under seven conditions:

- noise_0
- random_250
- random_1000
- random_4000
- similar_250
- similar_1000
- similar_4000

The random conditions used unrelated filler text. The similar conditions used semantically similar but irrelevant content. All trials used the same prompt layout:

- instruction
- noise block
- relevant task
- answer-format reminder

The experiment used one model, one stateless call per trial, exact automated scoring, separate compliance tracking, and wall-clock latency logging.

## Setup

This extended run contained:

- total trials: 560
- overall accuracy: 93.9%
- overall compliance: 100.0%
- retrieval trials: 350
- retrieval distractor adoption rate: 6.9%

Repository: https://github.com/qeinstein/context-collapse

Run ID: `a1b3b36a-ce7c-4a9b-b8a0-37c77beb1538`

## Results

### 1. Random context length had minimal effect on accuracy

Baseline accuracy was 98.8%. Under random unrelated context, accuracy remained effectively flat:

- random_250: 98.8%
- random_1000: 98.8%
- random_4000: 97.5%

This is the first important result. In this experiment, context length alone did not meaningfully degrade performance.

### 2. Semantically similar distractors reduced accuracy

Under semantically similar irrelevant context, accuracy dropped substantially:

- similar_250: 88.8%
- similar_1000: 82.5%
- similar_4000: 92.5%

The lowest overall condition was similar_1000 at 82.5%.

This means the key variable was not prompt length by itself, but semantic similarity between relevant and irrelevant context.

### 3. Retrieval tasks drove the effect

The degradation was concentrated in retrieval tasks:

- retrieval similar_250: 82.0%
- retrieval similar_1000: 76.0%
- retrieval similar_4000: 94.0%

Arithmetic, logic, and instruction-following remained largely stable by comparison.

This matters because it narrows the phenomenon. The model did not “generally collapse.” Instead, the weakness appeared when the task required selecting the correct fact from competing fact-like context.

### 4. Retrieval failures were explained by distractor adoption

This was the strongest result in the experiment.

Under retrieval tasks, distractor adoption rates were:

- similar_250: 18.0%
- similar_1000: 24.0%
- similar_4000: 6.0%

All observed retrieval errors in the extended run were cases where the returned answer appeared inside the distractor block. That means the model was not merely “wrong.” It was selecting competing values from irrelevant context.

This is a much stronger claim than simple accuracy loss. It identifies the mechanism of failure.

### 5. Compliance remained intact

Overall compliance was 100.0%.

That means the model continued to obey output-format instructions even when accuracy dropped. The failure mode here was not instruction drift or formatting collapse. It was answer selection under semantic competition.

### 6. Latency increased with context size

Median latency increased as noise size increased. This result is unsurprising and consistent with longer inputs requiring more processing time. However, latency is noisier than accuracy because it also reflects provider and network variability.

## Discussion

The main takeaway is straightforward:

**In this setup, long context alone was not the main problem. Semantic distractors were.**

That shifts the framing of the problem. Instead of saying “LLMs fail on long prompts,” a better description is:

> LLM retrieval can fail when semantically similar irrelevant facts compete with the relevant fact.

That is closer to a memory interference story than a pure context-window limitation story.

The result also shows why aggregate long-context benchmarks can be misleading. Two prompts of equal length may differ dramatically in difficulty depending on whether the irrelevant material is semantically inert or semantically competitive.

## Limitations

This experiment still has clear limits:

- it used one model
- it used synthetic tasks rather than natural corpora
- context size was approximated in words, not exact tokens
- contradictory distractors were not included
- sample sizes, while improved, are still modest for fine-grained curve estimation

So the correct interpretation is narrow: this is evidence about one model under one controlled setup, not a universal law of LLM behavior.

## Conclusion

The experiment does not support a naive “context length collapse” story. Random long context had little effect on accuracy. Semantically similar distractors did. In retrieval tasks, all observed failures were explained by distractor adoption.

The strongest conclusion is therefore:

**Performance degradation under cluttered context was primarily driven by semantic interference, not by context length alone.**

## Figures

- Figure 1: `figure_1_accuracy_vs_context_size.png`
- Figure 2: `figure_2_retrieval_accuracy.png`
- Figure 3: `figure_3_distractor_adoption.png`
- Figure 4: `figure_4_latency_vs_context_size.png`

## Repository

Code, experiment pipeline, and analysis artifacts: https://github.com/qeinstein/context-collapse
