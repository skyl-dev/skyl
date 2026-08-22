# Evidence: `android/permissions`

8 rules, 1 retired. The strongest result in the family, and the one that best shows a diagnosis being
tested rather than a rule.

## What was run

| eval | what it tested | models | arms | runs |
|---|---|---|---|---|
| 16 | the skill as first written | Haiku 4.5, Sonnet 5 | control / +core / +core+permissions | 24 |
| 16b | two rules rewritten after 16 | Haiku 4.5, Sonnet 5 | skill arm only, controls reused | 8 |

## What separated

Eval 16, three movements, and the two models moved on **different** rules.

| check | Haiku | Sonnet |
|---|---|---|
| `ASK-2` declaration removed or requested | **0/2 → 2/2** | 2/2 every arm |
| unnecessary `CAMERA` declaration *(violation)* | 2/2 every arm | **2/2 → 0/2** |
| `GRANT-1` re-read state on resume | 0/6 every arm | **0/2 → 2/2** |

## The finding the scoring table could not see

Haiku's control ships the exact `SecurityException` the rule describes: `ACTION_IMAGE_CAPTURE` called
while `CAMERA` sits declared and unrequested.

With the skill loaded, Haiku fixed it **by requesting `CAMERA`**, and built a camera viewfinder to go
with it. That satisfies one rule while violating the one above it, which says not to take the
permission at all. Sonnet deleted the declaration and kept the intent.

Same rule, same column, two fixes of very different quality. `ASK-2` now ranks the two fixes instead
of accepting either.

## Two rules that were on the wrong side of the request

Eval 16 recorded `GRANT-3` and the media half of `ASK-1` as **not landing**. Reading the runs showed
why, and in both cases the rule was positioned wrongly rather than being wrong.

Haiku launched fine location alone in all six runs, so it never reached a partial-grant state for
`GRANT-3` to handle: the missing rule was upstream, and is now `LEAST-1`. And Haiku used the photo
picker **and** declared a storage permission anyway, because `ASK-1` said to look for a
permission-free path and never said not to declare the permission too.

**Eval 16b tested that diagnosis with the prediction written first, and both halves were met:**

| Haiku | control | first version | revised |
|---|---|---|---|
| requests coarse location alone | 0/2 | 0/2 | **2/2** |
| media permission declared *(viol)* | 2/2 | 2/2 | **0/2** |
| `CAMERA` declared *(viol)* | 2/2 | 2/2 | **0/2** |
| picker **and** permission *(viol)* | 1/2 | 2/2 | **0/2** |

The comparison carries a stated confound: the two prompts differ by four changes, not two, because
the earlier prompt was generated before a ship-time adjustment. Attribution survives it, and the
results document says so rather than leaving it implicit.

## What was retired

The in-context timing rule: ask when the user invokes the feature, never at launch. **Zero
launch-time requests in 12 of 12 runs**, every arm including both controls. It is the most-repeated
piece of advice in the entire permissions corpus and the one thing no model needed telling.

## A correction to this eval's own record

Eval 16 first reported `GRANT-3` as *"Sonnet accepts a coarse grant in 3 of 6 with no arm pattern."*
That came from a column matching a **declaration** rather than a request, and then from a rescore
whose pattern missed a `const val` binding. Re-scored, both Sonnet skill runs used coarse location
and nothing else. The correction is annotated in place rather than swapped silently.

## Ledger

| rule | status | evidence |
|---|---|---|
| `ASK-2` | measured | Haiku 0/2 → 2/2. Now ranks its two fixes after Haiku chose the worse one. |
| `ASK-1` | measured | The belt-and-braces clause took Haiku from 2/2 violations to 0/2 in eval 16b. |
| `LEAST-1` | measured | Haiku 0/2 → 2/2 on requesting coarse location alone. Added from a diagnosis and then tested. |
| `GRANT-1` | measured | Sonnet 0/2 → 2/2. Haiku 0/6 in every arm. |
| `GRANT-3` | not-landing | Haiku requests fine location alone in all six runs. Depends on `LEAST-1` upstream. |
| `ASK-4` | not-tempted | The rationale ambiguity was not separately tempted. |
| `GRANT-2` | satisfied-unaided | The degrade half was satisfied 12 of 12; the re-prompt-loop half was never reached. |
| `DECL-1` | not-tempted | Not separately tempted. |
| `ASK-3` | retired | Zero launch-time requests in 12 of 12 runs, every arm including both controls. |
