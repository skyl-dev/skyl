---
name: android-java
description: "Java on Android without the language features Kotlin has: threading, equality, resource handling, and interoperating with Kotlin. Use for a Java codebase or the Java half of a mixed one."
---

## Rules

Java on Android, in the codebase you actually have: a large Java app, or a Kotlin app with Java
still in it. `core` owns the architecture. `kotlin` owns the Kotlin half and everything about
coroutines. This owns the Java half, what it must do without the language features Kotlin has, and
what must not change when someone starts converting it.

**This is not a Java style guide.** Member ordering, brace style, Javadoc obligations and parameter
counts are already enforced by Checkstyle, PMD or spotless, and a rule the formatter fixes is a rule
that costs a slot for nothing.

**Scope.** New Java code in an existing Java module, and the seam where Java meets Kotlin. New
modules should be Kotlin.

**When a rule here conflicts with the code you are editing** the surrounding convention wins for
style and structure, but never for a rule whose failure loses user data, leaks a credential, or
ships a crash. Fix those in their own change, not inside another one.

**When not to apply**(whole-skill): a greenfield module. Write it in Kotlin.

**Priority.** `must`, the failure is silent or crosses the language boundary. `should`, real
exceptions exist; name yours.

### Nullability

- **NULL-1** `must`: Every parameter and return type in a class Kotlin can see is annotated
 `@Nullable` or `@NonNull`.
 *Why:* unannotated Java arrives in Kotlin as a *platform type* a type whose nullability the
 compiler cannot check, so it stops enforcing anything and
 a null crosses the boundary silently and throws somewhere in the Kotlin code that never declared
 it could be null. The annotation is the only thing that makes the boundary checked, and it costs
 one word. *Not when:* a private method with no Kotlin caller.

- **NULL-2** `must`: Validate arguments at public entry points rather than relying on the eventual
 dereference to throw.
 *Why:* Java has no `?.` and no compiler check, so the failure surfaces wherever the value is
 finally used, usually a frame or two away, and often on another thread, where the stack trace no
 longer names the caller who passed the null.
 *Not when:* a hot path where the check is measurable, and the contract is documented.

### Interop with Kotlin

- **INTEROP-1** `must`: Kotlin declarations that Java still calls carry the annotations that keep
 them callable: `@JvmStatic` for companion members, `@JvmField` for constants read as fields
 `@JvmOverloads` for defaults, `@Throws` for checked exceptions Java must catch.
 *Why:* without them the Java call site changes shape, `Companion.get()`, a getter instead of a
 field, one overload instead of four, and a checked exception the Java compiler cannot see. That is
 a compile break in a module nobody was editing.
 *Not when:* no Java caller remains, and then delete the annotations rather than leaving them.

- **INTEROP-2** `should`: Keep the Java-facing surface of a converted class the same shape until
 the last Java caller is gone: same visibility, same names, same exception types.
 *Why:* conversion is meant to be invisible to callers. A `private` that was package-private, or a
 renamed getter, turns one file's conversion into a change across the module, and the diff no
 longer shows whether behaviour changed.
 *Not when:* the caller is being converted in the same change.

### Leaks, the surface Java has and Kotlin mostly does not

- **LEAK-1** `must`: A non-static inner class, an anonymous class, or a lambda that outlives the
 method holds the enclosing instance. Anything posted, scheduled or registered from an `Activity`
 `Fragment` or `View` is a `static` nested class with a `WeakReference`, or is cancelled in the
 matching teardown.
 *Why:* the capture is implicit and invisible, a `Handler`, a `Runnable`, a `TimerTask` or a
 listener written inline holds `this`, and `this` is the whole view hierarchy. The classic is a
 `Handler` posting a delayed message: the activity is destroyed, the message is still queued, and
 the activity cannot be collected until it fires. Kotlin makes this rarer by having no implicit
 outer reference in the same places; Java does it by default.
 *Not when:* the object provably does not outlive the method, a `Comparator` passed to a sort.

- **LEAK-2** `must`: No `Activity`, `Fragment`, `View` or their `Context` is held in a `static`
 field, a singleton, or a collection that outlives the screen. Long-lived objects take the
 application context.
 *Why:* a static field lives for the process. One activity reference in one static collection
 keeps every view, every bitmap and every listener it owns alive for the life of the app, and it
 grows with each rotation. `StaticFieldLeak` is a lint check for exactly this and is routinely
 suppressed. *Not when:* the value is genuinely application-scoped and holds no `Context` at all, **or you are converting existing code, where `CONVERT-1` outranks this.** Fix the leak in its own
 change, before or after, never inside the conversion.

