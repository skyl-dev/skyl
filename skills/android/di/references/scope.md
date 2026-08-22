# Scope

Referenced by `di SCOPE-1`, `SCOPE-2` and `SCOPE-3`.

## Scope is a lifetime

A scope annotation answers one question: **how long does this instance live?** It is not a
performance setting, and treating it as one is where most DI mistakes start.

| Lifetime | Use it for | Not for |
|---|---|---|
| unscoped | anything cheap and stateless, mappers, formatters, use cases | anything holding shared state |
| application | caches, connection pools, clients, a database | anything holding a screen |
| screen / retained | state one screen owns and must survive rotation | anything the app needs elsewhere |
| custom | a real domain lifetime, a session, a checkout | a lifetime you invented for one class |

The test for adding a scope: **would two instances of this be wrong?** If two are harmless, it does
not need one. A `QueryParser` with no fields can exist a thousand times over and nothing notices. A
cache cannot.

## Two things scope silently does

**It keeps objects alive.** A scoped object is unreachable for collection until its component dies.
Scope everything and the graph becomes a set of permanent objects, most of which nobody is using.

**It leaks between tests.** A scoped fake installed for one test is the *same instance* the next test
receives, so a test that mutates it changes a test that did not ask. This is the failure that
presents as "passes alone, fails in the suite", and it is genuinely hard to find because the failing
test is not the one at fault.

## Direction: only depend on something that outlives you

    application-scoped  ──may depend on──▶  application-scoped, unscoped
    screen-scoped       ──may depend on──▶  application-scoped, unscoped
    unscoped            ──may depend on──▶  anything it is constructed alongside

    application-scoped  ──MUST NOT──▶  screen-scoped, an Activity, a Fragment, a ViewModel

Point it the wrong way and there are only two outcomes: the long-lived object keeps the short-lived
one alive, an `Activity` and its entire view tree, held for the life of the process, growing with
every rotation, or it holds something already destroyed.

Where a long-lived object needs a `Context`, that is the **application** context, which is not a
screen and cannot leak one.

This failure has three entrances in this skill set, and they are worth knowing together:

| Where | Rule |
|---|---|
| a `static` field or a Java singleton | `java LEAK-2` |
| a `ViewModel` | `mvvm VM-2` |
| the object graph | `di SCOPE-2` |

## Custom scopes

Most apps have three lifetimes that matter: the process, the screen, and the thing currently on
screen. A custom scope is worth defining when a real one exists that none of those match, a
logged-in session that spans screens and ends at sign-out, a checkout flow that must be abandoned
whole.

It is not worth defining because a class felt like it deserved its own. Every custom scope is a
lifetime that every future reader has to hold in their head at each injection site.
