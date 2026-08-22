# The five axes

A skill belongs to exactly one axis. The axis determines when it loads.

| axis | loads when | examples |
|---|---|---|
| **core** | always, for the family | `android/core` |
| **language** | the language is present | `android/kotlin`, `android/java` |
| **framework** | the UI toolkit or framework is present | `android/compose`, `android/xml` |
| **service** | an external service is used | `appwrite/core` *(not yet built)* |
| **topic** | a concern only some projects have | `android/db`, `android/permissions` |

A project loads the **intersection**: its core, its language, its framework, whichever services it
calls, and whichever topics it actually has.

## The core / topic boundary

**Core is what every project in the family has. A topic is what only some have** which is exactly
what makes a topic detectable.

If a rule would fire on every project, it belongs in core and needs no detection. If it fires on
some, it is a topic and the `detect` block is what decides.

## Topics group by concern, not by library

`android/db` covers persistence, what is stored, what survives, what is encrypted at rest, whether the project uses Room, DataStore, or files. It is not `android/room`.

The test: **does this say something the library's own documentation does not?** A skill organised
around a library tends to restate that library's docs, which is the material the model already has.

## What is not an axis

Architecture patterns (`mvi`, `clean`) are not skills: nothing detects them. They resolve to a set
of skills, `core + kotlin + compose`, and are better expressed as a stack template.

A concern with no detection signal is a `references/` file inside the skill that owns it, not a
skill of its own.

## Family

A family is a platform or ecosystem: `android`, `web`, `appwrite`. Families compose sideways, a
project can load `android/*` and `appwrite/*` together, which is why `service` is its own axis
rather than a topic inside each platform.
