# Evidence: `android/compose`

14 rules, 2 retired. Only the interop rules have been through the current method; the rest predate
it.

## What was run

| eval | what it tested | models | arms | runs |
|---|---|---|---|---|
| 18 | the interop rules only | Haiku 4.5, Sonnet 5 | control / +core / +core+compose | 24 |

**The other 13 rules carry evidence from before the current method** and have not been re-run. Given
that every skill re-measured under the current method lost rules, this is the largest untested
surface in the family.

## Eval 18 was a null

The prediction, written before scoring, named this outcome as the falsifying one: *if nothing moves
anywhere, the rules were written from a corpus signal rather than a real model failure.* That is what
happened. `AndroidView` is one of the best-documented APIs in Compose, and its documentation is the
corpus.

| check | result |
|---|---|
| construct in `factory`, mutate in `update` | **12 of 12 correct**, every arm, zero violations |
| the hosted View is released | **22 of 24 correct** by outcome |
| forward the host's resume and pause | Sonnet 2/2 in **control**; Haiku 0/2 control, 0/2 `+core`, 1/2 with the skill |

Two rules retired. The third was dropped as an observation rather than a rule: the seed had no layout
to inflate, and the task requires an `AndroidView` in a lazy list, so the rule's own *not when*
covered the case it was written for.

## What survives, and why it is marked as not landing

`INTEROP-2`, forwarding the host's lifecycle. Both models call `onCreate` and `onDestroy`
unprompted. It is specifically the **resume and pause pair** that Haiku misses, in every arm, and
that is the pair which only fails after the app has been backgrounded, which is not something anyone
does while writing the screen.

Sonnet writes the observer in its control arm. Haiku writes it in one of two runs with the skill,
which is noise. Kept and recorded as not landing.

## A scoring error worth publishing

The first pass reported a clean separation on releasing the View. It was an artifact: the column
looked for `AndroidView`'s `onRelease` argument, and the Sonnet control released correctly through
`DisposableEffect { onDispose { ... } }` instead. Two correct mechanisms, one column, and the column
had a favourite. Re-scored on the outcome, the separation vanished entirely.

## Ledger

| rule | status | evidence |
|---|---|---|
| `INTEROP-2` | not-landing | Haiku 0/2 control and 1/2 with the skill. Sonnet does it unaided. |
| `EFFECT-1` | unmeasured | Predates the current method. |
| `EFFECT-2` | unmeasured | Predates the current method. |
| `EFFECT-3` | unmeasured | Predates the current method. |
| `EFFECT-4` | unmeasured | Predates the current method. |
| `REM-1` | unmeasured | Predates the current method. |
| `REM-2` | unmeasured | Predates the current method. |
| `SKIP-1` | unmeasured | Predates the current method. |
| `SKIP-2` | unmeasured | Predates the current method. |
| `SKIP-3` | unmeasured | Predates the current method. |
| `LAZY-1` | unmeasured | Predates the current method. |
| `TEXT-1` | unmeasured | Predates the current method. |
| `MOD-1` | unmeasured | Predates the current method. |
| `THEME-1` | unmeasured | Predates the current method. |
| `INTEROP-1` | retired | Correct in 12 of 12 task-A runs, every arm, zero violations. |
| `INTEROP-3` | retired | Dropped as an observation; its own *not when* covered the case. |
