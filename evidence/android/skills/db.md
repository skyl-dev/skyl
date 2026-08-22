# Evidence: `android/db`

15 rules. One measured, one rewritten after failing to land, one shrunk to a pointer after a seam
eval. The rest are unmeasured.

## What was run

| eval | what it tested | models | arms | runs |
|---|---|---|---|---|
| 08 | two screens over one cache | Haiku 4.5, Sonnet 5 | control / +core / +core+db | 12 |
| 09 | the skill against `core` alone | Haiku 4.5, Sonnet 5 | control / +core / +core+db | 4 |
| 10 | notes that sync | Haiku 4.5, Sonnet 5 | control / +core / +core+db | 11 |
| 20 | the seam with `security` | Haiku 4.5, Sonnet 5 | control / +db / +security / both | 32 |

## What separated

`WRITE-1`, a multi-statement write is one transaction. Haiku wrote delete-then-insert with no
transaction in **4 of 4** runs that used the pattern. Sonnet used a transaction in 3 of 3.

## An eval that could not test this skill

Eval 09 returned a null and the null was not informative: **the task specified the behaviour most of
these rules describe**, so four rules had nothing to act on and the rest were told what to do by the
prompt. It is recorded because a null from a task that cannot tempt the rules is not evidence of
absence, and reading it as one would have deleted a skill on no information.

## A rule that failed to land, and why it was the rule's fault

`SYNC-2` first read *"resolved by a server-assigned version, never by device clocks"*. It failed to
land in **every** treated run: all 10 runs that produced code used the device clock, because the
task's API supplied no version and the rule named no alternative.

**A prohibition with no actionable branch for the common case is not a rule a model can follow.** It
was rewritten to state what to do when the server offers nothing.

## What the seam eval changed

`STORE-3` used to name the deprecated crypto wrapper and defer the alternative to `android/security`.
Measured with four arms, `security` alone produced Keystore-backed encryption in **2/2** Haiku runs,
and **`db` and `security` together produced 0/2**. The extra rule count displaced the rule that
mattered, on the model least able to absorb it. Sonnet was unaffected.

`STORE-3` is now a pointer. **Two skills carrying one hazard measurably degrades the smaller model**,
which is the strongest argument in this project for the layering rule.

## A later eval, stopped part-way

16 of 24 runs before the eval was halted, so this is partial and recorded as such: task A complete on
both models, task B on Haiku only.

**Schema work was already right.** Adding a column to a database documented as already shipped
produced a version bump and a migration in 10 runs of 10, controls included, and nobody enabled
destructive fallback. Exporting the schema is weaker, at 3 of 10.

**Offline editing was already right.** Writing locally first, marking the row pending, observing the
store rather than polling, and keeping the main-thread guard were satisfied in 9 or 10 runs of 10.
Scheduling durable work to send the edit later split by model: Sonnet did it, Haiku did not, in any
arm.

**The seed's own bug was fixed by every arm.** `refresh()` shipped as clear-then-fetch, which empties
the app if the fetch fails. All six Haiku runs replaced it, controls included.

**Remote deletion, staleness and forced refresh moved by one run each**, which is noise at this
sample size, and the eval stopped before Sonnet could add anything.

