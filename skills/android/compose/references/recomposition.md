# Recomposition

Referenced by `compose SKIP-1`, `SKIP-2` and `REM-2`.

## The three phases

Compose does its work in three passes, and every state read is an input to exactly one of them:

| Phase | Produces | A change here re-runs |
|---|---|---|
| **Composition** | what to show | the composable function, and its children |
| **Layout** | where it goes | measure and place |
| **Draw** | pixels | the draw commands |

The cost falls by roughly an order of magnitude at each step. **Which phase a value is read in is
usually a bigger lever than anything else you can do** and it is decided by *where* you read it
not by what it is.

    // read in composition, a change re-runs the whole function
    Box(Modifier.offset(x = scrollOffset.dp))

    // read in layout, a change re-runs placement only
    Box(Modifier.offset { IntOffset(scrollOffset.roundToInt(), 0) })

For a value that changes every frame, that is the difference between recomposing a screen at 60fps
and moving a rectangle.

`graphicsLayer { }` pushes the read all the way to draw and is the right tool for alpha, scale
rotation and translation.

## Skipping, and why it stops working

Compose skips a composable when it can prove every parameter is unchanged. "Prove" is the operative
word, the compiler needs a type it can reason about.

**Stable:** primitives, `String`, function types, and any class whose public properties are all
`val` of stable types.

**Unstable, and the ones that bite:**

- `List`, `Set`, `Map`, interfaces, so the instance behind them may be a mutable implementation
  someone else still holds
- any class with a `var` property
- classes from a module that is not compiled with the Compose compiler

The fix is a type change, not a cache. `kotlinx.collections.immutable` (`ImmutableList`
`persistentListOf`) gives the compiler what it needs. `@Immutable` and `@Stable` are promises you
make on the compiler's behalf, correct only if the object genuinely never changes after
construction, and a lie the runtime cannot detect if it does.

## Why unskippable propagates

An unskippable composable recomposes, which re-invokes its children, which may themselves be
skippable but are now being called with fresh arguments. One unstable parameter near the top of a
screen can therefore recompose the entire subtree beneath it. This is why a single `List` parameter
shows up as "the whole list flashes when one row changes".

## `derivedStateOf`

Use it when a value is computed from state that changes **more often** than the result does:

    val showButton by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }

`firstVisibleItemIndex` changes constantly while scrolling; the boolean changes twice. Without
`derivedStateOf`, everything reading the boolean recomposes at scroll frequency.

It is not free, it allocates and adds a layer of observation. If the input changes no more often
than the output, it is pure overhead. The test is the *ratio* of change frequencies, not whether a
calculation is involved.

## Measuring rather than guessing

Do not optimise a path you have not observed.

- **Layout Inspector** → *Recomposition counts*. The column to watch is "skipped", a composable
  recomposing far more often than its data changes is the signal.
- **Composition tracing** in Android Studio's profiler attributes frame time to individual
  composables.
- **Always measure a release build** with R8 enabled. Debug Compose is dramatically slower and will
  send you after the wrong thing.
- **Baseline Profiles** address first-run cost specifically, which is a different problem from
  recomposition and is not fixed by any of the above.

## A shortlist for a janky screen

1. Is it a release build? If not, start there.
2. Recomposition counts, which composable is recomposing more than its data changes?
3. Is a parameter unstable? Fix the type before anything else.
4. Is an animating or scroll-linked value read in a composable body? Move it into a lambda modifier.
5. Is work proportional to the data happening inside a composable? Move it out.
6. Only now consider `derivedStateOf`, and only where the change ratio justifies it.
