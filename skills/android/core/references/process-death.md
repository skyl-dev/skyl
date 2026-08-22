# Process death

Referenced by `core STATE-1`.

## What actually happens

The system reclaims backgrounded app processes under memory pressure. Your process is killed
outright, no callbacks, no unwinding, nothing runs. When the user returns, the app starts fresh
and is expected to look as though it never left.

Rotation is a different event entirely: the activity is recreated, the process survives, and
anything held in a `ViewModel` is still there. **A screen can pass every rotation test and lose
everything to process death** which is why rotation is not the test.

## Reproducing it

    adb shell am kill <package>          # then resume from the launcher
    adb shell am kill <package>          # and again from a deep link

Swiping the app away from Recents is **not** the same thing, that is a user-initiated finish, and
the system discards saved state. If you want the setting instead of the command:
Developer options → **Don't keep activities**.

Test both entry paths. Resuming from the launcher and arriving via a deep link restore different
things, and the deep-link path is the one that usually breaks.

## What to save, and what not to

Save what **rebuilds** the screen. Do not save what **fills** it.

| Save | Do not save |
|---|---|
| the id of the thing being shown | the thing itself |
| a search query, a filter selection | the results of that query |
| a scroll position, an expanded row | the list being scrolled |
| which step of a flow the user is on | the fetched contents of that step |

Everything in the second column belongs in local storage or is re-fetched. The saved state exists
to reconstruct *where the user was* not *what they were looking at*.

## Why the size limit bites the wrong screen

`SavedStateHandle` writes into the activity's saved-state `Bundle`. Every saved `Bundle` in the
process is assembled into a single parcel and passed across a binder transaction with a hard
ceiling of roughly 1 MB shared process-wide, minus whatever the framework is already using.

So a screen that saves a long note does not fail on its own. It fails whichever screen happens to
push the total over the edge, at stop time, with a `TransactionTooLargeException` and a stack trace
pointing at the framework rather than at the code that saved too much. Aim for the low tens of KB
per screen and treat anything larger as a bug in what you chose to save.

## Typed text is the common mistake

A half-written message, a partly filled form, a long note, these feel like "state the user would
hate to lose", and they are. They are also exactly what must not go in the bundle.

Persist them to local storage as the user types, on a boundary rather than per keystroke
(`core STATE-4`), and keep only the draft's id in saved state.

## Checking your work

Ask of each field: *if the process died right now and the user came back, would this need to be
here for the screen to look right, or could it be rebuilt from an id and a query?* If it could be
rebuilt, rebuild it.
