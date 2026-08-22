# How a skill gets measured

Every skill in `skills/` went through this loop. The artifacts for each are in
[`evidence/`](../evidence), and they are replayable.

```
1  read the register and the primary sources    the artifact, never a summary of it
2  draft
3  web-check anything version-dependent         the highest-yield step
4  adjust
5  layering + cross-reference gates
6  design tasks                                 outcomes, never mechanisms
7  leak gate
8  run: control / +core / +skill × 2 models × 2 batches
9  adjust from the results
10 ship, with the result written into Provenance
```

## The arms

| arm | loaded | answers |
|---|---|---|
| control | nothing | does the model already do this? |
| +core | the family's core only | is any change just from having a file? |
| +skill | core and the skill | does *this* skill change anything? |

The `+core` arm exists because merely having a context file changes behaviour. Without it, every
result is confounded by that.

## The task states outcomes, never mechanisms

A task that names the mechanism measures instruction-following, not the rule.

```
GOOD   "Photos taken on the phone's own camera should look the same in the app
        as they do in the gallery."
BAD    "Apply the EXIF orientation before displaying the image."
```

The situation goes in the **seed**, not the prompt. A brownfield project is given to the run with
the trap already in it — a store documented as synchronous, a manifest that already declares a
permission nothing requests, a data class whose total sits outside `equals`.

## Temptation — a score is only evidence if the task created the situation

A rule that scores 12/12 on a task that never tempted it has not been measured. Every eval records
which rules the task tempted and which it did not, and the ones it did not are published as
`unmeasured` rather than counted as passes.

## Reading rules, fixed before any run

At two runs per cell, only **0/2 → 2/2** counts. A move from 1/2 to 2/2 is one run and is noise.
Predictions are written down **before** scoring, including what would falsify the skill.

## Void conditions — a run that is not evidence

A run is void, not weak, if it hit a provider error, was killed, produced no files, cannot confirm
which model served it, or **executed anywhere it could read the skill under test**.

That last one is not hypothetical. One eval here ran with its working directory inside the
repository that holds the skills; every agent resolved its project root to that repository and could
read the skill it was meant to be a control for. The whole eval was voided and re-run. Runs now
execute outside the repository and copy their output back in.

## The detector

Scoring is mechanical, and the scoring code is the most error-prone part of the whole method —
**thirteen detector errors so far, every one found by reading the generated code rather than the
table.** Four were the same shape: a column naming *one* mechanism where the rule permits several,
which fails in the direction that flatters the skill.

```
The rule:      the hosted View is released
The column:    does AndroidView's onRelease argument appear?
The control:   released it correctly via DisposableEffect { onDispose { ... } }
Scored as:     a failure. The skill appeared to separate. It did not.
```

So: **a detector asks for the outcome the rule cares about, never the mechanism the rule happens to
name**, and it is run against the unmodified seed first — a column that fires on the seed is
measuring the seed.

Fixtures include a **near-miss** class, not just a hit and a miss: a comment that mentions the API
without calling it, a getter written across two lines, a re-encode that is not a resize.

## Beyond one model and one harness

Results that hold in only one place are not portable. Three things were varied deliberately:

| varied | how |
|---|---|
| **model** | Opus 5, Sonnet 5, Haiku 4.5, qwen3.7-max |
| **harness** | `claude` CLI and `opencode` |
| **provider** | Anthropic direct and OpenRouter |

The harness test is a **bridge**: the *same* model (`anthropic/claude-haiku-4.5`) run through both
harnesses, so a difference is attributable to the harness rather than to the model. Running a
different model in a different harness moves two variables at once and measures neither.

## What is corrected, in public

Findings here have been wrong and were corrected rather than quietly replaced. One provenance claim
was generalised from a single hand-checked run to "24 of 24" and was false; the correction is
recorded in the eval it came from, along with the real figure. A separate systematic error reported
per-task columns of 12 runs as 24.

Both are documented where they happened. A method that never records a correction is not being
checked.
