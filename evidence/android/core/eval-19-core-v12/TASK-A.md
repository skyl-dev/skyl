# Task A, export the notes

Brownfield. `NoteStore` is documented as synchronous: every method touches the filesystem and
returns when it is done, with no asynchronous variant. `SettingsScreen` is a composable that already
holds a `NoteStore` and has a TODO. There is no ViewModel and no coroutine scope in sight.

## Prompt

Add an **Export notes** button to the settings screen.

Pressing it writes every note to a single backup file, then shows the SHA-256 of what was written so
the user can check it later. A full library is a few thousand notes.

Change whatever needs changing. Write the files you would actually write.

## What the task tempts

| Rule | The situation |
|---|---|
| `WORK-3` | a synchronous store, a hash over its output, and a click handler with nothing async in it |

The seed deliberately supplies no ViewModel and no scope, so the easy path is to call `readAll()`
straight from `onClick`. "A few thousand notes" is the size, stated as a fact about the data.
