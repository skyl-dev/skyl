# Evidence: `android/mvvm`

7 rules, 1 retired. The only finding in the family reproduced across two separate tasks.

## What was run

| eval | models | arms | runs |
|---|---|---|---|
| 07 | Haiku 4.5, Sonnet 5 | control / +core / +core+mvvm | 12 |
| 10 | Haiku 4.5, Sonnet 5 | control / +core / +core+mvvm | 11 |

## What separated

| rule | finding |
|---|---|
| `REPO-4` the repository interface is declared where it is used | **0/2 → 2/2 on both tasks.** The only result in this project reproduced twice. |
| `REPO-3` | **0/2 → 2/2** once a task supplied two origins for the same data. |

`REPO-3` is the reason task design gets its own section in the method. The first eval reported it
dead: that task had a single data origin, so there was nothing for the rule to act on. A second task
with two origins moved it 0/2 to 2/2. **A rule scored against a task that never tempted it has not
been measured**, and that is now a published rule rather than a lesson.

## What was retired

`VM-1` was tempted by both tasks and satisfied in every arm, including both controls. Removed.

## What was not measured

`VM-2` was never tempted: neither task needs a `Context` in a state holder, so it carries no
evidence in either direction. It is kept on the argument that it costs little and plausibly helps a
smaller model, which is weaker than the bar normally accepts and is marked accordingly.

## What the corpus said

The corpus called this skill a null result: 31 high-worth claims, 5 evidenced, 100% contested, and
the summary read that it had no content that was only its own. The measurement disagreed. The
eight-rule first draft was also wrong, in the other direction.

## Ledger

| rule | status | evidence |
|---|---|---|
| `REPO-4` | measured | 0/2 → 2/2 on both tasks, both models. Reproduced twice. |
| `REPO-3` | measured | 0/2 → 2/2 once a task supplied two data origins. Reported dead by a task that did not tempt it. |
| `VM-2` | unmeasured | Never tempted: neither task needs a `Context` in a state holder. |
| `VM-3` | unmeasured | Not separately tempted. |
| `VM-4` | unmeasured | Not separately tempted. |
| `REPO-1` | unmeasured | Not separately tempted. |
| `REPO-2` | unmeasured | Not separately tempted. |
| `VM-1` | retired | Tempted by both tasks and satisfied in every arm including the controls. |
