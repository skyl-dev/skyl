---
name: android/java
axis: language
family: android
requires: [android/core]
version: 1.0.0
authors: [ahmmedrejowan]
agent_sections: [rules]
detect:
 file: ["**/src/main/java/**/*.java"]
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

## Why

<!-- human-only: not installed -->

**Why this skill is not a Java style guide.** Because the tools already are one. Checkstyle, PMD and
spotless enforce member ordering, brace style, line length and Javadoc, and they do it without
spending a rule slot or a token. What is left after the linter is the set of things that compile
read correctly, and behave differently, and on Android that set is almost entirely about two
seams: the boundary with Kotlin, and the absence of structured concurrency.

The published material does not cover this. Search for Java-on-Android guidance and you find
migration guides, how to leave Java, written by people leaving it. That is useful and it is a
different subject. This is for the code that is still there, and will be for years.

**Why nullability annotations matter more in Java than they look.** Kotlin's null safety is a
compile-time guarantee, and it is only a guarantee about types Kotlin can reason about. Unannotated
Java is a *platform type*: Kotlin will let you assign it to a non-null type, dereference it without
a check, and pass it anywhere, and the compiler says nothing, because it has no information. The
null then surfaces inside Kotlin code that never declared it could be null.

So the annotation is not documentation. It is the switch that turns the guarantee back on, and its
absence disables the main safety feature of the other half of the codebase.

**Why the interop annotations exist and why they are forgotten.** A Kotlin `companion object`
member is `Companion.get()` from Java. A `const val` is a getter unless it is `@JvmField`. Default
arguments do not exist in Java at all, they compile to a single method with every parameter. And a
Kotlin function that throws does not declare it, so a Java caller cannot `catch` a checked exception
it does not know about.

None of that is visible from the Kotlin side. The file looks fine, the module compiles, and the
break is in a Java file nobody opened. That asymmetry is why these are forgotten and why they belong
in a rule.

**Why the leak surface is genuinely Java's, not Android's.** Android gets blamed for these leaks and
the language is the cause. A non-static inner class in Java holds a reference to its enclosing
instance, implicitly and invisibly, you cannot see it at the call site, and it is not in the
constructor. So an anonymous `Runnable` posted to a `Handler` from an activity holds that activity
and the activity holds its window, its views, and every bitmap in them.

The consequence is that Java's most natural way to write a callback is also its most reliable way to
leak a screen. `static` nested class plus `WeakReference` is the fix, and it is ugly enough that
people skip it, which is why it needs to be a rule rather than a preference.

**Why asynchrony is the hardest part of maintaining Java on Android.** Kotlin gives you a scope that
cancels, a suspend function that cannot be called from the wrong place, and a compiler that tracks
it. Java has none of that. Every one of those guarantees becomes something a human must remember, clear the callback, check the component is alive, do not touch the UI from the pool. The rules in
that section are all the same rule from different angles: *nothing here cancels itself.*

**Why a conversion must not change behaviour.** The only reason a conversion is safe to merge is
that a reviewer can check nothing changed. Fold in a fix, a different exception, a reordered side
effect, a tightened visibility, and neither half is verifiable: the diff is too large to read as a
behaviour change and too behavioural to read as a translation. Worse, when a regression appears six
months later it gets attributed to "the Kotlin migration", and that attribution outlives everyone
who could correct it.

The automatic converter is a syntactic tool, and it is honest about that. It produces platform types
where the Java had annotations, `!!` where it could not prove non-null, and `var` where the field
was effectively final. All of it compiles. None of it is what you would have written.

## Pitfalls

<!-- human-only: not installed -->

- **A null crossing into Kotlin and throwing three frames later** in code that never declared the
 value could be null. Unannotated Java.
- **A Java file that stops compiling after a Kotlin file was converted.** `@JvmStatic`, `@JvmField`
 or `@JvmOverloads` was dropped, or a getter replaced a field.
- **A checked exception nobody catches** because the Kotlin that throws it never declared `@Throws`.
- **A leak that grows with every rotation.** A listener registered and never cleared, with no scope
 to cancel it.
- **An activity that survives its own destruction until a delayed message fires.** An anonymous
 `Runnable` posted to a `Handler`, holding the enclosing instance.
- **One screen's worth of views held for the life of the process.** An `Activity` or its `Context` in
 a `static` field or a singleton, usually with the lint warning suppressed.
