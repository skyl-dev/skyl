---
name: android/di
axis: topic
family: android
requires: [android/core]
version: 1.0.0
authors: [ahmmedrejowan]
agent_sections: [rules]
detect:
  gradle_dependency:
    - "com.google.dagger:hilt-android"
    - "io.insert-koin:koin-android"
    - "com.google.dagger:dagger"
    - "dev.zacsweers.metro:runtime"
---

## Rules

How the object graph is wired: what lives how long, what may depend on what, and when a mistake in
the wiring is discovered. `core` owns that dependencies are supplied rather than constructed
(`BOUND-2`). `mvvm` owns where an interface is declared. This owns lifetime and the shape of the
graph.

**This is about the concern, not the container.** Where a rule names a mechanism it is the ordinary
one; the same rule holds under Hilt, Koin, Dagger or Metro, and the failure it prevents is the same.

**When a rule here conflicts with the code you are editing** the surrounding convention wins for
style and structure, but never for a rule whose failure loses user data, leaks a credential, or
ships a crash. Fix those in their own change, not inside another one.

**Scope.** New bindings and new modules. Match the container already configured.

**When not to apply**(whole-skill): an app small enough that construction happens in one place and
nobody is testing it.

**Priority.** `must`, the failure leaks, crashes, or is silent. `should`, real exceptions exist;
name yours.

### Lifetime

- **SCOPE-1** `must`: A binding is unscoped by default. Add a scope only when the object holds
 state that must be shared, or is genuinely expensive to build.
 *Why:* a scope is a lifetime, not a performance setting. A scoped object survives until its
 component dies, so scoping everything keeps objects alive that nobody is using and makes a
 test-time replacement leak into the next test. Mappers, formatters and use cases are cheap and
 stateless; making them singletons buys nothing and hides where state actually lives.
 *Not when:* a cache, a connection pool, or a client whose whole point is being shared.

- **SCOPE-2** `must`: Nothing longer-lived depends on something shorter-lived. An
 application-scoped object never holds an `Activity`, a `Fragment`, a `View`, their `Context`, or a
 `ViewModel`.
 *Why:* the dependency outlives the thing it depends on, so it either leaks it or holds a reference
 that is already dead. An `Activity` in a singleton keeps its whole view tree alive for the life of
 the process, and it grows with every rotation. Where a long-lived object needs a context, that is
 the application context.
 *Not when:* never, if it seems necessary, the dependency is pointing the wrong way.
 *(`java LEAK-2` and `mvvm VM-2` state the same failure where it arises in a static field and in a
 ViewModel. This is the graph-level decision: the scope you chose is longer than the thing you are
 injecting.)*

- **SCOPE-3** `should`: A scope is defined for a lifetime that actually exists in the app. Do not
 invent one where a standard scope fits.
 *Why:* every custom scope is a lifetime someone has to reason about at each injection site, and
 most apps only have three that matter: the process, the screen, and the thing on screen right now.
 *Not when:* a genuine domain lifetime, a logged-in session, a checkout flow, that no standard
 scope matches.

### The graph

- **GRAPH-1** `must`: A missing or ambiguous binding is discovered before the user sees it: at
 compile time where the container offers it, and by a graph test where it does not.
 *Why:* a container that resolves at runtime turns a wiring mistake into a crash on app start, on a
 screen nobody opened during testing. The test costs one file and converts that into a red build.
 *Not when:* never. If the container verifies at compile time this is free; if it does not, the test
 is the substitute.

- **GRAPH-2** `must`: Two bindings of the same type are distinguished by a qualifier, and every
 provider of that type is qualified once one of them is.
 *Why:* an unqualified duplicate is either a compile error or, worse, in a runtime container, a
 silent choice of the wrong instance. Qualifying one provider and not its sibling is the case that
 compiles and injects the wrong thing.
 *Not when:* the type is genuinely unique in the graph.

- **GRAPH-3** `should`: Prefer a compile-time-checked qualifier over a string name.
 *Why:* a typo in a string qualifier is a runtime failure with no compiler help, and a rename does
 not follow. *Not when:* interoperating with a container or a migration that uses names.

- **GRAPH-4** `must`: Break a dependency cycle by extracting the shared contract or deferring one
 side, never by reaching around the graph.
 *Why:* a cycle means two things each need the other fully built. The container reports it; a
 service-locator lookup to escape it hides the cycle instead of removing it and moves the failure
 to runtime. *Not when:* never, a cycle is a design fact, not a container limitation.

### How things are injected

- **INJECT-1** `must`: Dependencies arrive through the constructor. Field injection only where the
 framework constructs the object and you cannot, an `Activity`, a `Fragment`, a `Service`, a
 `BroadcastReceiver`, a `View`.
 *Why:* a constructor states what a class needs, so the compiler enforces it and a test can supply
 it without a container. Field injection hides the same information and produces an object that is
 briefly, legally, incompletely constructed.
 *Not when:* the framework owns construction, and then the list of injected fields is the
 documentation the constructor would have been.

