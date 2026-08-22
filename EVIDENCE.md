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
| rules retired on measurement | **17** |

Per skill: [`evidence/`](./evidence).

## How it was measured

Each skill was run against a **control** arm that was not told the rule, and a **treated** arm that
was. A middle arm loads only the family core, so a change cannot be explained by the mere presence of
a context file.

Tasks are small and self-contained, which is what makes a difference attributable and also what
limits it. A real project has more context competing for attention and repeats a wrong default across
many files, so **a difference measured here is a floor rather than a ceiling.**

## Results are per model, and the spread is wide

Skills here are written for whatever model a project uses. Four model families have been run against
them, and the same rule can be unnecessary on one and load-bearing on another: `core STATE-1` is
satisfied 6 of 6 unaided by the strongest model tested and 0 of 2 by two others.

So a rule recorded as `satisfied-unaided` is a statement about the models tested, not about models in
general. A weaker or differently-trained model may need exactly the rule a frontier model does not,
which is why nothing here is curated against the frontier alone.

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

**17 rules were removed** because a control arm already did the thing. Some were rules we were
confident about. The most-repeated advice in the entire permissions corpus, ask for a permission in
context rather than at launch, was satisfied in 12 of 12 control runs and deleted.

**Corpus support turned out to be an anti-signal.** The more repositories document a practice, the
more likely the model already follows it, because the corpus and the training data are the same
material. Register size has predicted result thinness across six axes: the largest register in the
project, 238 claims, produced the smallest skill, 3 rules.

**Two skills measured as nulls** and say so. `android/di` separated on nothing across 24 runs, and
its provenance records that the task tempted every scope decision the skill makes and both models
made the right call unaided.

**Some rules do not land.** A rule can name a genuine failure and fail to fix it on the models
tested. Those are recorded in the skill's evidence rather than quietly dropped or quietly counted.

## Corrections

Findings here have been wrong and were corrected where they were published rather than quietly
replaced. One claim was generalised from a single checked run and overstated; the real figure and the
correction sit in the skill's evidence. One eval was discarded entirely because its runs could read
the skill they were meant to be a control for.

Both are recorded because a result nobody can check is not evidence.
