# Evidence: `android/db`

Persistence: what is stored, what survives, what is stale, and what happens to local work that has
not reached the server.

## What was run

**5 evals, 94 recorded runs**, on Haiku 4.5 and Sonnet 5. Every run is archived: the generated
sources, the prompt each arm received, and the model each one reported.

One of them is partial: it was stopped part-way and is marked as such below.

## What loading the skill changed

**A write spanning more than one statement is one transaction.** Unaided Haiku runs wrote
delete-then-insert with no transaction every time the pattern came up; Sonnet used one.

**Where a secret goes.** This skill points at `android/security` rather than answering it, after a
measurement showed that carrying the same hazard in two skills made the smaller model worse rather
than better.

## What the tested models already handle

In a later eval, adding a column to a database documented as already shipped produced a version bump
and a migration in every run including controls, and nobody enabled destructive fallback. Writing an
edit locally first, marking it pending, and observing the store rather than polling were handled in
nearly every run. The seed shipped a refresh that cleared the table before fetching, which empties
the app if the fetch fails, and every arm replaced it.

That eval was stopped part-way, so its remaining findings are inconclusive.

## What one task could not show

One eval returned nothing, because its task specified the behaviour most of these rules describe:
several rules had nothing to act on and the rest were told what to do by the prompt. Recorded so the
result is not read as a measurement of the skill.

## A rule rewritten after measurement

A conflict rule first read "resolved by a server-assigned version, never by device clocks". It did
not land in any run: the task's API supplied no version and the rule named no alternative, so every
run used the device clock. A prohibition with no actionable branch for the common case is not
something a model can follow. It now states what to do when the server offers nothing.
