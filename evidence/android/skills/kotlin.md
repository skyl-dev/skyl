# Evidence: `android/kotlin`

Kotlin mechanics: the places where code compiles, reads correctly, and behaves differently from what
it looks like.

## What was run

Six evals across Opus 5, Sonnet 5, Haiku 4.5 and qwen3.7-max, including one run through a second
harness and one through a non-Anthropic provider. The most recent re-ran the whole skill from
scratch, because its earlier evidence had been gathered under a weaker task design.

## What loading the skill changed

All three of the effects below appeared on Haiku 4.5 and were consistent across runs. Sonnet 5
already handled them.

**Cancellation is not swallowed.** Unaided runs wrapped suspending work in a broad catch, which
silently absorbs cancellation and leaves work running after the screen that wanted it is gone.

**A re-triggered read is cancelled by the operator built for it** rather than by tracking a job by
hand, which races its own cancellation under fast input.

**Everything compared by equality lives in the constructor.** Unaided runs put a recomputed total in
the class body, where it sits outside `equals`, so a state object whose total changed compared equal
to the previous one and the screen never updated.

## What the tested models already handle

Not re-wrapping a call that already dispatches, replacing state rather than mutating it in place, and
making a genuinely absent field nullable rather than defaulted, were done unaided in every run of a
task built to tempt them.

## Where the skill did not change behaviour

Making a shared cold flow hot, and declaring a read-only type at a module boundary, were not picked
up in either arm.
