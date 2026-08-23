---
name: android-testing
description: "What makes a test able to fail for the right reason: the shape of the seam, the scheduler it runs on, and what an assertion is allowed to know. Use when writing tests, or changing code to make one possible."
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
