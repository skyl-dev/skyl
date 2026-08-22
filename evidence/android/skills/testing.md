# Evidence: `android/testing`

3 rules, 4 retired. The largest register in the family produced the smallest skill.

## What was run

| eval | models | arms | runs |
|---|---|---|---|
| 21 | Haiku 4.5, Sonnet 5 | control / +core / +core+testing | 24, two tasks |

## The finding

**Models build test seams. They build the wrong kind.**

A clock seam appears in **12 of 12** runs including every control. Nobody needed telling that a
twenty-four-hour expiry cannot be tested against the system clock. What separates is the *shape*.

| Sonnet | control | `+core` | `+testing` |
|---|---|---|---|
| clock supplied as a **parameter** | 0/2 | 0/2 | **2/2** |
| clock as a **mutable production field** *(viol)* | 2/2 | 2/2 | **0/2** |

The control wrote the problem out in its own comment:

```kotlin
/** Overridable in tests via friend-module access; defaults to the real clock. */
internal var clock: () -> Long = System::currentTimeMillis
```

A production field that exists because of a test, documented as such, and shipped. The skill arm
converted the object to a class with a constructor parameter.

**Static mocks: 0 of 12. Reflection: 0 of 12.** The wrong answers expected beforehand are not the
wrong answers models reach for. They reach for a widened mutable field, which looks responsible.

## Dropped before publication

Four rules, each with zero violations across twelve runs and every one predicted as
corpus-saturated before the run.

| rule | result |
|---|---|
| no sleeps, latches, or real waiting | 0 violations in 12 |
| never collect an unbounded stream to a list | 0 violations in 12 |
| a fake rather than a mock | 12 of 12 used a fake |
| reset process-wide state between tests | 10 of 12, no arm pattern |

## The most useful negative result

A rule saying *inject the dispatcher* landed in **0 of 12 runs, every arm**, while the clock rule
moved cleanly. **They are the same rule.** One stated the principle and the other stated a single
instance of it, under a different heading three sections away. The model built a parameter seam for
the clock and left a hardcoded dispatcher in the same file.

It was folded in rather than kept. **A principle stated once travels; the same principle stated
twice as two instances does not.**
