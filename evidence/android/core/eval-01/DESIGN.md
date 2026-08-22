# Eval 01, design

## What this measures

**Primarily admission test 1: does the model get it wrong unprompted?** That needs only arm 1.
A control arm alone answers it, because the question is about the model's unaided default rather
than about any skill's effect.

Arms 2 and 3 are secondary and answer two further questions:

- **arm 2 vs arm 1** does `core` change anything the control was getting wrong?
- **arm 3 vs arm 2** does adding a second skill help, or does the extra load degrade the rules
  `core` was already delivering? **This is the first composed-install measurement in the project** and the arithmetic predicts it should hurt: `core` at ~10 always-on plus `kotlin` at 4 is well
  past where a rule set is delivered as a set.

## Arms

| Arm | Loaded | Prompt | Output |
|---|---|---|---|
| 1 | nothing | `prompts/arm-1-control.md` | `runs/control.md` |
| 2 | `android/core` | `prompts/arm-2-core.md` | `runs/core.md` |
| 3 | `android/core` + `android/kotlin` | `prompts/arm-3-core-kotlin.md` | `runs/core-kotlin.md` |

The skill arrives inside the prompt, between `<skill>` delimiters, ahead of the task, a fresh
session has no install, and this is what an install puts in context anyway. Arm 3 loads core
first, then kotlin, matching `requires: [android/core]`.

The prompts also tell the model not to mention or quote the skill. Without that, a run narrates
which rules it followed, which makes scoring measure self-report rather than the artefact.

## Why this task

Chosen to trigger as many always-on rules as possible in one run, so three runs resolve test 1
across most of two skills.

| Rule | Triggered by |
|---|---|
| BOUND-1, BOUND-2 | a network source behind a screen |
| STATE-1 | filter + search + scroll position across process death |
| STATE-2 | a date and a status shown to the user |
| STATE-3 | failure states on load |
| STATE-4 | the search field, typed into |
| DATA-1 | remote data outliving the screen |
| DATA-2 | order totals, money |
| DATA-3 | JSON that may not parse |
| DATA-4 | sign-out, including server-initiated |
| WORK-1, WORK-2 | load, filter, cancel on re-query |
| SEC-3 | logging around auth failure |
| L10N-1 | dates and totals |
| L10N-2 | order status arriving as a server enum |
| A11Y-1, A11Y-2 | rows, filter chips, a search field |
| ASYNC-1..5 | repository suspend functions, search re-query, shared flow |
| TYPE-1..3 | a UiState with a list in it |
| SER-1 | JSON deserialization |

Not triggered, and therefore not measured by this run: BOUND-3, SEC-1, SEC-2.

The task deliberately never uses the project's vocabulary. It does not say "process death"
"single source of truth", "hoist", "minor units", or "localized formatter". A task that names the
rule measures reading comprehension, not the default.

## Protocol

- **Each arm run 3 times** where budget allows, 9 runs total. If only three runs are possible
  **spend all three on arm 1**: test 1 is the question that gates everything else, and arms 2 and
  3 mean nothing until it is answered.
- Fresh session per run. No project context, no `CLAUDE.md`, no installed skills.
- The task text is pasted verbatim from `TASK.md`. No follow-ups, no clarifying answers. If the
  model asks a question, the run ends and is recorded as it stands.
- Output stored unedited as `runs/<arm>-<n>.md`. Never edited afterwards, a fixed extraction
  script must be re-run over the artefacts it already produced, not applied only to new ones.
- Scoring into `SCORES.tsv`: one row per rule per run, `satisfied` / `violated` / `not-exercised`.
- `not-exercised` is a real outcome and is not evidence either way.

## Reading the result

- **3/3 satisfied** → the model already does it. The rule is deleted, whatever the corpus says.
- **0/3 or 1/3** → the rule is admitted, pending tests 2, 3 and 4.
- **2/3** → not a separation at n=3. Recorded as unresolved; it does not ship on this evidence.

`EVAL-PLAN.md` in both drafts records a prediction per rule, written before this run. Predictions
are scored too. If the three `likely fails`, BOUND-1, A11Y-1, A11Y-2, survive, the checkpoint's
central finding is wrong and the corpus was the better guide.

## Limits, stated rather than hedged

One task. One model. Three runs. No error bars. This resolves test 1 for the rules the task
happens to exercise and nothing else. It is not a win rate and must never be quoted as one.
