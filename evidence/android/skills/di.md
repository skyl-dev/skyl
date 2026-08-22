# Evidence: `android/di`

11 rules. **Measured as a null.** Nothing separated.

## What was run

| eval | models | arms | runs |
|---|---|---|---|
| 14 | Haiku 4.5, Sonnet 5 | control / +core / +core+di | 24, two seeded tasks |

## The result

No rule separated on either task.

Task A tempted **every scope decision this skill makes**: an object expensive to build, a cheap
stateless one, state scoped to a single screen, two bindings of one type needing a qualifier, and a
component the framework constructs itself. Both models made the right call on each without the skill
loaded.

**The null was not redesigned, and that was deliberate.** A null gets one redesign under this
project's method, and it was not spent here, because the null is not a task failure. A different task
tempting the same rules would measure the same defaults.

## One model-dependent result

Sonnet scopes screen-only state to the screen in every arm. Haiku never does, in any arm, **including
with the skill loaded**. That is the capability window rather than a rule that works: below the
window a rule does not land even when stated.

## The pattern this skill demonstrates

The register behind this skill was the largest of any axis at the time: 154 evidenced claims from 15
repos. Nearly all of it was library API detail, excluded by the rule that a topic groups by concern
rather than by library.

Register size has predicted result thinness across the family:

| skill | evidenced claims | rules that separated |
|---|---|---|
| `xml` | 29 | **4** |
| `networking` | 81 | 1 |
| `di` | **154** | **0** |

## Ledger

| rule | status | evidence |
|---|---|---|
| `SCOPE-1` | unmeasured | Tempted and satisfied unaided by both models. Retirement candidate pending a task that separates it. |
| `SCOPE-2` | unmeasured | Sonnet satisfies it in every arm; Haiku fails in every arm including with the skill. Below the window. |
| `SCOPE-3` | unmeasured | Never reached: neither task created a genuine domain lifetime. |
| `GRAPH-1` | unmeasured | Satisfied unaided in 11 of 12 runs. |
| `GRAPH-2` | unmeasured | Tempted and satisfied unaided by both models. |
| `GRAPH-3` | unmeasured | Not separately tempted. |
| `GRAPH-4` | unmeasured | Never reached: neither task created a dependency cycle. |
| `INJECT-1` | unmeasured | Tempted; both models satisfied it in nearly every run. |
| `INJECT-2` | unmeasured | Never reached: neither task supplied a runtime parameter. |
| `INJECT-3` | unmeasured | Not separately tempted. |
| `TEST-1` | unmeasured | Reached by neither task. |
