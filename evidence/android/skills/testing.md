# Evidence: `android/testing`

What makes a test able to fail for the right reason.

## What was run

One eval on Haiku 4.5 and Sonnet 5, two tasks, control against `+core` against `+core+testing`.

## What loading the skill changed

**Models build test seams. They build the wrong kind.**

A clock seam appeared in every run including the controls: nobody needed telling that a twenty-four
hour expiry cannot be tested against the system clock. What changed was the *shape*. Unaided runs
opened a mutable production field for the test to reassign. One wrote the problem out in its own
comment:

```kotlin
/** Overridable in tests via friend-module access; defaults to the real clock. */
internal var clock: () -> Long = System::currentTimeMillis
```

A production field that exists because of a test, documented as such, and shipped. Loaded runs
converted the object to a class taking the clock as a constructor parameter.

Static mocks and reflection, the wrong answers expected beforehand, appeared in no run at all.

## What the tested models already handle

No sleeps or latches, never collecting an unbounded stream to a list, using a fake rather than a
mock, and resetting process-wide state were all done unaided. Four rules were dropped as a result.

## Why this skill is three rules

The claim register behind it was the largest in the family and almost none of it survived. Not
because the claims are wrong, but because they describe what these models already do.
