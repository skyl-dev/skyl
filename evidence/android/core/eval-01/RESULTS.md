# Eval 01, results

18 runs. 6 per arm, 6 batches. Batches 1–4 run by hand; batches 5–6 run headless in tmux with
every plugin disabled. Model: Claude Opus 5. Greenfield, fresh session, one screen.

Conditions and their limits: `CONDITIONS.md`. Per-rule verdicts: `SCORES.tsv`.

## Contamination in batches 1–4, and why the result survives it

`compose-expert@aldefy-compose-skill`, a Compose skill, and one of the 293 repos in our own
corpus, was enabled globally. Its name and description sat in context for all 15 hand-run
sessions; in one, **a control run** it was invoked as a full skill.

Batches 5 and 6 were re-run with every plugin disabled, verified before launch. **They replicate
batches 1–4 exactly on every detector.** The contamination changed nothing measurable.

## The result

| Rule | control | core | core+kotlin | verdict |
|---|---|---|---|---|
| **STATE-4 / ASYNC-4** flow operator for re-triggered reads | **0/6** | **6/6** | **6/6** | **SEPARATED** |
| STATE-1 process death / SavedStateHandle | 6/6 | 6/6 | 6/6 | not needed here |
| DATA-2 money as minor units | 5/6 | 6/6 | 6/6 | not needed here |
| DATA-4 clear the store on sign-out | 6/6 | 5/6 | 5/6 | not needed here |
| L10N-1 localized formatters (zero `SimpleDateFormat` anywhere) | 6/6 | 6/6 | 6/6 | not needed here |
| A11Y-1 contentDescription | 6/6 | 6/6 | 6/6 | not needed here |
| ASYNC-2 rethrow CancellationException | 6/6 | 5/6 | 5/6 | not needed here |
| ASYNC-5 `stateIn` + `WhileSubscribed` | 6/6 | 6/6 | 6/6 | not needed here |
| DATA-3 no defaulting a failed parse | 6/6 | 6/6 | 5/6 | not needed here |
| TYPE-3 read-only types at boundaries | 6/6 | 6/6 | 6/6 | not needed here |
| A11Y-2 minimum touch target | 3/6 | 4/6 | 2/6 | unresolved |

**One rule separated out of sixteen exercised.** `0/6 → 6/6` in both treatment arms, replicated
across contaminated and isolated conditions.

It is `core STATE-4`, written yesterday to resolve a leak between two other skills, backed by
nothing in the corpus.

## Three findings

**1. Corpus rank predicted the wrong thing, again, under measurement.**
`STATE-1` has 47 independent repos behind it, the most-corroborated claim in 3,845 files, and
the model does it 6/6 unaided. `L10N-1`, `A11Y-1`, `DATA-2`, `DATA-4` likewise. The one rule that
separated has zero corpus support. This is the fourth independent confirmation.

**2. My own predictions failed in one direction.**
`EVAL-PLAN.md` called `DATA-2`, `DATA-4`, `L10N-1`, `L10N-2`, `STATE-2` and `SER-1` "likely
holds". All were already satisfied. Predicting **more** model failure than exists is the specific
bias that produces a bloated skill, and it is mine as much as the ecosystem's.

**3. `kotlin` adds nothing over `core` on this task.**
Arm 3 never beats arm 2 on any detector, and is worse on three (`A11Y-2` 2/6 vs 4/6, `DATA-3`
5/6 vs 6/6, `ASYNC-2` unchanged). `kotlin ASYNC-4` is redundant with `core STATE-4`, one
behaviour, two skills, which the layering rule forbids. The composed install has not yet shown a
benefit, and shows a hint of the predicted degradation.

## What this makes the skills

`android/core`, **1 rule survives measurement** of the 16 exercised. Four more are untested
because the task did not exercise them (BOUND-3, SEC-1, SEC-2, WORK-1).

`android/kotlin`, **0 rules survive.** Its one separating rule duplicates core's.

## What this does not license

- **Deleting the rules.** Verdicts read `NOT-NEEDED-HERE`. One condition, one model, greenfield
  6 runs. `6/6` at n=6 still admits a true rate near 70%.
- **Quoting a win rate.** There is no placebo arm and no negative-case arm. Restraint, whether a
  skill makes the model change things it should have left alone, is unmeasured.
- **Concluding skills do not work.** It concludes that *these* rules are not needed *here*. The
  conditions where a skill plausibly earns its place, long sessions, weaker models, brownfield
  competing conventions, are all untested.
