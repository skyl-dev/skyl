---
name: android-mvvm
description: "The shape of the layer graph: which layers exist, which way dependencies point, and what each one may touch. Use when the app has a ViewModel layer."
---

## Rules

Where things go and what may reach what. `android/core` owns what state *is* what survives
process death, what the UI may claim, where a value is formatted. This owns the ** shape of the
graph**: which layers exist, which way they point, and what each one is allowed to touch.

The failure this prevents is not a wrong line of code. It is a screen that works, ships, and cannot
be tested, reused, or changed without touching four files.

**Scope.** New code, and new features in an existing structure. Match the layering already in the
module you are editing, a codebase with one consistent wrong shape is better than two right ones.

**When a rule here conflicts with the code you are editing** the surrounding convention wins for
style and structure, but never for a rule whose failure loses user data, leaks a credential, or
ships a crash. Fix those in their own change, not inside another one.

**When not to apply**(whole-skill): a single screen with no remote data and no persistence. A
prototype. A sample.

**Priority.** `must`, the failure is structural and expensive to undo. `should`, real exceptions
exist; name yours.

### What core already owns

`core` states the layering itself and this file does not repeat it: dependencies point one way
(`BOUND-1`), each layer's public surface uses types it owns (`BOUND-2`), and a layer is added when
a second consumer appears rather than at the first screen (`BOUND-3`).

What follows is what those rules do not say: where the ViewModel sits, what it may touch, and how
the repository and its sources are arranged.

### The ViewModel

- **VM-2** `must`: The ViewModel holds no Android framework object: no `Context`, `Activity`
 `Fragment`, `View`, `Resources`, `Uri` resolution, or navigation controller.
 *Why:* it outlives all of them, so holding one leaks it, and needing one is almost always a sign
 that a decision belongs in the UI or a string belongs in a resource.
 *Not when:* the application context, injected, for something that genuinely has no other home.

- **VM-3** `must`: The ViewModel decides *what* should happen; the UI decides *how* it looks.
 Navigation, dialogs, toasts and formatting are UI concerns triggered by state, not performed by
 the ViewModel. *Why:* a ViewModel that navigates cannot be tested without a nav host, and a
 ViewModel that formats has frozen a locale. *Not when:* never, but "the UI decides how" includes
 choosing which string resource a state maps to.

- **VM-4** `should`: One ViewModel per screen, scoped to that screen. Share one across screens only
 when they are genuinely one flow over one piece of state, a wizard, a multi-step form.
 *Why:* a ViewModel shared for convenience becomes a place to put anything, and its lifetime stops
 matching anything on screen. *Not when:* the flow really is one, and then scope it to the
 navigation graph, not to the activity.

### The repository

- **REPO-1** `must`: The repository is the only thing that knows where data comes from. It owns
 the choice between network, cache and database, and callers cannot tell which answered.
 *Why:* this is the single decision that makes offline support, caching and retry changeable in
 one place. A ViewModel that calls the API when online and the DAO when offline has taken that
 decision and spread it across every screen.
 *Not when:* there is exactly one source and no caching, then the repository is a thin pass-through
 and should be honest about it rather than growing ceremony.

- **REPO-2** `must`: The repository exposes domain types and domain failures. SDK exceptions, HTTP
 status codes and SQL errors stop there.
 *Why:* a status code reaching a ViewModel means the UI is deciding what 409 means. *Not when:*
 never for errors that reach the user.

- **REPO-3** `should`: Data sources are separate from the repository: one per origin, remote
 local, in-memory. The repository coordinates them and contains no I/O of its own.
 *Why:* it is what lets you fake one source in a test while the other stays real, and it keeps the
 caching decision readable in one place rather than interleaved with parsing.
 *Not when:* a single source, where the split is two files pretending to be a design.

- **REPO-4** `must`: A repository interface is defined where it is *used* not where it is
 implemented, and the ViewModel depends on the interface.
 *Why:* this is the difference between a layered app and a layered folder structure. If the
 interface lives beside the implementation, the UI still depends on the data layer and the arrow in
 `core BOUND-1` is decorative. *Not when:* no test and no second implementation is plausible, say
 so. **Or the codebase already declares its interfaces beside their implementations** moving one
 interface across a module boundary is a change that reaches every call site, and it does not
 belong inside a feature. Write the new one correctly; move the old ones deliberately.
