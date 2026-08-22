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

## Ledger

Every rule, and what is known about it. `scripts/build-ledger.py` reads this table, so a rule
missing from it fails the build.

| rule | status | evidence |
|---|---|---|
| `STATE-1` | measured | Sonnet and Haiku 0/2 → 2/2. Opus 6/6 unaided. |
| `STATE-4` | measured | Opus 0/6 → 6/6. Separates only where the model can act on it. |
| `DATA-2` | measured | Haiku 0/2 → 2/2, Sonnet 1/2 → 2/2. Replicated in `opencode` and on qwen. |
| `DATA-4` | measured | Haiku 0/2 → 2/2 with kotlin loaded. Inverted under `opencode`. |
| `WORK-3` | not-landing | Haiku control fails 2/2. Skill fixes 1 of 2, which is noise. |
| `BUILD-3` | not-landing | Haiku uses KAPT for Room in 4 of 4 runs, both arms. |
| `A11Y-1` | satisfied-unaided | Satisfied in every control tested: Opus 6/6, Sonnet 2/2, Haiku 2/2, qwen yes. Degraded under `opencode` with the skill loaded. Not re-tempted by eval 23. |
| `L10N-1` | measured | Haiku 2/2 → 0/2 on hand-rolled money patterns once a task gave it a multi-currency total. The earlier tasks never tempted it. |
| `BOUND-1` | satisfied-unaided | Tempted by eval 23 and satisfied unaided: 0 violations in 8 runs, both arms. |
| `BOUND-2` | not-tempted | Tempted by eval 23; moved by one run in each direction, which is noise. |
| `BOUND-3` | satisfied-unaided | Tempted by eval 23 and satisfied unaided in 8 of 8. |
| `STATE-2` | not-tempted | Not separately tempted. |
| `STATE-3` | not-tempted | Not separately tempted. |
| `DATA-1` | satisfied-unaided | Tempted by eval 23 and satisfied unaided in 8 of 8. |
| `DATA-3` | not-tempted | Tempted by eval 23; moved by one run in each direction, which is noise. |
| `WORK-1` | satisfied-unaided | Tempted by eval 23 and satisfied unaided: 0 violations in 8. |
| `WORK-2` | satisfied-unaided | Tempted by eval 23 and satisfied unaided: 8 of 8 used a scheduler. |
| `SEC-1` | not-tempted | Not separately tempted. |
| `SEC-2` | not-landing | 0 of 8 runs declared `exported` on a receiver with an intent filter, or validated its extras. Stated, loaded, ignored. |
| `SEC-3` | not-tempted | Appeared to fail in 7 of 8; the column was broader than the rule. What the runs logged was an order id, which the rule's boundary permits. |
| `L10N-2` | measured | Haiku 2/2 → 0/2. The control renders the raw server enum; the treated arm maps it. |
| `A11Y-2` | not-tempted | Not separately tempted. |
| `BUILD-1` | retired | Shrinking present in 8 of 8 runs, every arm. |
| `BUILD-2` | retired | No run violated it, and the task could not tempt the violation. |

**Two rules were satisfied by every control run.** `A11Y-1` and `L10N-1` were satisfied by every control this
project has run except one Haiku cell. By the admission bar they should go. They are listed rather
than quietly kept, and rather than quietly cut without a task that tempts them properly.

## Method

Arms, task design, void conditions and the detector discipline are in [spec/METHOD.md](../../../spec/METHOD.md).
The short version: a control arm answers whether the model already does it, a `+core` arm answers
whether any change is just from having a file, and a rule that the control satisfies is removed.
