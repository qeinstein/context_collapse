This is basically my Research Notes.

Research Question: How does increasing amounts of irrelevant context affect an LLM's
                   task performance, latency, and instruction compliance across several task types?

The question is a bit broad, but it's traceable experimentally

A tighter Version: Given a fixed task and fixed prompt instructions, how do diff
amounts and types of irrelevant context inserted into the model input change:
    1. answer correctness,
    2. response latency,
    3. instruction following reliability
    4. error profile?



I should do this in phases

Phase 1:For small and moderate tasks, does increasing irrelevant context length
degrade LLM performance, and does the degradation depend on the type of irrelevant
context?


Candidate Hypotheses

    a. As irrelevant context length increases, response latency increases
    b. As irrelevant context length increases, task accuracy decreases
    c. Semantically similar or contradictory irrelevant context causes larger
       performance degradation than random unrelated texts of equal length
    d. The effect of irrelevant context differs by tasl type, instruction
       following and retrieval tasks may degrade differently from arithemetic tasks
    e. performance degradation is not necessarily linear w context size; there may be
       threshold effect where performance stays stable up to some point and then drops sharply



Independent Variables: 

    1. Irrelevant context amount: approximate token lenght of noise
    2. Irrelevant context type: diff noise types
    3. Task type: arithemetic, logic/reasoning e.t.can
    4. Model: idk yet, probably just one model to reduce complexity and comparison



Dependent Variables:

    1. accuracy
    2. latency
    3 Instruction Compliance: if the model followed the requested output format or constraints
    4. Output length: In tokens
    5. Error Category
        - wrong answer despite using relevant info
        - distractor adoption
        - instruction violation
        - incomplete answer
        - hallucinated justification
        - arithmetic slip
        - contradiction confusion

Controlled Variables:
    1. model settings: temperature, max tokens, top_p
    2. task difficulty within each task family
    3. prompt template structure
    4. API endpoint / runtime environment
    5. position of relevant information relative to distractor context
    6. response format constraints
    7. number of repetitions per condition



Success Condition: 
    A successful first experiment doesn'e mean "I've proven context colapse exists"

    It means I: 
        produced a clean, repoducibe setup
        made sure the measured vars are well defined(done)
        see interpretable trends
        can tell which claims are justified and which are not

    Examples of success:
        - latency clearly increases with prompt size
        - some task types show meaningful accuracy decline under certain distractor types
        - semantically similar distractors hurt more than random filler
        - the logging and evaluation pipeline is good enough that later extensions are easy



Faiure: 
    
    It is not failure if the hypotheses was wrong(those are assumptiions)

    Real failures: 
        prompt construction is inconsistent across conditions
        tasks are too easy so ceiling effects mask everything
        tasks are too hard so all conditions are near random
        evaluation is ambiguous
        latency measurements are dominated by network noise
        distractor types are not actually distinguishable
        sample size is too small to tell signal from noise



Noise Types:
    -  Random Unrelated texts
    -  Semantically similar but irrelevant text







Definitions (This should be down)
- Context Length: amount of input provided to the model(in tokens, usually)
- Irrelevant context: Unnecessary input for solving the given task
- Distraction: A stronger notion than irrelevaance. Context that can possibly pull the model toward the wrong answer