- **INJECT-2** `must`: A value known only at runtime is passed in, not injected. Assisted injection
 or a plain parameter, never a mutable global the graph reads later.
 *Why:* the graph is built before the value exists. Wiring one in means either a binding that
 cannot be satisfied at build time or a placeholder that is empty when something reads it early.
 *Not when:* the value is a navigation argument, where saved state is simpler and survives process
 death.

- **INJECT-3** `should`: Third-party SDK construction happens behind a binding you own.
 *Why:* it is what lets a test replace the SDK without the code under test knowing, and what keeps
 a vendor's initialisation out of the call sites that use it. *Not when:* the SDK is already a thin
 interface you control.

### Testing

- **TEST-1** `must`: A test replaces a binding through the container, not by reaching past it.
 *Why:* a mock assigned to a field the container also populates is overwritten, or is not, and
 which one happens depends on ordering the test does not control. The container has a replacement
 mechanism; a mock the container cannot see is not in the graph.
 *Not when:* the object under test takes its dependencies through its constructor, where no
 container is involved at all, which is the reason `INJECT-1` exists.

## Why

<!-- human-only: not installed -->

**Why a scope is a lifetime, not a speed setting.** `@Singleton` reads like an optimisation and is
not one, it is a declaration that this object lives until its component dies, which for an
application component is the life of the process. Scoping a stateless mapper does not make it
faster; it keeps it alive forever and, more importantly, it hides where state lives. When everything
is a singleton you can no longer tell by reading which objects are shared, so nobody knows which
ones are safe to mutate.

The corollary is the one people miss: scope is also what makes a test dirty. A scoped fake replaced
in one test is the same instance the next test receives.

**Why the direction of a dependency is a lifetime question.** An object may only depend on things
that live at least as long as it does. Point that the wrong way, an application-scoped object
holding an `Activity`, and you have either a leak or a reference to something already destroyed.
The graph makes this visible in a way ordinary code does not: the scope annotations are right there
and a longer scope depending on a shorter one is a mistake you can see without running anything.

The same failure appears in three places in this set, with three mechanisms: a static field
(`java LEAK-2`), a ViewModel (`mvvm VM-2`), and a scope mismatch here. Same leak, three ways in.

**Why runtime values do not belong in the graph.** The graph is built before your data exists. A
binding for "the current order id" cannot be satisfied at construction time, so it becomes either a
build failure or a mutable holder that is empty when something reads it early, and *early* is a
race you will not reproduce. Pass it as a parameter. Assisted injection exists precisely for the
case where some arguments come from the graph and some from the caller.

**Why a runtime container needs a test that a compile-time one does not.** A container that resolves
at compile time reports a missing binding as a build error. One that resolves at runtime reports it
as a crash, on app start, or worse, on the one screen nobody opened before release. The graph test
is what converts the second into the first. It costs one file and it is the difference between a red
build and a support ticket.

**Why field injection is not just style.** A constructor is a statement of what a class needs; the
compiler enforces it and a test can satisfy it with no container at all. Field injection makes the
same object constructible in an incomplete state, legally, briefly, and moves the requirement out
of the signature into a convention. It is the right answer only where the framework constructs the
object and you genuinely cannot intervene.

## Pitfalls

<!-- human-only: not installed -->

- **Memory that never comes down, and a leak that grows with rotations.** An `Activity` or its
 `Context` reachable from an application-scoped object.
- **A test that passes alone and fails in a suite.** A scoped fake surviving into the next test.
- **The wrong instance injected, silently.** Two providers of one type, one qualified and one not.
- **A crash on app start after a refactor.** A runtime container, a binding removed, and no graph
 test.
- **A crash on one screen that nobody opened before release.** The same, later.
- **A `lateinit` property not initialised.** A framework-constructed class missing its entry point.
- **A binding that cannot be satisfied at build time.** A runtime value wired into the graph.
- **Everything is a singleton and nobody knows what is shared.** Scope used as an optimisation.

## Provenance

<!-- human-only: outside agent_sections, never installed -->

**Eval 14 was a null: no rule separated.** 24 runs, two seeded tasks, Haiku 4.5 and Sonnet 5. Task A
tempted every scope decision this skill makes, expensive object, cheap object, screen-scoped state
duplicate type needing a qualifier, framework-constructed class, and both models made the right
call on each without the skill.

One model-dependent result: Sonnet scopes screen-only state to the screen in every arm; Haiku never
does, in any arm, **including with the skill loaded.** Below the capability window rather than
unnecessary.

Not redesigned, deliberately. The null is not a task failure, a different task tempting the same
rules would measure the same defaults. `GRAPH-4` (cycles), `SCOPE-3` (custom scopes) and `INJECT-2`
(runtime parameters) were never reached and remain unmeasured.

The register behind this skill was the largest of any axis at 154 evidenced claims from 15 repos
and nearly all of it was library API detail excluded by the concern-not-library rule. Register size
has now predicted result thinness three times running: `xml` 29 claims → 4 rules separated;
`networking` 81 → 1; `di` 154 → 0. See `evals/android/eval-14-di/RESULTS.md`.