- **Rx subscriptions accumulating across navigations.** No `CompositeDisposable`, or one that is
 never cleared.
- **`git blame` stopping at "convert to Kotlin".** The rename and the content change were one
 commit.
- **A crash on a detached fragment** from a background result that arrived after the screen was
 gone.
- **The whole app's background work stalled behind one slow task.** `AsyncTask`'s serial executor.
- **A background failure that reports nothing at all.** `AsyncTask` swallowing the exception thrown
 in `doInBackground`.
- **A `Handler` posting to the wrong thread, or messages silently dropped.** `new Handler()` adopting
 whichever `Looper` happened to be current.
- **A callback where both the result and the error are null** or both are set, and every call site
 handles it differently.
- **A regression blamed on "the Kotlin migration"** for years, because a behaviour change was folded
 into a conversion commit.
- **`!!` scattered through freshly converted code** from the converter rather than from a decision.

## Provenance

<!-- human-only: outside agent_sections, never installed -->

**Partly measured.** Eval 11 ran control, `+core` and `+core+java` arms across Haiku 4.5 and
Sonnet 5, 24 runs. Task A of that eval was discarded as invalid, so six rules remain untested. What
follows records both what separated and what the eval got wrong about this skill.

**Added later:** the `LEAK-*` rules and `CONVERT-4`/`CONVERT-5` after re-reading the claim register
rather than the extraction summary. the first draft had been made from the summary, and missed the
Android-Java cluster the evidenced claims actually name: implicit outer references in inner classes
and `Handler`s, `Activity` references in static fields and singletons, Rx subscriptions with no
`CompositeDisposable`, characterization tests before conversion, and separating the rename commit
so `git blame` survives. `ASYNC-3` was folded into `LEAK-3`.

**Added later:** the shared precedence sentence now carried by `core`, `mvvm` and `db` as well, so the
rule below is stated in the same terms across the set rather than only here.

**Added later:** a statement of a precedence the file had left implicit. Eval 11 scored `LEAK-2` as failing to
land, 1 of 12 runs, and reading the runs showed the opposite: every treated run kept the static
singleton holding a `Context` **because `CONVERT-1` says preserve behaviour exactly** which is the
correct resolution. The models arbitrated between two rules in this file and got it right; the file
just never said which wins. `LEAK-2` now carries the conversion exception and `CONVERT-1` states that
it outranks the structural rules during a conversion. The detector had scored a right answer as a
miss.

Eval 11 also found `CONVERT-1`'s observation-contract clause unnecessary, all 12 runs kept
`java.util.Observable` and none swapped it for a `Flow`, in any arm on either model. Kept anyway, on
the same basis as elsewhere: it costs little and the sample is two per cell.

`ASYNC-5` (explicit `Looper`) separated on both models, 0/2 control to 2/2 treated. `INTEROP-1`
separated on Haiku, 0/2 to 2/2, and is inert on Sonnet. Task A of that eval was discarded as invalid
so `NULL-1`, `LEAK-1`, `LEAK-3` and `ASYNC-1/2/4` remain untested.

**Corrected later:** a factual error and adds one rule, both from web verification against primary
sources rather than the corpus. `ASYNC-1` claimed `AsyncTask` was *removed from the platform*; it is
**deprecated since API 30 and still present**. The real reasons are better than the one I wrote: it
swallows exceptions thrown in `doInBackground`, and its default executor is serial. `ASYNC-5` is new, `new Handler()` and `new Handler(callback)` are deprecated at API 30 because they silently adopt
the current thread's `Looper`. The corpus does mention this in passing; no evidenced claim carried
it.

Its **scope** is evidenced rather than assumed. The corpus holds 260 claims across 11 files from
4 repos, and the extraction found that ** nobody writes about Java-on-Android as a language to write
well in**. The best source in the set, `nextcloud/android`'s `android-java-to-kotlin`, which cites
its own PR numbers, is a *migration* skill: roughly 90 of its ~150 claims belong to `kotlin` or
`core`, not here. Two others are Android-architecture skills that happen to use Java syntax. The one
file that does treat Java as a language with a house style is the least evidenced in the set and is
largely lint-shaped.

So this skill covers what that material actually supports, the Java-shaped half of a mixed
codebase and the discipline for leaving it, and deliberately does not invent the Java style guide
the corpus does not contain.

See `registers/android/language/java/notes.md`.
