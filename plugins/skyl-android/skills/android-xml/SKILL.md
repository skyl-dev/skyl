---
name: android-xml
description: "The View system: layouts, adapters, RecyclerView, ViewBinding, and the seam where a ComposeView sits inside a View hierarchy. Use when the UI is XML layouts."
---

## Rules

The View system, in the codebase you have: an app built on layouts and `RecyclerView`, usually with
Compose arriving screen by screen. `core` owns the architecture. `compose` owns Compose itself. This
owns layouts, adapters, and the seam where a `ComposeView` sits inside a View hierarchy.

**When a rule here conflicts with the code you are editing** the surrounding convention wins for
style and structure, but never for a rule whose failure loses user data, leaks a credential, or
ships a crash. Fix those in their own change, not inside another one.

**Scope.** New screens and new adapters in an existing View codebase, and the boundary where Compose
is introduced. A new app should be Compose.

**When not to apply**(whole-skill): a greenfield app. Use Compose.

**Priority.** `must`, the failure leaks, crashes, or loses state. `should`, real exceptions exist;
name yours.

### Hosting Compose in a View hierarchy

- **HOST-1** `must`: A `ComposeView` in a Fragment's view sets
 `ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed`.
 *Why:* a Fragment's view is destroyed long before its window is. The default disposes on window
 detach, so a Fragment on the back stack keeps a live composition holding a dead view, memory that
 grows with navigation depth, and nothing throws. The same applies wherever the lifecycle is not
 known at construction.
 *Not when:* an Activity's content view, or a pooled container. ** The default already handles
 pooling** `ViewCompositionStrategy.Default` is
 `DisposeOnDetachedFromWindowOrReleasedFromPool`, which disposes a `RecyclerView` row when the
 container detaches or the pool discards it. Setting it explicitly there is a no-op.

- **HOST-2** `must`: Content inside `setContent` is wrapped in the app's Compose theme.
 *Why:* a `ComposeView` inherits nothing from the surrounding XML theme. Without the wrapper the
 island renders with default Material colours and typography beside views that do not, and it looks
 like a bug in one screen rather than a missing line.
 *Not when:* the app has no Compose theme yet, and then that is the thing to add.

- **HOST-4** `must`: When a screen moves to Compose, its view references go with it. No `lateinit`
 binding or view field left behind.
 *Why:* they cannot survive the migration and they will be null at the moment something still
 touches them. A half-migrated screen holding both is the shape that crashes.
 *Not when:* the screen is deliberately hybrid and both halves are live.

### Lists

- **LIST-1** `must`: `RecyclerView` with `ListAdapter` and a `DiffUtil.ItemCallback`.
 `notifyDataSetChanged` rebinds every visible holder and disables item animations.
 *Why:* `ListAdapter` wraps `AsyncListDiffer`, so the diff runs off the main thread and the
 animations are correct for free. The manual alternative is correct until the first insertion.
 *Not when:* a short static list that never changes.

- **LIST-2** `must`: A `ViewHolder` reads its item through `bindingAdapterPosition`, checked against
 `NO_POSITION`, never a captured item, never `adapterPosition`.
 *Why:* a click that lands between a list submission and its layout pass acts on the row that used
 to be there. The captured version is worse: it deletes the wrong item and looks like a backend bug.
 *Not when:* never in a click handler.

- **LIST-3** `should`: When only part of a row changes, `getChangePayload` returns a payload and the
 partial `onBindViewHolder` updates just that view.
 *Why:* a full rebind re-issues the row's image request, which is a visible flicker on every toggle.
 *Not when:* the row is cheap and holds no image.

- **LIST-4** `should`: A `RecyclerView` whose content arrives asynchronously sets
 `stateRestorationPolicy = PREVENT_WHEN_EMPTY`.
 *Why:* otherwise the layout manager restores scroll position against the empty list it was given
 first, and the user lands at the top of a list they had scrolled halfway down. Both rotation and
 process death hit it. *Not when:* the first submission is synchronous.

### View state

- **STATE-1** `must`: A field whose value the state holder already owns sets
 `android:saveEnabled="false"`.
 *Why:* otherwise the view saves its own copy into the same bundle as the holder's, and the two
 restore independently. It survives exactly one rotation before diverging, and the bug reads as
 the state holder being wrong. *Not when:* the view is the only owner of that value.

- **STATE-2** `must`: Every view whose state must survive recreation has a unique `android:id`.
 *Why:* `dispatchSaveInstanceState` silently skips id-less views, and duplicate ids overwrite each
 other in one shared array. Nothing reports either. *Not when:* a purely decorative view.

### Layout

- **LAYOUT-1** `should`: Reduce hierarchy depth before anything else. `<merge>` as the root of an
 included layout, `ConstraintLayout` for complex screens, a compound drawable instead of an
 `ImageView` beside a `TextView`.
 *Why:* every widget pays init, measure, layout and draw, and nesting multiplies it, nested weights
 measure their children twice per pass. Depth is the first-order cost and the one worth fixing;
 `ConstraintLayout` resolves a flat screen in a single measurement pass.
 *Not when:* a shallow layout, where `LinearLayout` is easier to read and costs nothing.

- **LAYOUT-2** `must`: A `CoordinatorLayout.Behavior` callback allocates nothing.
 *Why:* it is dispatched to every dependent child on every scroll frame. An allocation there is an
 allocation per frame per child. *Not when:* never.

### Binding and resources

- **BIND-1** `should`: Use view binding. `findViewById` is neither type-checked nor null-checked
 and data binding puts logic in XML where review and refactoring tools cannot see it, at the cost
 of an annotation processor on every build.
 *Why:* view binding kept the generated-accessor half and dropped the expression half, which is why
 it became the default. *Not when:* a codebase already committed to data binding, see `BIND-2`.

- **BIND-2** `must`: A `BindingAdapter` must be able to undo itself. Binding `false` reverses what
 binding `true` did.
 *Why:* the adapter is called on every bind, including with the value that turns the effect off. An
 early return on anything but `true` leaves the previous row's effect applied to a recycled view.
 *Not when:* the attribute is genuinely write-once.

- **RES-1** `must`: Resource file names use lowercase letters, digits and underscores only, and
 files live in the predefined type directory for their kind.
 *Why:* both are compile failures rather than warnings, and the message names the resource system
 rather than the file you added. *Not when:* never.
