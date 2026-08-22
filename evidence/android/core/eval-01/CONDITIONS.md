# What eval 01 measured, and what it did not

Every verdict in `SCORES.tsv` is conditional on the environment below. The verdict vocabulary says
`NOT-NEEDED-HERE`, not `DELETE`, because deleting a rule on this evidence would be deleting it on
the strength of the single most favourable condition for the control arm.

## The condition measured

| | |
|---|---|
| Model | Claude Opus 5, frontier, current |
| Session | fresh, the task is turn 1 |
| Codebase | greenfield, empty directory |
| Scope | one screen, ~25 files |
| Competing instructions | none, no CLAUDE.md, no house style, no existing code |
| Runs | 4 per arm |

This is close to the best case a control arm can have. A model with no prior context, no accumulated
session state, and no existing code to imitate has every advantage.

## The conditions not measured, where a skill is actually used

1. **Long sessions.** A rule satisfied at turn 1 is not necessarily satisfied at turn 80. Nothing
   here measures retention across a session, and the adherence research says nothing about it
   either, its runs are short.
2. **Weaker models.** Uplift tracks how wrong the model's unaided default is. A rule that is
   inert for Opus 5 may separate cleanly for a smaller or older model. **Admission is
   model-dependent, and this project has never said which model it curates against.**
3. **Brownfield.** The task was an empty directory. Real installs land in existing codebases with
   existing patterns, and our own skills tell the agent to *match the file it is editing*. That
   clause may hand the decision to whatever the codebase already does. This was flagged as
   untested before the corpus work began and is still untested.
4. **Scale.** One screen, ~25 files. Rules about module boundaries and dependency direction cannot
   fail meaningfully at this size.
5. **Competing instructions.** No project conventions to contradict the skill. Contradiction is the
   one thing prose is measured to be bad at handling.

## What n=4 can and cannot say

`4/4` does not mean 100%. At n=4 the interval around a perfect score still reaches down to roughly
50–60%. A rule the model follows 75% of the time unaided would plausibly read 4/4 here, and would
still cost one user in four.

So `NOT-NEEDED-HERE` means: **not demonstrated to be needed in this condition, at this sample
size.** It does not mean the model always does it.

## What this does not soften

The two rules that separated, `core STATE-4` and `kotlin ASYNC-4`, separated at 0/4 against 4/4
in both treatment arms. Widening the conditions can only add rules back, not remove those.

And the direction of the result stands regardless of condition: **every rule with heavy corpus
backing failed to separate, and the rule that separated had none.** Corpus rank predicted the
wrong thing here exactly as it did in the four skill comparisons.
