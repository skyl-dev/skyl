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

## Headline findings

**Capability is the variable.** The same rule is unnecessary on one model and load-bearing on
another. `core STATE-1` is satisfied 6/6 unaided by Opus and 0/2 by both Sonnet and Haiku, and the
skill fixes it in both. Curating against the frontier alone would have deleted it.

**Corpus support is an anti-signal.** Register size has predicted result thinness across six axes.
The largest register, 238 claims, produced the smallest skill, 3 rules.

**Two skills measured as nulls.** `android/di` separated on nothing across 24 runs. Its task tempted
every scope decision the skill makes and both models made the right call unaided.

**Two rules are retirement candidates.** `core A11Y-1` and `core L10N-1` were satisfied by nearly
every control run. By the admission bar they should be removed, and they are marked rather than
quietly kept.
