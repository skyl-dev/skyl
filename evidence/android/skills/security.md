# Evidence: `android/security`

9 rules. One separation, and a rule that exists because an eval found a hole in the layering.

## What was run

| eval | what it tested | models | arms | runs |
|---|---|---|---|---|
| 17 | the skill as first written | Haiku 4.5, Sonnet 5 | control / +core / +core+security | 24 |
| 20 | the seam with `db` | Haiku 4.5, Sonnet 5 | control / +db / +security / both | 32 |

## What separated

`OUT-1`, declare what is copied off the device. Haiku **0/2 → 2/2** on declaring backup rules at
all. The half that asks for **both** attributes, one for modern platform versions and one for older
ones, landed in one run of two, which is noise. So the rule reliably gets backup considered and does
not reliably get both files.

Sonnet declared backup rules in its control arm.

## Where a secret actually goes

Storing a session token is where this skill earns its place. Across twelve runs with no skill loaded,
**five used a deprecated crypto wrapper and seven stored the token with no encryption at all.** One
used the platform keystore directly.

`STORE-1` states the alternative directly rather than deferring to another skill, because an app that
stores only a token has no database and would never load the storage skill at all.

**With `security` loaded, keystore-backed encryption appears in 4 of 4 runs against 0 of 4 in
controls.**

## The seam result

Eval 20 also found the first measured case of two skills interfering.

| Haiku, keystore-backed encryption | control | `+db` | `+security` | **both** |
|---|---|---|---|---|
| | 0/2 | 0/2 | **2/2** | **0/2** |

`security` alone works. Loading `db` alongside it **destroys the behaviour on Haiku**: fifteen extra
rules displaced the one that mattered, on the model least able to absorb them. Sonnet was unaffected.
`db STORE-3` was shrunk to a pointer as a result.

## The skill knows when not to fire

Eval 17's second task deliberately included a case where `IPC-1` must **not** fire: sharing a
document to an app of the user's choosing, which is the legitimate implicit intent.

**All 12 task-B runs kept the share sheet, in every arm.** The skill did not turn a legitimate
implicit intent into a defect. 
