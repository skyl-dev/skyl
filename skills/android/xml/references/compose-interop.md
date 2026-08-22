# Hosting Compose in a View hierarchy

Referenced by `xml HOST-1`, `HOST-2` and `HOST-4`.

A `ComposeView` inherits nothing from the layout around it. Not the theme, not a disposal point
not a lifecycle. Every default it ships with is chosen for the simplest case, a `ComposeView` in an
Activity's content view, and that is not where most of them end up.

## Disposal: one case needs you, and it is not the one most articles name

| Where the `ComposeView` is | Strategy |
|---|---|
| an Activity's content view | the default |
| **a Fragment's view** | **`DisposeOnViewTreeLifecycleDestroyed`** you must set this |
| a `RecyclerView` row | the default already handles it |
| a View whose lifecycle is unknown at construction | `DisposeOnViewTreeLifecycleDestroyed` |

`ViewCompositionStrategy.Default` is `DisposeOnDetachedFromWindowOrReleasedFromPool`: it disposes on
window detach, and inside a pooling container it disposes when the container detaches or the pool
discards the item.

    composeView.setViewCompositionStrategy(
        ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed
    )

**Why the Fragment case leaks.** A Fragment's *view* is destroyed when it goes on the back stack;
its *window* is not. The default strategy waits for the window, so the composition survives the view
it was drawing, holding it and everything it references. Memory grows with navigation depth and
nothing throws.

**Why the RecyclerView case no longer needs you.** It used to: the older default disposed only on
window detach, so a recycled holder kept its previous composition. The default changed to handle
pooling, and most published advice, including the claims in our own corpus, predates it and still
tells you to set `DisposeOnDetachedFromWindowOrReleasedFromPool` explicitly. That is now a no-op.

## Theme: nothing is inherited

    composeView.setContent {
        AppTheme {          // without this, default Material colours and typography
            OrderRow(order)
        }
    }

The XML around it carries an Android theme; Compose reads a Compose theme, and there is no bridge.
An unwrapped island renders in default Material beside views that do not, which reads as one screen
being broken rather than one line being absent.

## Migrating a screen: take the view references with it

When a screen becomes Compose, the `lateinit` binding and any view fields go. They cannot survive
the migration, and the failure is a null dereference at whatever still touches them, usually a
lifecycle callback nobody edited.

A half-migrated screen holding both is the shape that crashes. Either the screen is Compose and the
view references are gone, or it is hybrid and both halves are deliberately live.

## Migrate incrementally

Views and Compose coexist by design. One screen per pull request, reviewable on its own. A rewrite
of the whole app is a project that has to be funded and finished before anything ships, and that is
rarely how it goes, the incremental path is the one that survives a change of priorities.
