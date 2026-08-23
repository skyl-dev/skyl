---
name: android/compose
axis: framework
family: android
requires: [android/core]
version: 1.0.0
authors: [ahmmedrejowan]
agent_sections: [rules]
retired: [INTEROP-1, INTEROP-3]
detect:
  gradle_dependency:
    - "androidx.compose.ui:ui"
    - "androidx.compose.runtime:runtime"
    - "androidx.compose.foundation:foundation"
    - "androidx.compose.material3:material3"
    - "androidx.compose.material:material"
    - "androidx.compose:compose-bom"
    - "androidx.activity:activity-compose"
  gradle_plugin: ["org.jetbrains.kotlin.plugin.compose"]
---

## Rules

Compose mechanics. `android/core` owns the decision, where state lives, what survives process
death, what the UI may claim. This says how Compose expresses it, and only where Compose expresses
it in a way that goes wrong. `android/xml` owns the other side of the seam, a `ComposeView` hosted
in a View hierarchy; this owns a View hosted inside Compose.

A composable is a function that may run on any frame, more than once per frame, in any order, and
be skipped entirely. Almost every rule here follows from that one sentence.

**Scope.** New code. Match the file you are editing.

**When not to apply**(whole-skill): a preview-only or sample screen you will delete.
Never raise these on code you are not otherwise changing.

**Priority.** `must`, the failure is silent, visual, or expensive. `should`, real exceptions
exist; name yours.

### Effects

- **EFFECT-1** `must`: Anything that is not producing UI goes in an effect, never in the composable
 body. Launching work, subscribing, logging, navigating, showing a snackbar.
 *Why:* the body runs on recomposition, which happens on any frame and can be skipped. Work started
 there runs an unpredictable number of times, usually once in a preview, several times on a real
 screen, and the duplicate network call is the visible half.
 *Not when:* deriving a value from parameters, which is exactly what the body is for.

- **EFFECT-2** `must`: An effect's keys are the values it must restart for. `LaunchedEffect(Unit)`
 means "once for the lifetime of this composition, whatever changes around it".
 *Why:* keys are the whole API. Too few and the effect keeps running against a stale value, an
 observer still watching the previous id. Too many and it cancels and restarts on every
 recomposition, which for a network call means a request per frame.
 *Not when:* the effect genuinely should run once, then `Unit` is correct and deliberate.

- **EFFECT-3** `must`: A value a long-running effect must see, but must not restart for, is wrapped
 in `rememberUpdatedState`.
 *Why:* this is the escape from EFFECT-2's dilemma. A timeout that fires a callback should not
 restart when the callback identity changes, but must call the current one, capturing the lambda
 directly calls the version from when the effect started.
 *Not when:* the effect should restart. Then it is a key.

- **EFFECT-4** `must`: Anything registered is unregistered in the matching `DisposableEffect`
 `onDispose`. Listeners, observers, callbacks, receivers.
 *Why:* a composable leaves the composition without warning, a conditional branch, a list scroll
 a navigation. Nothing else runs your cleanup.
 *Not when:* the subscription is a `Flow` collected by `collectAsStateWithLifecycle`, which
 disposes itself.

### Remembering

- **REM-1** `must`: A value that must outlive a recomposition is `remember`ed; a value that must
 outlive activity recreation is `rememberSaveable`.
 *Why:* an un-remembered value is recreated on every recomposition, so anything derived from it, a scroll position, an animation, a generated id, resets at random moments. The two are different
 guarantees and the wrong one fails in a different situation.
 *Not when:* the value is cheap and genuinely derived from parameters every time.

- **REM-2** `should`: A value computed from state that changes more often than the result is
 wrapped in `derivedStateOf`.
 *Why:* `firstVisibleItemIndex > 0` changes on every scrolled pixel; the boolean changes twice.
 Without `derivedStateOf` every reader recomposes at scroll frequency.
 *Not when:* the input changes no more often than the output, then it is overhead and an extra
 object.

### Recomposition

- **SKIP-1** `should`: A composable can only be skipped if its parameters are stable. Prefer
 immutable types; where an unstable type must cross the boundary, mark it or wrap it.
 *Why:* `List` is an interface, so the compiler cannot know the instance is not mutated in place
 and treats the composable as never skippable. One changed row then recomposes every visible row.
 *Not when:* the composable is cheap and runs rarely, stability annotations are not free to read.

