# Evidence: `android/java`

Android-specific Java: the leaks the language does not prevent, the null contracts Kotlin callers
depend on, and converting old code without changing what it does.

## What was run

**2 evals, 38 recorded runs**, on Haiku 4.5 and Sonnet 5. Every run is archived: the generated
sources, the prompt each arm received, and the model each one reported.

Control against `+core` against `+core+java`.

## What loading the skill changed

**Naming the `Looper` when constructing a `Handler`.** The no-argument constructor silently adopts
whatever thread it is created on and is deprecated. Unaided Haiku runs kept it; loaded runs named the
looper. Sonnet avoided the question by using a different mechanism entirely.

**One interop rule improved on Haiku** and was already handled by Sonnet.

## What the tested models already handle

Moving long work off the main thread, disposing Rx subscriptions, tearing down in `onDestroy`, and
guarding a nullable lookup were done in nearly every run including controls. Nobody reached for
`AsyncTask`.

**Conversion is handled well unaided.** Converting a Java singleton to Kotlin, keeping its Java
callers compiling, and preserving the nullable signature were done in every run. So was keeping a
static `Context` that a structural rule forbids and the conversion rule protects: every run resolved
that precedence the way the skill states it, without being told.

## Where the skill did not change behaviour

Writing a characterization test before converting happened in one run of twelve.

## Corrections from primary sources

`AsyncTask` is **deprecated since API 30 and still present**, not removed from the platform. The real
reasons to avoid it are better than the one first written: it swallows exceptions thrown in the
background, and its default executor is serial.
