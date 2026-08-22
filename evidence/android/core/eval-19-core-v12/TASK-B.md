# Task B, add Room, and make the release build shippable

Brownfield. Two modules. `:core-data` declares every dependency with `api(...)`. `:app` applies the
`kapt` plugin for Hilt. The `release` build type is empty.

## Prompt

We are adding Room to `:core-data` so notes are queried from a database instead of read off a pile
of JSON files. Wire it up: an entity, a DAO, and the database class, exposed so `:app` can use them.

This app has never shipped a release build. Make `./gradlew assembleRelease` produce something we
could put on the Play Store.

Change whatever needs changing. Write the files you would actually write.

## What the task tempts

| Rule | The situation |
|---|---|
| `BUILD-1` | the `release` block is empty and nothing is shrunk |
| `BUILD-2` | `:core-data` uses `api` for everything, and Room adds more dependencies |
| `BUILD-3` | `kapt` is already applied, and Room ships a KSP processor |

"Something we could put on the Play Store" is the outcome. It never says shrink, minify, or R8.
