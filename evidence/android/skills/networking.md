# Evidence: `android/networking`

15 rules. The richest register in the family produced the thinnest result.

## What was run

| eval | models | arms | runs |
|---|---|---|---|
| 13 | Haiku 4.5, Sonnet 5 | control / +core / +core+networking | 24, two tasks |

## What separated

One rule. `CLIENT-2`, set a whole-call timeout rather than only the per-operation ones. Haiku
**0/2 → 2/2**.

It is also the one rule here whose reason came from a **primary source rather than the corpus**.
Checking OkHttp's actual defaults showed the per-operation timeouts are ten seconds each and only
`callTimeout` defaults to none, so a request can keep resetting its own ten seconds while the call as
a whole never finishes.

## Already handled by the tested models

`AUTH-1`, `AUTH-2` and `AUTH-3` were satisfied unaided by both models **on a task built to tempt
them**. The sample is two runs per cell, so this is recorded as a result rather than treated as final.

## The pattern this skill demonstrates

This register was the richest of any axis: 81 evidenced claims from 12 repos. It produced one
separation.

Heavy corpus backing predicts rules the model already follows, because the corpus and the training
data are the same material. Across the family, register size has predicted result thinness rather
than richness.
