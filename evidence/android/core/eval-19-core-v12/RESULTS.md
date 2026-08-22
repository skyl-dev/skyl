# Eval 19, `core` v1.2.0 (`WORK-3`, `BUILD-1`–`BUILD-3`)

16 runs: 2 tasks × 2 arms (control / `+core`) × 2 models × 2 batches. All model ids confirmed.

## Result

| Rule | Finding | Action |
|---|---|---|
| `WORK-3` main thread | Haiku control **fails 2/2**; `+core` fails 1/2. Sonnet clean in every arm. | **keep** records as not landing |
| `BUILD-1` shrinking | `isMinifyEnabled` and `proguardFiles` in **8/8** every arm | **retire** |
| `BUILD-2` `api`/`implementation` | no run violated it, and the one column that said otherwise was wrong | **cut** |
| `BUILD-3` KSP over KAPT | Haiku uses **KAPT for Room in 4/4** runs, *both arms*. Sonnet uses KSP in 3/4. | **keep** records as not landing |

### `WORK-3`, the failure is real and hand-verified

The Haiku control does exactly what the rule describes:

```kotlin
Button(onClick = {
    val notes = store.readAll()                      // documented as touching the filesystem
    ...
    val hash = MessageDigest.getInstance("SHA-256")  // over a few thousand notes
```

Both control runs. With `+core` it happens in one of two. So the rule names a genuine Haiku failure
and does not reliably fix it, and Sonnet never had the problem.

This is the first direct evidence for `WORK-3` on anything other than Opus. The prior record was
`OFF-MAIN` scoring 6/6 in an Opus control, which said nothing about the models where it fails.

## The pre-registered falsifier, and where I am departing from it

`PREDICTION.md` said: *"if `BUILD-1` does not move, all four rules came from a corpus bucket rather
than a model failure and the build section should be cut rather than kept as unmeasured."*

`BUILD-1` did not move, 8/8 in both arms. I am **cutting `BUILD-1` and `BUILD-2` and keeping
`BUILD-3`** which is a departure, and the reason is that the falsifier's premise is directly
contradicted for that one rule. `BUILD-3` is not a corpus artifact: **Haiku reaches for KAPT on Room
in four runs out of four** in both arms, and Room has led with KSP for years. That is a real model
failure that the rule fails to fix, which is the "does not land" verdict, not the "corpus bucket"
verdict.

Departing from a pre-registration is only legitimate when the data contradicts its premise rather
than its conclusion. Recording it here so the departure is visible rather than quiet.

## Method notes

**Tenth detector error, `roomApiVIOL` scored the correct answer as a violation.** The column
assumed `api("androidx.room:room-runtime")` in `:core-data` was wrong. It is right: the runs declare

```kotlin
abstract class NotesDatabase : RoomDatabase()
```

publicly in that module, so a Room type *is* in the module's public signature, which is precisely the
condition `BUILD-2` names for `api`. Every run got this right and my column called all eight wrong.

Same shape as the ninth: **a column encoding a preference instead of the rule's actual condition.**
The ninth preferred one release mechanism over another; this one preferred one dependency
configuration without checking the condition attached to it. `METHOD.md` already carries the rule
this violates.

**Task B has a design flaw worth recording.** *"Make `./gradlew assembleRelease` produce something we
could put on the Play Store"* reads as an instruction to *run* the build. Several runs did, one
Haiku run produced 1,221 files and took 20 minutes against 2 minutes for its siblings, and three
Sonnet runs ran past 27 minutes. It is a valid outcome statement and it makes runtime vary tenfold
while spending the run's budget on Gradle output rather than on the decision under test. A build
task should ask for the configuration, not for the artifact.

**`BUILD-2` was untestable as designed.** The task asks for Room to be exposed to `:app`, which makes
`api` correct, so nothing could tempt the violation. No evidence either way; cut rather than kept
because an unmeasured rule in the always-installed skill is the most expensive place to keep one.