- **LEAK-3** `must`: Every subscription, observer and callback registered against a component is
 released in the matching lifecycle callback. Rx subscriptions go into a `CompositeDisposable`
 that is cleared in `onDestroy`.
 *Why:* Java has no scope that cancels. Nothing is released because the screen went away, the
 release is a line someone has to write, and the leak grows with every navigation.
 *Not when:* the API already ties the subscription to a lifecycle owner.

### Asynchrony without coroutines

- **ASYNC-1** `must`: Background work runs on a shared `Executor` owned by the application, never
 on a raw `new Thread()` and never on `AsyncTask`.
 *Why:* `AsyncTask` has been deprecated since API 30 and it swallows exceptions thrown in
 `doInBackground`, the work fails, nothing is reported, and the callback simply receives nothing.
 Its default executor is also serial, so every task in the app queues behind the slowest one. A
 bare thread has no pool, no lifecycle and no way to be cancelled or observed.
 *Not when:* a genuinely one-off thread with a documented lifetime, rare enough to be worth a
 comment.

- **ASYNC-2** `must`: An asynchronous API reports success and failure on separate paths, two
 callback methods, or a result type with both cases, never a single callback with a nullable
 result and a nullable error.
 *Why:* Java has no sealed types and no `Result`, so "both null" and "both set" are states the
 compiler permits and every caller must handle. A callback pair makes the two outcomes
 unrepresentable together. *Not when:* the operation genuinely cannot fail.

- **ASYNC-4** `must`: Check that the component is still alive before touching UI from a background
 result.
 *Why:* the work has no idea the screen is gone. Without the guard the callback lands on a detached
 fragment or a finished activity, and the crash is a `IllegalStateException` far from the code that
 started the work. *Not when:* the result is delivered by something already lifecycle-aware.

- **ASYNC-5** `must`: A `Handler` is constructed with an explicit `Looper`. `new Handler()` and
 `new Handler(callback)` are deprecated.
 *Why:* the no-argument forms silently adopt the current thread's `Looper`, so the handler attaches
 to whichever thread happened to construct it. The failures are all quiet ones: messages posted to
 a looper that has quit are dropped, construction on a thread with no active looper throws, and the
 same code behaves differently depending on the caller. `Looper.getMainLooper()` says what you
 meant. *Not when:* the surrounding code already passes one.

### Converting to Kotlin

- **CONVERT-1** `must`: A conversion preserves behaviour exactly, including the exception type
 thrown, the order of side effects, and the notification contract of anything observable. Change
 behaviour in a separate commit.
 *Why:* the value of a conversion is that it is reviewable, a reviewer checks that nothing changed.
 Fold a behaviour change into it and neither half can be verified, and a regression is attributed to
 "the Kotlin migration" for years.
 **This rule outranks every structural rule in this file during a conversion.** If the Java holds a
 `Context` statically (`LEAK-2`) or captures an outer reference (`LEAK-1`), the conversion keeps it
 and the fix is a separate change. A conversion that also repairs a leak is neither reviewable as a
 translation nor as a fix.
 *Not when:* the original behaviour is the bug being fixed, and then it is not a conversion.

- **CONVERT-2** `should`: Convert leaves before callers: a class with no Java dependents first, one
 class per change.
 *Why:* every conversion changes a Java-facing surface (`INTEROP-1`), and converting a widely-called
 class first means fixing every call site in the same diff. *Not when:* a small, self-contained
 cluster that only makes sense together.

- **CONVERT-3** `must`: After the automatic converter runs, the result is reviewed as new code, not
 accepted as a translation.
 *Why:* the converter is syntactic. It produces platform types where the Java had annotations
 `!!` where it could not prove non-null, and `var` where the field was effectively final, all of
 which compile and none of which are what you would have written. *Not when:* never.

- **CONVERT-4** `must`: A class with no tests gets a characterization test pinning current
 behaviour **before** it is converted.
 *Why:* `CONVERT-1` says preserve behaviour, and without a test that claim is an assertion. The
 test does not need to be good or permanent, it needs to fail if the conversion changed anything.
 *Not when:* the class is already covered.

- **CONVERT-5** `must`: Do the conversion in separate commits: the file rename on its own, then the
 mechanical conversion, then the idiomatic pass.
 *Why:* a rename combined with a content change breaks `git blame`, and the history of the file
 that most needs history is the one that just changed language. Mechanical and idiomatic separated
 means a reviewer can read the second diff as the only place behaviour could have moved.
 *Not when:* a file small enough that the whole thing is readable at once.
