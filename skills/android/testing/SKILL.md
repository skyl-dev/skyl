---
name: android/testing
axis: topic
family: android
requires: [android/core]
version: 1.0.0
authors: [ahmmedrejowan]
agent_sections: [rules]
retired: [REACH-1, TIME-1, STATE-1, STREAM-1]
detect:
 gradle_dependency:
 - "org.jetbrains.kotlinx:kotlinx-coroutines-test"
 - "app.cash.turbine:turbine"
 - "org.robolectric:robolectric"
 - "androidx.compose.ui:ui-test-junit4"
 - "androidx.test.espresso:espresso-core"
---

## Rules

What makes a test able to fail for the right reason. `core` owns what the production code does.
`di` owns how a binding is replaced through a container. This owns the seam a test needs and the
scheduler it runs on.

**Three rules, not thirty.** Almost everything written about testing, prefer fakes to mocks, cover
the error path, never sleep, name the test after the behaviour, is already what these models do.
What is left is the part nobody writes down.

**Scope.** New tests, and production code you are changing to make a test possible.

**When not to apply**(whole-skill): a spike you will delete.

**Priority.** `must`, the failure is a flake, or a test that cannot fail. `should`, real
exceptions exist; name yours.

- **SEAM-1** `must`: Anything a test must control is a ** constructor parameter with a production
 default**: a clock, a dispatcher, a collaborator, a source of randomness. Never open a mutable
 field for tests, never widen visibility to reach one, never statically mock a platform type.
 *Why:* the seam is not the hard part, a class that reads the wall clock or names a global
 dispatcher is untestable and everyone can see it. The trap is the shape of the fix. A mutable
 `internal var` that a test reassigns is production state that any code can now change, it leaks
 between tests in the same process because nothing resets it, and it makes the class's real
 dependencies invisible in its signature. A static mock of a platform type is worse: it changes
 behaviour for code that never asked, for as long as the mock is installed. A parameter with a
 default costs nothing at every existing call site and is the entire difference.
 *Not when:* the class genuinely has no such dependency, a pure function needs no seam at all.

- **SCHED-1** `must`: One scheduler per test. Replace the main dispatcher **first** then create
 every other test dispatcher, they inherit its scheduler automatically. Never construct one
 before, and never pass a second one in.
 *Why:* this is the failure that looks like the framework being broken. Advancing time does nothing
 to work queued on a *different* scheduler, so the code under test never runs, the assertion reads
 untouched initial state, and no error message says why. The ordering is the whole rule: a test
 dispatcher created after the main replacement picks up its scheduler; one created before gets its
 own. The default test dispatcher also queues rather than running eagerly, which is why the symptom
 is a wrong assertion rather than a hang.
 *Not when:* nothing under test dispatches, and then none of this applies.

- **KNOW-1** `should`: Assert on what the caller can observe, not on how it was produced. Not call
 counts, not ordering between collaborators, not a `toString`.
 *Why:* asserting on the mechanism makes the test a copy of the implementation, so it can only ever
 agree with it, it cannot catch a wrong result, and it fails on a correct refactor. That is the
 inverse of what a test is for, and it is what teaches a team to delete tests rather than read them.
 *Not when:* the interaction *is* the requirement, that a payment is charged once, that a
 destructive call is never made, where the count is the behaviour.

## Why

<!-- human-only: not installed -->

**Why this skill is three rules.** The register behind it held 238 distinct testing claims, the
largest pool of any axis, and almost none of it survived. Not because the claims are wrong, most are
correct, but because they describe what these models already do. Across 24 runs there was not a
single `Thread.sleep`, not a single unbounded stream collected to a list, not one mock where a fake
belonged, and `runTest` in every arm including every control. Writing those down would have cost
tokens and displaced the rules that work.

**Why the seam's shape is the whole finding.** Every run understood that a 24-hour expiry cannot be
tested against the system clock. Twelve of twelve built a seam. What separated was what they built:
a mutable `internal var` the test reassigns, versus a constructor parameter. One control wrote the
problem out in its own comment, *"Overridable in tests via friend-module access"* which is a
production field that exists because of a test, documented as such, and shipped.

That shape is the difference between a dependency and a back door. A parameter states what the class
needs, cannot be changed by anything else, and cannot leak into the next test. A mutable field states
nothing, can be changed by anything, and is reset only if someone remembers.

**Why the dispatcher rule failed and the clock rule worked.** They are the same rule. The draft
stated the clock case as a principle and the dispatcher case as a separate instruction three
sections away, and the dispatcher one landed in zero runs of twenty-four while the clock one moved
cleanly. The model built a seam for the clock and never connected it to `Dispatchers.IO` sitting in
the same file. ** A principle stated once travels; the same principle stated twice as two instances
does not.**## Pitfalls

<!-- human-only: not installed -->

- **A test passes alone and fails in the suite.** Shared mutable state that nothing resets, often a
 seam that was opened rather than passed.
- **An assertion reads the initial state and nothing explains why.** Two schedulers: a test
 dispatcher created before the main dispatcher was replaced.
- **A test that fails on every refactor and has never caught a bug.** It asserts on the mechanism.
- **A production field whose only caller is a test.** The seam has the wrong shape.
- **A platform type behaving strangely in an unrelated test.** A static mock still installed.

## Provenance

<!-- human-only: outside agent_sections, never installed -->

**Eval 21, 24 runs, Haiku 4.5 and Sonnet 5.** `SEAM-1` is the measured rule: on Sonnet, a clock
supplied as a parameter went **0/2 → 2/2** and a clock as a mutable production field went
**2/2 → 0/2** both directions on the same rule. Haiku moved 1/2 on each, which is noise.

**Nine rules became three, and the cuts are the evidence.** Retired as satisfied unaided: no real
waiting (0 violations in 12), never collecting an unbounded stream (0 in 12), fakes over mocks
(12/12), resetting process-wide state (10/12, no arm pattern). Every one of those was predicted as
corpus-saturated before the run and every one was.

`TIME-3` (inject the dispatcher) landed in **0 of 12** runs, every arm, and it is the same rule as
`SEAM-1`, stated as a separate instance under a different heading. It is now folded in rather than
kept, which is the actionable form of the finding.

`SCHED-1` and `KNOW-1` are **unmeasured**: `setMain` was noisy on Haiku and already universal on
Sonnet, and neither task tempted an assertion on mechanism.

**Eleventh detector error.** The visibility column read `Y` in all 12 runs including controls
because its regex matched a field that is `private` *in the unmodified seed*. Running the detector
against the seed itself is now the first check in `method/METHOD.md`.
