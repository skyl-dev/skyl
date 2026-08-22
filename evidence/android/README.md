# Evidence: `android`

| | |
|---|---|
| skills | 13 |
| evals | 21, plus one voided and re-run |
| recorded runs | 519 |
| models | Opus 5 · Sonnet 5 · Haiku 4.5 · qwen3.7-max |
| harnesses | `claude` CLI · `opencode` 1.17.11 |
| providers | Anthropic direct · OpenRouter |

- [Rule ledger](./rules.md), every rule in the family and its status. Generated.
- [Model matrix](./model-matrix.md), the same task across models, harnesses and providers.
- [`skills/`](./skills), one document per skill: what was run, what separated, what did not.

## Reading the ledger

**Statuses are per model tested.** Four model families have been run here. A rule the tested models
already follow may still be the rule a different model needs, so `satisfied-unaided` is a result
about them rather than a judgement about the rule.

`not-tempted` does not mean untested. It means **no task has created that rule's situation**, so
nothing is known either way. `satisfied-unaided` means a task did create it and the control already
got it right, which is a measurement with a negative answer.

Those were one word until 23-Aug-2026, and collapsing them made a well-tested skill look untested. A
skill can have most of its rules loaded in every run of a 24-run eval and still have most of them
`not-tempted`, because a task tempts the handful of rules its situation reaches.

Evals in progress are converting these: the `core` eval alone moved seven rules out of
`not-tempted`, two of them into `measured`.

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
