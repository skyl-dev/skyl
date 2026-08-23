---
name: android/kotlin
axis: language
family: android
requires: [android/core]
version: 1.0.0
authors: [ahmmedrejowan]
agent_sections: [rules]
retired: [ASYNC-1, TYPE-2, SER-1]
detect:
  file: ["**/*.kt"]
  gradle_plugin: ["org.jetbrains.kotlin.android"]
---

## Rules

Kotlin mechanics. `android/core` owns the decision; this says how Kotlin expresses it, and only
where Kotlin expresses it in a way that goes wrong. A rule that would read the same in Java is
core's, not this file's.

Most of a Kotlin style guide is already a compiler error, a lint warning, or something the
formatter fixes. What is left is the small set of places where the code compiles, reads correctly
and behaves differently.

**Scope.** New code. Match the file you are editing.

**When not to apply**(whole-skill): a module with no coroutines and no shared state. And never raise these on code you are not otherwise changing.

**Priority.** `must`, the failure is silent or expensive. `should`, real exceptions exist; name
yours.

### Suspending and dispatch

- **ASYNC-2** `must`: Cancellation is not an error to catch. `runCatching`, `catch (e: Exception)`
 and `catch (e: Throwable)` all swallow `CancellationException`; re-raise it before handling
 anything else.
 *Why:* a coroutine that swallows its own cancellation keeps running after its scope is gone, so
 the work it was doing outlives the screen that wanted it and completes against a dead consumer.
 A timeout arrives as a cancellation but is not the caller's cancellation, which is why the two
 cases have to be told apart rather than both suppressed.
 *Not when:* never in a general catch. A `catch (e: IOException)` cannot catch cancellation and
 needs no guard, catching only what you can name is the better fix, and removes the question.
 See `references/cancellation.md`.
 *(`core WORK-2` states when work may be abandoned. This is the mechanism that leaks it.)*

- **ASYNC-3** `must`: Pick the scope builder by what should happen when one child fails.
 `coroutineScope` fails the group: one failure cancels the siblings and throws to the caller.
 `supervisorScope` isolates: one failing child leaves the others running, and does **not** handle
 the failure, so every child still needs its own handler.
 *Why:* they read as variants of one thing and answer opposite questions. The trap is assuming
 `supervisorScope` catches; it only stops the failure spreading sideways, and an uncaught child
 still crashes the process.
 *Not when:* a single child, then neither builder is doing anything.

- **ASYNC-4** `must`: A read that can be re-triggered, a query, a filter, a refresh, is cancelled
 by the operator built for it, `flatMapLatest` or `collectLatest`, not by tracking jobs by hand.
 The same operators are wrong for a write.
 *Why:* hand-tracked jobs race their own cancellation on fast input. And cancelling a write does
 not un-send it: the request may already have reached the server, so a re-triggered write handled
 this way is silently dropped until the first one finishes.
 *Not when:* every emission must be processed, then the operator is losing work by design.

- **ASYNC-5** `should`: A flow with more than one collector is made hot explicitly, with `stateIn`
 or `shareIn` and a stated sharing policy. A cold flow restarts its upstream for every collector.
 *Why:* two collectors on a cold flow means two network calls, two database cursors, and two sets
 of results that can disagree. The policy is the second half: `WhileSubscribed()` with no timeout
 tears down and re-runs the upstream on every configuration change, and `Eagerly` keeps it running
 after the last collector is gone.
 *Not when:* the flow genuinely has one collector for its whole life, a `stateIn` on something
 only one screen ever reads is ceremony.

### Types and equality

- **TYPE-1** `must`: Everything `equals` should compare goes in the data class's primary
 constructor. A property declared in the class body is excluded from `equals`, `hashCode`, `copy`
 and destructuring.
 *Why:* the exclusion is silent. A state holder that drops updates it considers equal will drop
 every update that differs only in a body property, with no crash and no log.
 *Not when:* the property is genuinely derived and should not participate, then make it a getter
 which documents that choice.

- **TYPE-3** `should`: A type crossing a boundary declares its read-only shape: `List`, not
 `MutableList`; `val`, not `var`.
 *Why:* `List` is an interface, and the object behind it can be a `MutableList` that its creator
 still holds. Declaring the read-only type is what makes the contract inspectable at the call
 site, where the reader is.
 *Not when:* inside a single function, where the mutation and its scope are visible together.

## Why

<!-- human-only: not installed -->

**Why `suspend` is not what it looks like.** It reads like `async` and promises none of it: not
non-blocking, not off the main thread, not automatically cancellable. What makes the ecosystem
workable is a convention, not a guarantee, that a `suspend` function is safe to call from any
dispatcher, because it handles its own dispatching internally. Once one caller starts adding its
own `withContext`, every caller has to know the callee's internals to avoid double-switching, and
one of them will guess wrong. The convention only holds if everyone keeps it.

**Why cancellation is the one that survives review.** `CancellationException` is a normal exception
on the JVM, so `catch (e: Exception)` catches it, and so does `runCatching`. A coroutine that
swallows its own cancellation keeps running after its scope is gone: the screen is destroyed, the
work continues, and it completes against a consumer nobody is listening to. Nothing crashes and
nothing logs, which is why it survives review, the code reads as careful error handling.

The deeper trap is that a timeout arrives *as* a cancellation. `withTimeout` cancels the body, so
code that suppresses all cancellation cannot tell "the user navigated away" from "this took too
long", and the two need opposite responses.