- **SKIP-2** `should`: State read inside a lambda-based modifier is read in layout or draw, not in
 composition. Prefer `Modifier.offset { }` and `graphicsLayer { }` for values that change every
 frame.
 *Why:* reading an animating value in the composable body recomposes the whole function on every
 frame. Reading it inside the lambda re-runs only layout or draw.
 *Not when:* the value changes rarely, the lambda form is harder to read for no gain.

- **SKIP-3** `must`: Work proportional to the data, filtering, sorting, mapping, happens before
 the composable, not inside it.
 *Why:* the body can run on any frame. A sort in a composable is a sort per frame.
 *Not when:* the collection is small and fixed, and the alternative is plumbing that obscures the
 screen.

### Lists

- **LAZY-1** `must`: `items(...)` passes a stable `key`. Where the list holds more than one row
 shape, it also passes `contentType`.
 *Why:* without a key, removing a row re-binds every row after it and per-row state follows the
 wrong item. Without `contentType`, a scrolled-off row's composition cannot be reused for a row of
 the same shape, so every recycle re-runs the whole subtree.
 *Not when:* a short static list that never reorders.

### Text input

- **TEXT-1** `must`: A text field the user types into holds its own `TextFieldState`. Observe it
 with `snapshotFlow { state.text }` where a pipeline needs the text.
 *Why:* this is `core STATE-4` in Compose. Routing keystrokes out to a state holder and back
 reorders and drops characters under fast input, and breaks composition on predictive, CJK, Indic
 and gesture keyboards.
 *Not when:* the field is read-only, or its content is fully controlled elsewhere, a filter chip
 rendered as a field.

### Structure

- **MOD-1** `must`: A composable that draws anything takes `modifier: Modifier = Modifier` as its
 first optional parameter, applies it to its outermost element, and applies it exactly once.
 *Why:* the caller owns layout. A composable that does not forward the modifier cannot be padded
 sized or clicked by its parent, and one that applies it twice applies padding and click handling
 twice.
 *Not when:* the composable draws nothing, a pure state-holder composable.

- **THEME-1** `should`: Colour, typography and shape come from `MaterialTheme`, not from literals.
 *Why:* a literal colour is the one that stays light when the app goes dark, and the one that does
 not follow a theme change. *Not when:* a genuinely fixed brand value that must not adapt, and
 then it belongs in the theme as a named token, not inline.

### Hosting a View

- **INTEROP-2** `must`: A View hosted in `AndroidView` is given the host's lifecycle. Forward
 `ON_RESUME` and `ON_PAUSE` to it, not just creation and disposal.
 *Why:* leaving composition and being backgrounded are different events, and only the first one
 Compose tells you about. A `MapView`, a `VideoView`, a camera preview or anything holding a
 renderer or a location listener keeps working while the user is in another app, draining battery
 and holding a surface, because nothing paused it. Creation and destruction are the pair people
 remember; resume and pause are the pair that only fails once the app has been backgrounded, which
 is not a thing anyone does while writing the screen.
 *Not when:* a View that holds nothing that should stop, a static custom drawing with no animator
 no listener and no surface.

## Why

<!-- human-only: not installed -->

**Everything follows from one property.** A composable is a function the runtime may call on any
frame, more than once per frame, in any order relative to its siblings, and skip entirely. It is not
a lifecycle, it is not a constructor, and it is not a place where things happen once. Every rule
above is a consequence: if the body can run at any time, work must not live in it; if it can be
skipped, the conditions for skipping matter; if it can be abandoned, cleanup must be explicit.

Developers arriving from the View system carry the opposite assumption, `onCreateView` runs once
`onDestroyView` runs once, and code between them happens in order. That intuition is what produces
the duplicate network call in a composable body.

**Why keys are the whole effect API.** `LaunchedEffect` gives you exactly one control: what it
restarts for. Everything people get wrong about effects is a key that is too broad or too narrow.
Too narrow, and the effect keeps running against a value that has moved on, the classic is an
observer still watching the id it was started with. Too broad, and it cancels and restarts on every
recomposition, which for a network call is a request per frame and looks, from the server, like an
attack.

`rememberUpdatedState` exists for the case where those two are both wrong: the effect must not
restart, but must use the current value. Without it you are choosing between a stale callback and a
restarting one.

**Why stability is not a micro-optimisation.** Compose skips a composable when it can prove the
parameters have not changed. A `List` parameter is an interface, so the compiler cannot prove the
instance was not mutated in place, and marks the composable unskippable. That decision propagates:
the composable recomposes, so its children are re-invoked, and one changed row becomes every visible
row recomposing on every emission.

