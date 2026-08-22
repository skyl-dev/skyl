# Evidence

Every rule in this registry was put in front of a model that had not been told the rule, and kept
only if the model got it wrong.

## What was run

| | |
|---|---|
| evals | **26** |
| recorded runs | **490** |
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
them, and the same rule can be unnecessary on one and load-bearing on another.

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

**Rules were dropped when the measurement said the model already did it**, which is what keeps the
installed set small. The most-repeated advice in the permissions corpus, ask for a permission in
context rather than at launch, was satisfied by every unaided run, so it is not here taking up
context.

**Corpus support turned out to be an anti-signal.** The more repositories document a practice, the
more likely the model already follows it, because the corpus and the training data are the same
material. Register size has predicted result thinness across six axes: the largest register in the
project, 238 claims, produced the smallest skill, 3 rules.

**Where a measurement found nothing, the skill's evidence says so.** The tested models handle some of
this already, and each skill records which parts and on which models, so a reader can judge whether
it is worth installing for theirs.
