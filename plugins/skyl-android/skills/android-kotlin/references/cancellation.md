# Cancellation

Referenced by `kotlin ASYNC-2`. `core WORK-2` states when work may be abandoned; this is the
mechanism that leaks it.

Of every rule measured across five models and two harnesses, this is the one nothing fixed. Opus
handles it unaided; Sonnet, Haiku and qwen did not, treated or not. It is worth understanding
rather than memorising.

## The mechanism

`CancellationException` is an ordinary exception on the JVM. Cancelling a coroutine works by
throwing it at the next suspension point. So everything that catches broadly catches it too:

    try { … } catch (e: Exception)   { … }   // catches cancellation
    try { … } catch (e: Throwable)   { … }   // catches cancellation
    runCatching { … }                        // catches cancellation

A coroutine that swallows its own cancellation keeps running after its scope is gone. The screen is
destroyed, the work continues, and it completes against a consumer nobody is listening to. Nothing
crashes and nothing logs, which is why this survives code review. The code reads as careful error
handling.

## The two fixes, in order of preference

**1. Catch what you can name.** This removes the question entirely, a `catch (e: IOException)`
cannot catch cancellation.

    try {
        api.load()
    } catch (e: IOException)            { Result.Offline }
    catch (e: SerializationException)   { Result.Malformed }

**2. Rethrow it first** where a broad catch is genuinely needed:

    try {
        api.load()
    } catch (e: CancellationException) {
        throw e
    } catch (e: Exception) {
        Result.Failed(e)
    }

Order matters. `CancellationException` must come first, or the broad clause takes it.

## `runCatching` is the common case

`runCatching` is a broad catch with friendly syntax, and it has nowhere to rethrow from, the
failure is already a value by the time you inspect it. Inside a coroutine, either avoid it or
unwrap deliberately:

    runCatching { api.load() }
        .onFailure { if (it is CancellationException) throw it }

## Timeouts arrive as cancellation

`withTimeout` cancels the body, so the failure surfaces as a `TimeoutCancellationException`, a
subclass of `CancellationException`. Code that suppresses all cancellation cannot distinguish:

- **the caller's cancellation** the user navigated away; nothing should be reported, retried, or
  logged as an error;
- **a timeout** the work took too long; the user probably should be told, and a retry may be
  right.

They need opposite responses, and suppressing both makes them look identical.

If you want a timeout as a value rather than an exception, `withTimeoutOrNull` returns `null`
instead, often the cleaner shape.

## Cleanup still runs

Cancellation unwinds through `finally`, so cleanup happens. But a cancelled scope will not suspend
again, a suspending call inside `finally` throws immediately. For cleanup that must suspend:

    withContext(NonCancellable) { db.close() }

Use it only for genuine cleanup. `NonCancellable` around real work is how a "cancelled" operation
carries on to completion.

## Cooperative cancellation

Cancellation is delivered at suspension points. A tight computational loop with no suspension never
notices it and runs to completion after its scope has died. Check explicitly:

    for (row in rows) {
        ensureActive()          // throws CancellationException if the scope is gone
        process(row)
    }

`yield()` does the same and also gives the dispatcher a chance to run something else.

## Reviewing for this

Search the codebase for `catch (e: Exception)`, `catch (e: Throwable)` and `runCatching` inside
suspending code. Each one is either a bug or a deliberate decision, and the deliberate ones should
say so, a rethrow line is the cheapest possible comment.
