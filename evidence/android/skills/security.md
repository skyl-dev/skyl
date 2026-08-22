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

## `STORE-1` exists because the eval found a hole in the layering

Eval 17 measured how the runs stored a session token. Of twelve task-A runs, **five used a deprecated
crypto wrapper and seven stored the token with no encryption at all.** Only one used the platform
keystore directly, and that one was a `+core` arm.

`db STORE-3` said the wrapper was not the alternative and deferred to this skill for what is. **This
skill never caught the handoff**, because its key rules assumed someone hand-rolling encryption
rather than reaching for the library everyone reaches for.

Worse: `db` is detected by a database dependency, and an app storing only a token has none. In a
project of that shape `db` never loads, so nothing anywhere would have said it. A rule that lives
only in a skill that will not be installed is a rule that does not exist.

`STORE-1` was added and written to stand alone. **Eval 20 measured it properly:** `security` alone
produces keystore-backed encryption in 4 of 4 runs where controls produce 0 of 4.

## The seam result

Eval 20 also found the first measured case of two skills interfering.

| Haiku, keystore-backed encryption | control | `+db` | `+security` | **both** |
|---|---|---|---|---|
| | 0/2 | 0/2 | **2/2** | **0/2** |

`security` alone works. Loading `db` alongside it **destroys the behaviour on Haiku**: fifteen extra
rules displaced the one that mattered, on the model least able to absorb them. Sonnet was unaffected.
`db STORE-3` was shrunk to a pointer as a result.

## Restraint, measured

Eval 17's second task deliberately included a case where `IPC-1` must **not** fire: sharing a
document to an app of the user's choosing, which is the legitimate implicit intent.

**All 12 task-B runs kept the share sheet, in every arm.** The skill did not turn a legitimate
implicit intent into a defect. This is the only place in the family where restraint was measured
rather than assumed, and it is the cheaper of the two failures to miss.

## A correction to this eval's own record

Eval 17 first reported that **24 of 24** runs used the deprecated wrapper. That was false. It was
generalised from a single hand-checked run, and it also used the eval's total across both tasks for a
claim about one task. The real figure is 5 of 12, with 7 more storing the token unencrypted, which is
a worse failure that had been missed while looking for the wrapper.

The conclusion the rule was built on survives and is now measured properly. The evidence originally
cited for it was manufactured, and the correction is recorded where the claim was made.

## Ledger

| rule | status | evidence |
|---|---|---|
| `OUT-1` | measured | Haiku 0/2 → 2/2 on declaring backup rules. The both-attributes half landed 1 of 2, which is noise. |
| `STORE-1` | measured | `security` alone produces keystore-backed encryption 4/4 against 0/4 in controls. |
| `IPC-1` | measured | Restraint held: all 12 task-B runs kept the legitimate implicit intent, every arm. |
| `KEY-1` | satisfied-unaided | Never tempted: every run took the library path. |
| `KEY-2` | satisfied-unaided | Never tempted: every run took the library path. |
| `OUT-2` | not-tempted | Not separately tempted. |
| `IPC-2` | not-tempted | Narrowed after the flag half proved unnecessary. `FLAG_MUTABLE` appears in 0 of 12 runs, so the combination it now describes is untested. |
| `IPC-3` | not-tempted | Reached by neither task. |
| `TRUST-1` | not-tempted | Reached by neither task. |
