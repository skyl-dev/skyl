# Evidence: `android`

| | |
|---|---|
| skills | 13 |
| evals | 24, plus two voided |
| recorded runs | 575 |
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
another: `core STATE-1` is satisfied 6 of 6 unaided by the strongest model tested and 0 of 2 by two
others. Nothing here is curated against the frontier alone.

## Headline findings

**Capability is the variable.** The same rule is unnecessary on one model and load-bearing on
another. `core STATE-1` is satisfied 6/6 unaided by Opus and 0/2 by both Sonnet and Haiku, and the
skill fixes it in both. Curating against the frontier alone would have deleted it.

**Corpus support is an anti-signal.** Register size has predicted result thinness across six axes.
The largest register, 238 claims, produced the smallest skill, 3 rules.

**Two skills measured as nulls.** `android/di` separated on nothing across 24 runs. Its task tempted
every scope decision the skill makes and both models made the right call unaided.

**Some rules the models already follow.** `core A11Y-1` was satisfied by every control run tested.
`core L10N-1` looked the same until a task gave it a multi-currency total to format, and then the
Haiku control failed it in both runs. Whether a rule is needed depends on whether a task has asked.
