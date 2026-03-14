# I Tested “Context Collapse” in an LLM. The Real Problem Wasn’t Context Length.

People often say LLMs break when the prompt gets too long.

That claim is too vague.

A long prompt can fail for at least two completely different reasons:

- the model is genuinely struggling with length
- the prompt contains semantically similar distractors that interfere with retrieval

Those are not the same thing.

So I built a controlled experiment to separate them.

The repository is here: https://github.com/qeinstein/context-collapse

## The setup

I created a small research pipeline that evaluates a model on four task families:

- arithmetic
- retrieval from provided context
- logic
- instruction-following

Then I embedded those tasks inside different kinds of irrelevant context:

- random unrelated text
- semantically similar but irrelevant text

And I scaled the irrelevant context across several sizes:

- 0
- 250
- 1000
- 4000 (approx words)

Every trial was logged, scored automatically, and analyzed with a reproducible pipeline.

## What I expected

The obvious hypothesis was:

> more irrelevant context → worse performance

That turned out to be incomplete.

## What actually happened

Random unrelated context barely mattered.

Baseline accuracy was 98.8%.

Even with large random context, accuracy stayed basically unchanged:

- random_4000: 97.5%

But semantically similar distractors were a different story.

At similar_1000, overall accuracy dropped to:

- 82.5%

So the problem wasn’t just “more text.”

It was **competing text that looked relevant**.

## The interesting part: retrieval failures weren’t random

I added a distractor-adoption analysis to check whether wrong answers were actually being copied from the irrelevant context.

That’s exactly what happened.

For retrieval tasks under similar_1000, distractor adoption rate reached:

- 24.0%

In other words, the model often returned values that were present in the distractor block instead of the correct fact.

That’s not generic failure.

That’s semantic interference.

## What this means

The common “long context makes LLMs fail” framing is too blunt.

A better framing is:

> long context becomes dangerous when it contains semantically competitive distractors.

That is a much more useful way to think about prompt robustness, retrieval pipelines, and long-context evaluation.

## What did *not* fail

Instruction compliance stayed at 100%.

So the model didn’t start ignoring formatting instructions.

The failure mode was narrower:
- output format remained stable
- answer selection degraded under semantic competition

## Why I think this matters

A lot of long-context discussion treats token count as the main stressor.

This experiment suggests that **semantic competition matters more than raw length**, at least in this controlled setup.

That has direct implications for:
- RAG evaluation
- long-context benchmark design
- prompt engineering
- robustness testing

## Limits

This was still a controlled one-model study:
- one model
- synthetic tasks
- approximate word-based context sizing
- no contradiction condition yet

So this is not a universal claim about all LLMs.

But it is enough to make one strong point:

**The model didn’t fail because the prompt was long. It failed because the irrelevant context looked too much like the thing it was supposed to retrieve.**

If you want to inspect the code, figures, and analysis outputs, the repo is here:

https://github.com/qeinstein/context-collapse

Run ID used for this write-up: `a1b3b36a-ce7c-4a9b-b8a0-37c77beb1538`
