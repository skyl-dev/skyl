# Evidence: `android/core`

Two evals. Everything here is the input to a run or the write-up of one, so it can be replayed and
disagreed with.

| file | what it is |
|---|---|
| `TASK*.md` | the task, verbatim, with a note on which rules it tempts |
| `PREDICTION*.md` | written **before** scoring, including what would falsify the skill |
| `prompts/` | exactly what each arm received. Verbatim, never edited. |
| `seed/` | the starting project, with the situation already in it |
| `RESULTS.md` | what happened, including what did not work |
| `*check.py` | the scoring code |

**The prompts are the record.** `arm-1` is the control and contains only the task. `arm-2` adds the
family core. `arm-3` adds the skill under test. Reading them side by side is the fastest way to see
what was actually varied.

## eval-01

The first eval, and the one that established the arms. Opus 5, n=6 per arm.

Its `PREDICTION-core.md` is a per-rule prediction recorded before any run: `likely holds` meant an
unaided control was expected to get it wrong, `likely fails` meant the rule was expected to be
deleted. Written that way so the result could contradict it rather than confirm whatever turned up.

## eval-19-core-v12

Four rules added later, measured. One survived as written, one was retired, one was cut as
untestable, and one is kept while recorded as **not landing**.

`WORK-3`, the main-thread rule, is the interesting one: the Haiku control calls a filesystem read
and a SHA-256 straight out of a click handler in both runs, so the rule names a real failure, and
the skill fixes it in only one of two runs. That is published as a rule that does not reliably land
rather than as a win.

`PREDICTION.md` for this eval named a falsifier and the result partly met it. The reasoning for
departing from it is in `RESULTS.md`, so the departure is visible rather than silent.
