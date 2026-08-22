# Evidence: `android`

| | |
|---|---|
| skills | 13 |
| evals | 26 |
| recorded runs | 490 |
| models | Opus 5 · Sonnet 5 · Haiku 4.5 · qwen3.7-max |
| harnesses | `claude` CLI · `opencode` 1.17.11 |
| providers | Anthropic direct · OpenRouter |

- [Model matrix](./model-matrix.md), the same task across models, harnesses and providers.
- [`skills/`](./skills), one document per skill: what was run, what separated, what did not.

## How to read this

**Every skill here was measured.** Drafted from a claim register, checked against primary sources,
and run against control and treated arms on four model families. The documents below record what
separated and what did not, including the results that went the other way.

**The tasks are small on purpose.** A self-contained task finishes in minutes and makes a difference
attributable to one change. That is what makes it a measurement, and also what limits it: a real
project has far more context competing for the model's attention and compounds a mistake across many
files. **A difference that shows as one run in a small task is larger in a real codebase, not
smaller.**

**Results are per model tested.** The same rule is unnecessary on one model and load-bearing on
another, so nothing here is curated against the frontier alone. See the
[model matrix](./model-matrix.md).

## Headline findings

**Capability is the variable.** The same rule is unnecessary on one model and load-bearing on
another, and the gap is large. Curating against the strongest model alone would have removed rules
that two of the three models tested need.

**Corpus support is an anti-signal.** Register size has predicted result thinness across six axes.
The largest register, 238 claims, produced the smallest skill, 3 rules.

**Two skills measured as nulls.** `android/di` separated on nothing across 24 runs. Its task tempted
every scope decision the skill makes and both models made the right call unaided.

**Some rules the tested models already follow**, and those are noted in each skill's evidence so a
reader can judge what is worth installing for their model.
