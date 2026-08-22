# Evidence: `android/networking`

Talking to a server: the client itself, what comes back, what happens when it does not, and how a
request is authorised.

## What was run

One eval on Haiku 4.5 and Sonnet 5, two tasks, control against `+core` against `+core+networking`.

## What loading the skill changed

**Setting a whole-call timeout rather than only the per-operation ones.** The per-operation defaults
are reasonable and do not bound the request: a call can keep resetting its own ten seconds while
never finishing, and the coroutine waiting on it is never resumed. Improved on Haiku.

This is also the one rule here whose reason came from reading the library's documented defaults
rather than from the corpus.

## What the tested models already handle

Attaching a token on the client rather than per endpoint, excluding the refresh request from its own
interceptor, and collapsing concurrent refreshes were all handled unaided on a task built to tempt
them.

## What this skill demonstrates

The claim register behind it was the richest of any axis in this family: 81 evidenced claims from 12
repositories. Heavy documentation predicts rules the models already follow, because the corpus and
the training data are the same material.
