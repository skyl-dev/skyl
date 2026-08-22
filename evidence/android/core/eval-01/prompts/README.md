# How to run eval 01

The three `arm-*.txt` files contain **only** the prompt. Select all, copy, paste, stop.
Nothing in them names this project, the eval, or the arm — a run that knows it is being measured
is not measuring a default.

| File | Loaded | Bring the reply back as |
|---|---|---|
| `arm-1.txt` | nothing | `runs/arm-1-<n>.md` |
| `arm-2.txt` | `android/core` | `runs/arm-2-<n>.md` |
| `arm-3.txt` | `android/core` + `android/kotlin` | `runs/arm-3-<n>.md` |

`<n>` is the run number: `arm-1-1.md`, `arm-1-2.md`, `arm-1-3.md`.

## Rules for the run

- **Fresh session every time.** New conversation, no project open, no skills installed, no
  CLAUDE.md in context. Run them wherever you like — the working folder does not matter, only
  that it carries none of this project's files.
- **Paste and stop.** No follow-ups, no clarifications. If it asks a question, do not answer —
  end the run and keep what it produced. That is a valid outcome.
- **Save the whole reply, unedited.** Including any prose around the code. Do not trim, reformat,
  or fix anything. Four transcription bugs in the previous round came from tidying artefacts
  after the fact.

## If the budget is tight

Spend everything on `arm-1`. Test 1 — does the model get it wrong unprompted — gates every other
question, and arms 2 and 3 mean nothing until it is answered.

## Regenerating

These files were generated from `the skill as it stood at the time` as it stood at the time, taking only the `## Rules` section to
match `agent_sections: [rules]`. If a draft changes, regenerate. Never hand-edit them, or an arm
stops matching the skill it claims to test.

> The `drafts/` folder was cleared on 22-Aug-2026 once every skill had shipped, so those source
> files no longer exist. The prompts here are the record of what was actually put in front of
> each arm, which is the thing that matters; `git log` holds the drafts they came from.
