# Evidence: `android/permissions`

Runtime permissions: whether to take one at all, how to ask, and what the app does with the answer.

## What was run

Two evals on Haiku 4.5 and Sonnet 5. The second re-ran the skill arm after two rules were rewritten,
with the expected result written down beforehand.

## What loading the skill changed

The two models improved on **different** rules, which is the clearest illustration in this family of
why a single model is not enough to judge a skill by.

**Not declaring a permission the app never requests.** Declaring `CAMERA` makes an intent that needs
no permission throw, and the merged manifest means a dependency can cause it in code nobody touched.
Unaided Haiku runs shipped exactly that failure.

**Removing a permission that was never needed.** Sonnet's loaded runs deleted the declaration and
kept the permission-free intent.

**Re-reading permission state when a screen becomes visible again.** A grant made in Settings
produces no callback, so a screen waiting on a result it asked for waits forever. Sonnet improved
here.

**Requesting the weakest form that serves the feature**, and not declaring a permission alongside the
permission-free path that replaced it. Both were added after reading the runs, and both improved on
Haiku in the follow-up eval.

## What the tested models already handle

Asking in context rather than at launch is the most-repeated advice in the permissions corpus and no
unaided run got it wrong, so it is not here taking up context.

## What the scoring could not see

Unaided Haiku shipped a `SecurityException` from a permission it never wanted. With the skill loaded
it fixed the measurement by *requesting* the permission and building a camera viewfinder, satisfying
one rule while breaking the one above it. Sonnet deleted the declaration and kept the intent. Same
column, two fixes of very different quality, so the rule now ranks them rather than accepting either.
