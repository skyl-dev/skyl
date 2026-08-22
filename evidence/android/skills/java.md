# Evidence: `android/java`

16 rules. Partly measured: eval 11 discarded one of its two tasks, so six rules remain untested.

## What was run

| eval | models | arms | runs |
|---|---|---|---|
| 11 | Haiku 4.5, Sonnet 5 | control / +core / +core+java | 24 |

Task A was discarded as invalid. Its results are not counted anywhere here.

## What separated

| rule | finding |
|---|---|
| `ASYNC-5` name the `Looper` explicitly | **0/2 → 2/2 on both models.** `new Handler()` silently adopts the current thread's looper and is deprecated at API 30. |
| `INTEROP-1` | **Haiku 0/2 → 2/2.** Inert on Sonnet, which already does it. |

## What the eval got wrong about this skill

`LEAK-2` was scored as failing to land, 1 of 12 runs. Reading the runs showed the opposite: every
treated run kept a static singleton holding a `Context` **because `CONVERT-1` says preserve
behaviour exactly**, which is the correct resolution during a conversion.

The models arbitrated between two rules in this file and got it right. The file had never said which
one wins. `LEAK-2` now carries the conversion exception and `CONVERT-1` states that it outranks the
structural rules during a conversion.

**The detector had scored a right answer as a miss.** That is the failure mode this project has hit
thirteen times, and it is why scoring code is now run against the unmodified seed first and its
fixtures include near-misses.

## Satisfied unaided

`CONVERT-1` carries an observation-contract clause that eval 11 found unnecessary: all 12 runs kept
`java.util.Observable` and none swapped it for a `Flow`, in any arm on either model. Kept on the
grounds that it costs little and the sample is two per cell, which is a weaker justification than
the bar normally accepts. Marked rather than quietly retained.

## Corrections from primary sources

Two factual errors were caught by checking the platform documentation rather than the corpus.

`ASYNC-1` claimed `AsyncTask` had been **removed from the platform**. It is deprecated since API 30
and still present. The real reasons are better than the one originally written: it swallows
exceptions thrown in `doInBackground`, and its default executor is serial.

The `LEAK-*` rules and `CONVERT-4`/`CONVERT-5` were added after re-reading the claim register rather
than an extraction summary of it. The first draft had been made from the summary and missed the
entire Android-Java cluster the evidenced claims actually name.

## Ledger

| rule | status | evidence |
|---|---|---|
| `ASYNC-5` | measured | 0/2 → 2/2 on both models. |
| `INTEROP-1` | measured | Haiku 0/2 → 2/2. Inert on Sonnet. |
| `CONVERT-1` | satisfied-unaided | Its observation-contract clause was unnecessary in 12 of 12 runs. |
| `LEAK-2` | not-tempted | Scored as not landing; reading the runs showed the models correctly applied `CONVERT-1` instead. Its own effect is untested. |
| `NULL-1` | not-tempted | Task A discarded. |
| `NULL-2` | not-tempted | Not separately tempted. |
| `INTEROP-2` | not-tempted | Not separately tempted. |
| `LEAK-1` | not-tempted | Task A discarded. |
| `LEAK-3` | not-tempted | Task A discarded. |
| `ASYNC-1` | not-tempted | Task A discarded. Its factual claim was corrected against primary sources. |
| `ASYNC-2` | not-tempted | Task A discarded. |
| `ASYNC-4` | not-tempted | Task A discarded. |
| `CONVERT-2` | not-tempted | Not separately tempted. |
| `CONVERT-3` | not-tempted | Not separately tempted. |
| `CONVERT-4` | not-tempted | Added after re-reading the register. Not tempted. |
| `CONVERT-5` | not-tempted | Added after re-reading the register. Not tempted. |
