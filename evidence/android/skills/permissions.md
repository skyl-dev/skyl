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

## Dropped before publication

The in-context timing rule: ask when the user invokes the feature, never at launch. **Zero
launch-time requests in 12 of 12 runs**, every arm including both controls. It is the most-repeated
piece of advice in the entire permissions corpus and the one thing no model needed telling.
