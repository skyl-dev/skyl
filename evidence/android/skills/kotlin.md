# Evidence: `android/kotlin`

6 rules, 3 retired. Re-measured under the current method in eval 22.

## What was run

| eval | what it tested | models | arms | runs |
|---|---|---|---|---|
| 01, 03, 04, 05, 06 | the original rule set | Opus 5, Sonnet 5, Haiku 4.5, qwen3.7-max | control / +core / +kotlin | see the [matrix](../model-matrix.md) |
| 22 | the whole skill, re-run under the current method | Haiku 4.5, Sonnet 5 | control / +core / +kotlin | 24 |

Eval 22 exists because this skill carried the oldest evidence in the family: measured before
brownfield seeds, before the temptation rule, before near-miss fixtures in the scoring code. Every
other skill re-run under the current method had lost rules, so the expectation was that this one
would too.

## What separated

Three rules, all on Haiku, all `2/2 → 0/2` in the violation direction with the `+core` arm flat.

| rule | Haiku ctl → +core → +kotlin | Sonnet |
|---|---|---|
| `ASYNC-2` cancellation swallowed | **2/2 → 2/2 → 0/2** | 0/6, every arm |
| `ASYNC-4` job tracked by hand | **2/2 → 2/2 → 0/2** | 0/6, every arm |
| `TYPE-1` stored property in a data class body | **2/2 → 2/2 → 0/2** | 1/2 → 0/2 |

Sonnet satisfies all three unaided and Haiku fails all three unaided. That is the capability window
measured about as cleanly as this project manages.

Verified by reading the code rather than the table: the Haiku control keeps a `var` total in a data
class body, so the value sits outside `equals` and a cart whose total changes compares equal to the
previous state. The skill arm writes a computed getter, which is the alternative the rule itself
names.

**The two rules that carried old evidence both reproduced.** `ASYNC-2` was 0/3 → 3/3 and `ASYNC-4`
was 1/3 → 3/3 under the old method. Three runs on one model is a weak sample, and it turned out not
to be a wrong one.

## What did not land

| rule | finding |
|---|---|
| `ASYNC-5` make a shared cold flow hot | Appears in 1 of 12 runs. Two screens read one cold flow and nobody noticed, with or without the rule. |
| `TYPE-3` read-only type at a boundary | The cache still hands out its own `MutableList` in 12 of 12 runs, untouched by any arm. |

## What was retired

| rule | why |
|---|---|
| don't re-wrap a call that already dispatches | 0 violations in 12 runs, every arm |
| replace state rather than mutating it | 0 violations in 12 runs, every arm |
| absence is nullable, not defaulted | 0 violations in 12; 10 of 12 made the field nullable unprompted |

## A scoring error worth publishing

The first pass reported `ASYNC-2` separating on **Sonnet**. That was backwards. The column looked
for cancellation being re-raised and matched neither correct form the runs actually used: the Sonnet
control catches `CancellationException` and rethrows *on the following line*, and the skill arms use
`Flow.catch`, which is transparent to cancellation by design. Both were scored as swallowing it.

Rewritten as the outcome, is cancellation swallowed, with three accepted mechanisms, the separation
moved to Haiku and Sonnet turned out clean in all six runs. Thirteenth scoring error in the project
and the fourth of that shape, which fails in the direction that flatters the skill.