This is why the fix is a type change rather than a caching layer. You are not making the work
faster, you are restoring the runtime's ability to not do it.

**Why deferring a state read changes the cost by an order of magnitude.** Compose runs three phases:
composition, layout, draw. Reading a state value in the composable body means the value is a
composition input, so a change re-runs composition, the whole function. Reading the same value
inside `Modifier.offset { }` makes it a layout input, so a change re-runs layout only. For a value
that changes every frame, that is the difference between recomposing a screen sixty times a second
and moving a rectangle.

**Why the text field is the sharpest case in the whole skill.** Every other rule here costs frames.
This one costs characters. Routing each keystroke out to a state holder and back introduces an
asynchronous hop between the keypress and the field's content, and under fast input the field
receives values out of order. On a physical keyboard in English it usually looks fine. On a
predictive, CJK, Indic or gesture keyboard the composing region is destroyed, and those are the
users least able to work around it, and least likely to be on the team.

**What changed, if you learned Compose earlier.**| Then | Now |
|---|---|
| `TextField(value, onValueChange)` for typed input | `TextFieldState` and `snapshotFlow` |
| `collectAsState()` | `collectAsStateWithLifecycle()` |
| `Modifier.offset(x, y)` for animated values | `Modifier.offset { }`, read in layout |
| `items(list)` | `items(list, key = ... contentType = ...)` |
| `@Composable` functions returning state everywhere | stateless composable plus a stateful wrapper |
| manual `LaunchedEffect(Unit)` for one-shot events | events consumed from state, cleared by the UI |

## Pitfalls

<!-- human-only: not installed -->

- **The same request is sent two or three times on one screen open.** Work in the composable body
 or an effect keyed too broadly.
- **A callback fires against the previous item.** An effect keyed too narrowly, holding the value it
 started with, `rememberUpdatedState` is the fix.
- **A listener that outlives the screen.** Registered without a `DisposableEffect`, so nothing
 removed it.
- **A scroll position, animation, or generated id that resets at random.** The value was not
 remembered, so it is recreated on recomposition.
- **The whole list flashes when one row changes.** An unstable parameter made the row composable
 unskippable.
- **Per-row state follows the wrong row after a deletion.** Missing or unstable `key`.
- **Every row re-runs its whole subtree while scrolling a mixed list.** Missing `contentType`.
- **The screen recomposes sixty times a second during an animation.** An animating value read in the
 composable body rather than in a lambda modifier.
- **Text drops or reorders characters, and breaks entirely on a gesture or CJK keyboard.** The field
 round-trips through an asynchronous state hop.
- **A component cannot be padded or sized by its parent.** The modifier parameter is missing or not
 forwarded. **Or padding applies twice** it was applied to two elements.
- **One colour stays light in dark mode.** A literal instead of a theme value.

## Provenance

<!-- human-only: outside agent_sections, never installed -->

**This section was missing until 22-Aug-2026.** `compose` and `kotlin` shipped without one, and two
attempts to append the eval-18 record silently did nothing because they anchored on a heading that
did not exist. Recorded because a skill with no provenance is one whose claims cannot be checked.

**eval 18 was a null, and two of three interop rules are gone.** `AndroidView`'s
`factory`/`update` split (construct once, mutate thereafter) was correct in **12 of 12** task-A runs
both models, every arm, with zero violations, its own documentation is the most-copied snippet in
Compose interop, and corpus saturation has been an anti-signal every time. Releasing the hosted View
was correct in **22 of 24** by outcome, 11 of 12 in each task. Both retired. The third rule
(inflation cost in lazy lists) was dropped as an observation rather than a rule: the seed had no
layout to inflate, and the task requires an `AndroidView` in a lazy list, so the rule's own *not
when* covered the case it was written for.

What survives is `INTEROP-2`, forwarding the host's lifecycle. Sonnet writes the
`ON_RESUME`/`ON_PAUSE` observer in its **control** arm, both batches; Haiku writes it in no control
and no `+core` run, and in one of two with the skill. Both models call `onCreate` and `onDestroy`
unprompted, it is specifically the resume/pause pair, the one that only fails after the app has
been backgrounded, that Haiku misses. Kept and recorded as *does not land* which is a different
finding from the model already doing it. See `evals/android/eval-18-compose-interop/RESULTS.md`.

** Rules `EFFECT-*` through `THEME-1` predate this session's eval record** and carry the evidence
described in the project's earlier eval files rather than a per-rule score here.
