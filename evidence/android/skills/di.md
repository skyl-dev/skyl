# Evidence: `android/di`

Lifetime and graph shape: what lives how long, what may depend on what, and when a wiring mistake is
discovered.

## What was run

**1 eval, 48 recorded runs**, on Haiku 4.5 and Sonnet 5. Every run is archived: the generated
sources, the prompt each arm received, and the model each one reported.

Two seeded tasks, control against `+core` against `+core+di`.

## What the measurement showed

On these two models, no rule changed behaviour. The task tempted every scope decision the skill
makes: an object expensive to build, a cheap stateless one, state scoped to a single screen, two
bindings of one type needing a qualifier, and a component the framework constructs itself. Both
models made the right call on each unaided.

These models already make these decisions correctly on a task of this size. The skill states them for
models that do not, and for projects large enough that the decisions stop being obvious.

## One difference between models

Scoping state to the screen that owns it: Sonnet does it in every arm, Haiku in none, loaded or not.

## What this skill demonstrates

The claim register behind it was the largest of any axis, and nearly all of it was library API
detail, which the rule that a topic groups by concern rather than by library excludes.
