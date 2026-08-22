# Evidence

Every rule in this registry was put in front of a model that had not been told the rule, and kept
only if the model got it wrong.

## What was run

| | |
|---|---|
| evals | **21** (one further eval was voided and re-run) |
| recorded runs | **519** |
| models | Opus 5 · Sonnet 5 · Haiku 4.5 · qwen3.7-max |
| harnesses | `claude` CLI · `opencode` 1.17.11 |
| providers | Anthropic direct · OpenRouter |
| rules retired on measurement | **18** |

Per skill: [`evidence/`](./evidence). Across skills: the [rule ledger](./evidence/rules.md).
Method: [`spec/METHOD.md`](./spec/METHOD.md).

## Three arms, because two are not enough

| arm | loaded | answers |
|---|---|---|
| control | nothing | does the model already do this? |
| +core | the family core only | is any change just from having a file? |
| +skill | core and the skill | does *this* skill change anything? |

The middle arm exists because merely having a context file changes behaviour. Without it every
result is confounded by that, and a skill can appear to work when what worked was the presence of
instructions.

## Beyond one model and one harness

A result that holds in one place is not portable. Three variables were moved deliberately.

**Model.** Four families, and the differences are large. See the [model matrix](./evidence/model-matrix.md).

**Harness.** A [bridge run](./evidence/model-matrix.md#the-bridge) put the *same* model
(`anthropic/claude-haiku-4.5`) through both the `claude` CLI and `opencode`, so any difference is
attributable to the harness rather than the model. Running a different model in a different harness
moves two variables at once and measures neither.

**Provider.** Anthropic direct, and the same and different models through OpenRouter, including
`qwen3.7-max` on a non-Anthropic model in a non-Claude harness.

## What the measurements changed

**18 rules were removed** because a control arm already did the thing. Some were rules we were
confident about. The most-repeated advice in the entire permissions corpus, ask for a permission in
context rather than at launch, was satisfied in 12 of 12 control runs and deleted.

**Corpus support turned out to be an anti-signal.** The more repositories document a practice, the
more likely the model already follows it, because the corpus and the training data are the same
material. Register size has predicted result thinness across six axes: the largest register in the
project, 238 claims, produced the smallest skill, 3 rules.

**Two skills measured as nulls** and say so. `android/di` separated on nothing across 24 runs, and
its provenance records that the task tempted every scope decision the skill makes and both models
made the right call unaided.

**Some rules do not land.** A rule can name a genuine failure and fail to fix it. Those are marked
`not-landing` rather than quietly dropped or quietly counted.

## What went wrong

A method that never records a correction is not being checked.

**A claim was fabricated by over-generalising.** One provenance line read "24 of 24 runs used the
deprecated API". It came from hand-checking a single run. The real figure was 5 of 12, with 7 more
storing the value with no encryption at all, which is a worse failure that had been missed. Corrected
where it was written rather than replaced.

**A whole eval was voided.** Runs were launched with their working directory inside the repository
holding the skills, so every agent could read the skill it was meant to be a control for. One control
arm said so in its own summary. The eval was thrown away and re-run from a scratch directory outside
the repository.

**Thirteen scoring errors**, every one found by reading generated code rather than the results table.
Four shared one shape: a column naming a single mechanism where the rule permits several, which fails
in the direction that flatters the skill. Scoring code is now run against the unmodified seed first,
and its fixtures include near-misses rather than only a hit and a miss.
