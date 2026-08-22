# Evidence: `android/xml`

14 rules, 1 retired. The clearest demonstration in the family that corpus support is an anti-signal.

## What was run

| eval | models | arms | runs |
|---|---|---|---|
| 12 | Haiku 4.5, Sonnet 5 | control / +core / +core+xml | 24 |

## What separated

| rule | finding |
|---|---|
| `LIST-2` | **0/2 → 2/2 on both models.** Eight runs moving the same way. |
| `LIST-4` | **0/2 → 2/2 on both models.** |
| `LIST-3` | Separated on Haiku. Already satisfied by Sonnet. |
| `STATE-1` | Separated on Sonnet. Landed nowhere on Haiku. |
| `HOST-1` | Separated on Haiku. Inert on Sonnet. |

## The finding this skill exists to demonstrate

**Four of those rules have zero support anywhere in the 3,845-file corpus.** They were found by
running a control arm, not by reading what other people had written down.

In the same file, the two rules that *are* corpus-backed are satisfied by every arm including the
controls. Within one skill, the measurement-sourced rules were the entire effect and the
corpus-sourced ones were inert.

That is the anti-signal stated as precisely as this project can state it: the corpus and the
training data are the same material, so a rule everyone has written down is one the model already
follows.

## A correction that held up in behaviour

An earlier version claimed the default `ViewCompositionStrategy` was wrong in two places. Only the
Fragment case is real: the default already handles the pooled case. After the correction, **not one
of the 12 task-B runs** set the pooling strategy on a non-pooled Fragment header, treated arms
included, which is the behaviour the corrected rule predicts.

## Ledger

| rule | status | evidence |
|---|---|---|
| `LIST-2` | measured | 0/2 → 2/2 on both models. Zero corpus support. |
| `LIST-3` | measured | Separated on Haiku, satisfied by Sonnet. Zero corpus support. |
| `LIST-4` | measured | 0/2 → 2/2 on both models. Zero corpus support. |
| `STATE-1` | measured | Separated on Sonnet, landed nowhere on Haiku. Zero corpus support. |
| `HOST-1` | measured | Separated on Haiku, inert on Sonnet. |
| `LIST-1` | candidate | Satisfied by every arm including the controls. Corpus-backed. |
| `HOST-2` | candidate | Satisfied by every arm including the controls. Corpus-backed. |
| `HOST-4` | not-tempted | Not separately tempted. |
| `STATE-2` | not-tempted | Not separately tempted. |
| `LAYOUT-1` | not-tempted | Not separately tempted. |
| `LAYOUT-2` | not-tempted | Not separately tempted. |
| `BIND-1` | not-tempted | Not separately tempted. |
| `BIND-2` | not-tempted | Not separately tempted. |
| `RES-1` | not-tempted | Not separately tempted. |
| `HOST-3` | retired | Cut before shipping: a `ComposeView`'s state using `rememberSaveable` was already universal. |
