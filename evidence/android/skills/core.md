# Evidence: `android/core`

22 rules. Measured in two evals.

## What was run

| eval | what it tested | models | arms | runs |
|---|---|---|---|---|
| 01 | the original rule set | Opus 5 | control / +core / +core+kotlin | 18 |
| 19 | four rules added later | Haiku 4.5, Sonnet 5 | control / +core | 16 |

Eval 01 also fed the [model matrix](../model-matrix.md), where the same task was run across Opus 5,
Sonnet 5 and Haiku 4.5 to find where each rule sits in the capability window.

## What separated

| rule | finding |
|---|---|
| `STATE-1` save what rebuilds the screen | Opus 6/6 unaided. Sonnet and Haiku **0/2 → 2/2**. The rule a frontier-only eval would have deleted. |
| `DATA-2` money as minor units | Haiku **0/2 → 2/2**. Sonnet 1/2 → 2/2. |
| `DATA-4` destroy account data on sign-out | Haiku **0/2 → 2/2** with kotlin loaded. |
| `STATE-4` input owned by the control | Opus **0/6 → 6/6**. Sonnet 0/2 → 1/2, Haiku 0/2 → 0/2. Separates only on the model able to act on it. |

`STATE-1` and `STATE-4` are the two bounds of the capability window in one table. The first is
unnecessary at the frontier and needed below it; the second is the reverse.

## Eval 23: the rules no task had reached

Fourteen of the twenty-two rules had never been in front of a control arm. Two tasks, 16 runs,
control and `+core`.

**Two separations, both on Haiku.** `L10N-2`, the raw server enum rendered to a user, 2/2 → 0/2. And
`L10N-1`, hand-rolled money and date patterns, also 2/2 → 0/2.

**`L10N-1` was marked for retirement and should not have been.** It had been satisfied by every
control run in earlier work, which is the condition for removing a rule. Given a task with a
multi-currency total the Haiku control produced:

```kotlin
"USD" -> String.format("$%.2f", totalMinor / 100.0)
"EUR" -> String.format("€%.2f", totalMinor / 100.0)
```

A hardcoded symbol, a hardcoded exponent, and the symbol on the wrong side for a European locale.
The earlier tasks had never given it anything to format. Whether a rule is needed depends on whether
a task has asked, and until one does the answer is unknown rather than negative.

**Satisfied unaided in every arm:** the layer-direction rule, both work rules, one-source-of-truth,
and string resources.

**`SEC-2` did not land, and it is the clearest failure here.** The seed declares a broadcast receiver
with an intent filter and no `exported` attribute. Not one run of eight added it, in either arm, and
none validated the intent's extras.

## What did not land

**`WORK-3`, the main thread.** The Haiku control calls a filesystem read and a SHA-256 straight out
of a click handler, in both runs. The rule names a real failure and fixes it in one run of two,
which is one run and is noise. Kept, and recorded as not landing rather than as a win.

## What was retired

| rule | why |
|---|---|
| shrinking enabled for release builds | present in 8 of 8 runs, every arm |
| `implementation` over `api` | no run violated it, and the task could not tempt the violation |

Both were added on the strength of a large claim register and removed by the first measurement.

## What was not measured

The rules predating eval 01 carry the evidence in that eval's write-up rather than a per-rule score.
`WORK-1`, `WORK-2` and the localization rules were not separately tempted by either task.

## Method

Arms, task design, void conditions and the detector discipline are in [spec/METHOD.md](../../../spec/METHOD.md).
The short version: a control arm answers whether the model already does it, a `+core` arm answers
whether any change is just from having a file, and a rule that the control satisfies is removed.
