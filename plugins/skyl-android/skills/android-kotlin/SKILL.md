---
name: android-kotlin
description: "Kotlin mechanics on Android: coroutine scope and cancellation, flow collection, nullability and equality. Use when most of the code is Kotlin."
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