**Why the two scope builders get mixed up.** `coroutineScope` and `supervisorScope` read as variants
of one thing and answer opposite questions. `coroutineScope` treats its children as one unit, if
any part fails, the whole thing failed, so cancel the rest and tell the caller. `supervisorScope`
treats them as things that merely happen together, the header, the list, the banner, where one
failing should not blank the other two.

The trap is assuming `supervisorScope` also *handles* the failure. It does not. It stops the failure
spreading sideways, and an uncaught child still crashes the process. Every child needs its own
handler.

**Why the equality trap is silent.** Four reasonable behaviours combine into one invisible bug. A
state holder drops emissions it considers equal. `copy()` copies references rather than contents.
Properties declared in the class body are excluded from `equals`, `hashCode`, `copy` and
destructuring. And a `List` is an interface, so the object behind it may be a `MutableList` its
creator still holds.

Each is defensible alone. Together they give you a screen that stops updating with no crash, no
log, and nothing to search for. Most "why isn't my UI refreshing" time is spent here.

**Why a serialization default is not a convenience.** A default on a `@Serializable` property means
"absent is acceptable". The moment a server stops sending a field, every object deserialises
successfully carrying a value nobody chose, and it looks exactly like a value someone did choose.
Nullable is the honest encoding of "this may not arrive", because it forces the decision at the use
site instead of hiding it at the parse site.

**What changed, if you learned Kotlin earlier.**| Then | Now |
|---|---|
| `runBlockingTest`, `TestCoroutineDispatcher` | `runTest`, `TestScope`, the old ones are gone |
| `values()` | `entries` |
| `object Loading` | `data object Loading` |
| `sealed class` by default | `sealed interface` unless you need shared state |
| `else -> {}` to satisfy a `when` | a non-exhaustive `when` on a closed set is a compile error |
| `GlobalScope` for "fire and forget" | a scope with an owner, or durable work |

## Pitfalls

<!-- human-only: not installed -->

- **The screen stops updating and nothing is wrong.** The equality trap: a mutated list inside a
 copied state object compares equal, so the update never emits.
- **A field that should have changed the UI is ignored.** It is declared in the class body, so it is
 not part of `equals`.
- **Work continues after the user leaves the screen.** A `runCatching` or `catch (e: Exception)`
 swallowed the cancellation.
- **A timeout that behaves like a navigation, or vice versa.** Both arrive as cancellation and the
 code suppressed both.
- **One failing section blanks the whole screen** `coroutineScope` where `supervisorScope` was
 meant. Or **the process crashes from a child that "should have been isolated"** `supervisorScope`
 without a handler on the child.
- **Two network calls for one screen.** A cold flow with two collectors and no `stateIn`.
- **The list reloads on every rotation.** `WhileSubscribed()` with no timeout, tearing down and
 restarting the upstream across the configuration change.
- **Search results arrive out of order under fast typing.** Hand-tracked jobs instead of
 `flatMapLatest`.
- **A re-triggered write silently does nothing.** `flatMapLatest` on a write: cancelling the client
 does not un-send the request.
- **A field the server stopped sending is quietly a default.** A `@Serializable` default where
 nullable was meant.

## Provenance

<!-- human-only: outside agent_sections, never installed -->

**This section was missing until 22-Aug-2026** as it was in `compose`. Both shipped without one.

**eval 22 re-ran this skill under the current bar and it held better than expected.** Three of nine rules separated, all of them on Haiku, all `2/2 → 0/2` in the violation direction with
the `+core` arm flat:

| rule | Haiku ctl → +core → +kotlin | Sonnet |
|---|---|---|
| `ASYNC-2` cancellation swallowed | **2/2 → 2/2 → 0/2**| 0/6 |
| `ASYNC-4` job tracked by hand | **2/2 → 2/2 → 0/2**| 0/6 |
| `TYPE-1` stored property in a body | **2/2 → 2/2 → 0/2**| 1/2 → 0/2 |

Sonnet satisfies all three unaided; Haiku fails all three unaided and is fixed in every skill run.
That is the capability window measured about as cleanly as this project manages. `ASYNC-2` and
`ASYNC-4` were the two rules carrying evidence from the old design (0/3 → 3/3 and 1/3 → 3/3), and
both reproduce here, the old numbers were small but they were not wrong.

**Retired as satisfied unaided:** `ASYNC-1` (don't re-wrap a call that already dispatches, 0
violations in 12, every arm), `TYPE-2` (replace state rather than mutating it, 0 in 12), and
`SER-1` (absence is nullable, not defaulted, 0 in 12, with 10 of 12 making the field nullable
without being told).

**Kept but not landing:** `ASYNC-5`, making a shared cold flow hot appears in 1 of 12 runs. Two
screens read one cold flow and nobody noticed, with or without the rule. `TYPE-3`, the cache still
hands out its own `MutableList` in 12 of 12, untouched by any arm.

**Never tempted:** `ASYNC-3`. Neither task creates a group of concurrent children.

The first attempt at this eval is void, it ran inside the repo, so the agents could read this file.
See `evals/android/eval-22-kotlin/VOID.md`. The re-run verified isolation before scoring.

One correction from that earlier work is worth carrying: `kotlin` v0.2 taught serialisation in a way
that led an eval arm to use `limitedParallelism(1)` as a mutex, which caps concurrency without
holding the slot across a suspension. Teaching cleverness produced a subtle bug, and the rule was
rewritten to prefer the standard-library answer.
