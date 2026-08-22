# Evidence: `android/di`

11 rules on lifetime and graph shape: what lives how long, what may depend on what, and when a
wiring mistake is discovered.

## What was run

| eval | models | arms | runs |
|---|---|---|---|
| 14 | Haiku 4.5, Sonnet 5 | control / +core / +core+di | 24, two seeded tasks |

## What the measurement showed

On Haiku 4.5 and Sonnet 5, no rule separated. The task tempted **every scope decision this skill makes**: an object expensive to build, a cheap
stateless one, state scoped to a single screen, two bindings of one type needing a qualifier, and a
component the framework constructs itself. Both models made the right call on each without the skill
loaded.

These two models already make the right scope decisions on a task of this size. The skill states
them for models that do not, and for projects large enough that the decisions stop being obvious.

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
