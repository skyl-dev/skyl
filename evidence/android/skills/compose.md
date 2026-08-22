# Evidence: `android/compose`

Compose mechanics, almost all of which follow from one fact: a composable may run on any frame, more
than once per frame, in any order, and be skipped entirely.

## What was run

**1 eval, 24 recorded runs**, on Haiku 4.5 and Sonnet 5. Every run is archived: the generated
sources, the prompt each arm received, and the model each one reported.

Covering the interop rules. The remaining rules carry evidence from earlier work under a weaker task
design and have not been re-run.

## What the tested models already handle

Constructing a hosted View once and mutating it thereafter, and releasing it when the composable
leaves, were done correctly in nearly every run including controls. `AndroidView` is among the
best-documented APIs in Compose, and its documentation is the corpus these models trained on.

Two rules were dropped as a result.

## What survives, and where

Forwarding the host's resume and pause to a hosted View. Both models call create and destroy
unprompted; it is specifically the resume and pause pair that Haiku misses, and that pair only fails
after the app has been backgrounded, which is not something anyone does while writing the screen.
Sonnet writes it unaided.
