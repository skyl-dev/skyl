---
name: android/xml
axis: framework
family: android
description: "The View system: layouts, adapters, RecyclerView, ViewBinding, and the seam where a ComposeView sits inside a View hierarchy. Use when the UI is XML layouts."
requires: [android/core]
version: 1.0.1
authors: [ahmmedrejowan]
agent_sections: [rules]
retired: [HOST-3]
detect:
  file: ["**/src/main/res/layout/*.xml"]
  gradle_property: ["android.buildFeatures.viewBinding", "android.buildFeatures.dataBinding"]
  gradle_dependency: ["androidx.recyclerview:recyclerview", "com.google.android.material:material"]
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

## Why

<!-- human-only: not installed -->

**Why the Compose seam is the first section.** Most View codebases are not being maintained so much
as slowly replaced, one screen at a time. That means the highest-frequency new code in an XML app is
a `ComposeView` inside a layout, and it is the place with the most silent failures, because a
`ComposeView` inherits nothing. Not the theme, not a sensible disposal point, not saved state. Three
defaults are wrong for the two places it is most often used, and none of them fail loudly.

The disposal one deserves the detail, and it is also where most published advice is now out of date.
The default disposes when the window detaches, and a Fragment's view is destroyed long before its
window is, so a `ComposeView` in a Fragment on the back stack keeps a live composition holding a
dead view. That leak is real, it does not throw, and it grows with navigation depth.

The pooled case used to be the same story and no longer is. `ViewCompositionStrategy.Default` is
`DisposeOnDetachedFromWindowOrReleasedFromPool`, which disposes a `RecyclerView` row when the
container detaches or the pool discards it. Most of what is written about `ComposeView` in a
`RecyclerView` predates that and tells you to set explicitly what is already the default.

**Why `bindingAdapterPosition` and not the captured item.** An adapter position is a fact about a
moment. Between `submitList` and the layout pass that follows it, the list has changed and the
holders have not been rebound, so a click in that window carries a stale position. Capturing the
item at bind time feels safer and is worse: the position at least fails visibly with `NO_POSITION`
while the captured item silently acts on the wrong row. A delete that removes the wrong item reads
as a backend bug for as long as it takes someone to reproduce it.

**Why the scroll position resets.** A `RecyclerView` restores its saved scroll position as soon as
it has an adapter with content. If the first thing it receives is an empty list, which is what
happens when data arrives asynchronously, it restores against zero items and gives up. The user
lands at the top of a list they had scrolled halfway down, and it happens on rotation *and* on
process death, which is why it survives testing on a fast device.

**Why two owners of one value is worse than none.** `android:saveEnabled` defaults to true, so a
`TextInputEditText` bound to a state holder saves its own copy into the same bundle the holder is
using. Both restore. Whichever wins is an implementation detail of restore order. It survives
exactly one rotation before diverging, and the divergence looks like the state holder is wrong
which is where everyone looks first.

**What changed, if you learned this earlier.**| Then | Now |
|---|---|
| `findViewById` | view binding |
| data binding expressions in XML | view binding, logic in code |
| `notifyDataSetChanged` | `ListAdapter` and `DiffUtil` |
| `adapterPosition` | `bindingAdapterPosition`, checked |
| nested `LinearLayout` with weights | `ConstraintLayout`, one measure pass |
| `ListView` | `RecyclerView` |
| a rewrite to Compose | a `ComposeView` per screen, coexisting |

## Pitfalls

<!-- human-only: not installed -->

- **Memory that grows with navigation depth.** A `ComposeView` with the default disposal strategy in
 a Fragment.
- **One screen rendering with the wrong colours.** `setContent` without the app theme wrapper.
- **Only the Compose part of a screen resets on rotation.** `remember` where `rememberSaveable` was
 needed, `compose REM-1`. It is more visible here than in a pure Compose screen, because the
 surrounding View state survived and the island did not.
- **A delete that removes the wrong item.** A captured item, or `adapterPosition` after a submission.
- **The list jumps to the top after rotation.** No `PREVENT_WHEN_EMPTY`, restoring against an empty
 list.
- **A field that reverts to an older value after one rotation, then behaves.** Two owners saving into
 the same bundle.
- **A toggle that flickers the row's image on every tap.** Full rebind where a payload was needed.
- **A scroll that stutters only on some screens.** An allocation inside a `CoordinatorLayout.Behavior`
 callback.
- **A build failure naming the resource system rather than your file.** An uppercase letter or a
 hyphen in a resource file name.

## Provenance

<!-- human-only: outside agent_sections, never installed -->

**Eval 12 measured this skill and four rules separated.** `LIST-2` and `LIST-4` went 0/2 to 2/2 on
**both** models, eight runs moving the same way. `LIST-3` separated on Haiku and is already
satisfied by Sonnet; `STATE-1` separated on Sonnet and landed nowhere on Haiku. `HOST-1` separated
on Haiku and is inert on Sonnet.

**Those four are exactly the four with zero corpus support.** The corpus-backed rules in this same
file, `LIST-1` (`ListAdapter`/`DiffUtil`) and `HOST-2` (the theme wrapper), are satisfied by every
arm including the controls. Within one skill, the measurement-sourced rules were the entire effect
and the corpus-sourced ones were inert.

The `ViewCompositionStrategy` correction also held up in behaviour: **not one of the 12 task-B runs** set the pooling
strategy on a non-pooled Fragment header, treated arms included. See `evals/android/eval-12-xml/RESULTS.md`.

`LIST-2`, `LIST-3`, `LIST-4` and `STATE-1` come from a measured predecessor. In a rebuild of this
skill after its first version lost 4–1 to `core` alone, three unaided implementations of a
search-and-list screen were scored: `LIST-4` separated (1 of 3 controls did it), and the other three
scored 2 of 3, not a separation at that n, and kept on argument. That work is in
`trash/experiments/android/xml/`.

Those four rules have **zero support anywhere in the 3,845-file corpus**. They were found by running
a control arm, not by reading, and they are the clearest example in the project of the difference, see `registers/android/framework/xml/VS-V0.3.0.md`.

Everything else here is corpus-evidenced and unmeasured. The `HOST-*` cluster is the strongest
signal in the folder: five claims across four independent repos, every one of them with a leak as
the stated symptom.

**Corrected later:** `HOST-1` after a web pass. It claimed the default `ViewCompositionStrategy` was
wrong in *two* places, a Fragment and a pooled `RecyclerView` row. Only the Fragment case is real:
`ViewCompositionStrategy.Default` **is** `DisposeOnDetachedFromWindowOrReleasedFromPool` and already
disposes pooled rows. The corpus cluster that led this file, five claims, four repos, every one
citing a leak, is half stale, and I had carried the stale half through. See
`registers/android/REVERSALS.md`.

Also checked and **not** changed: Data Binding is not deprecated. A codelab carries a banner, the
library does not, so `BIND-1` stays a `should`.

`HOST-3` was drafted and cut before shipping: "a `ComposeView`'s state uses `rememberSaveable`" is
`compose REM-1` restated with a narrower subject. The layering check caught it. The
hosting-specific symptom, the Compose island resetting while the surrounding View state survives, is kept in Pitfalls, which is where a manifestation belongs rather than a duplicate rule.

The axis is genuinely thin. 106 of 370 extracted rows proposed out to `compose`, and 9 of 16 repos
in the folder are migration skills, the corpus contains an XML-exit body of knowledge more than an
XML-craft one, which is why the Compose seam leads this file rather than trailing it.
