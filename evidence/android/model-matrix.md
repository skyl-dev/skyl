# The model matrix

Same task, same prompts, same isolated settings, fresh session each time. `ctrl` is unaided.

## Across models

Opus n=6 per arm, Sonnet and Haiku n=2 per arm.

| rule | Opus ctrl | Sonnet ctrl | Haiku ctrl | Sonnet +core | Haiku +core |
|---|---|---|---|---|---|
| `STATE-1` save what rebuilds the screen | **6/6** | 0/2 | 0/2 | **2/2** | **2/2** |
| `DATA-2` money as minor units | 5/6 | 1/2 | 0/2 | **2/2** | **2/2** |
| `DATA-4` destroy account data on sign-out | 6/6 | 1/2 | 0/2 | **2/2** | 1/2 |
| `ASYNC-2` re-raise cancellation | 6/6 | 0/2 | 0/2 | 1/2 | 0/2 |
| `ASYNC-5` make a shared flow hot | 6/6 | 2/2 | 0/2 | 2/2 | **2/2** |
| `L10N-1` localized formatters | 6/6 | 2/2 | 1/2 | 2/2 | **2/2** |
| `A11Y-1` label every control | 6/6 | 2/2 | 2/2 | 2/2 | 2/2 |
| `STATE-4` input owned by the control | **0/6 → 6/6** | 0/2 → 1/2 | 0/2 → 0/2 | | |

**Capability is the variable, and it is monotonic.** Opus satisfies almost everything unaided.
Sonnet drops three. Haiku drops nearly all of them. The rules did not change; the model did.

**The skill closes the gap it was written for**, and only below the frontier. Every rule Sonnet or
Haiku fails unaided is fixed by loading the core skill.

**`STATE-1` is the rule a frontier-only eval would have deleted.** 6/6 unaided on Opus, top of every
corpus ranking, and needed by two of the three models tested.

**`STATE-4` inverts.** It is the only rule that separated on the frontier, and it is the one a small
model cannot act on even when told. A rule earns its slot inside a window bounded at both ends.

## The bridge

The same model through two harnesses, so a difference is attributable to the harness rather than the
model. `opencode` 1.17.11 with `openrouter/anthropic/claude-haiku-4.5`, against the `claude` CLI with
the same model. Served model confirmed on both arms.

| rule | CLI ctrl | CLI +core | opencode ctrl | opencode +core | replicates |
|---|---|---|---|---|---|
| `STATE-1` | 0/2 | **2/2** | no | **yes** | **yes** |
| `DATA-2` | 0/2 | **2/2** | no, used `Double` | **yes** | **yes** |
| `L10N-1` | 1/2 | 2/2 | yes | yes | yes |
| `ASYNC-5` | 0/2 | 2/2 | no | no | **no** |
| `ASYNC-2` | 0/2 | 0/2 | no | no | yes, both fail |
| `STATE-4` | 0/2 | 0/2 | no | no | yes, both fail |
| `DATA-4` | 0/2 | 1/2 | yes | no | inverted |
| `A11Y-1` | 2/2 | 2/2 | yes | **no** | degraded |

**The two clearest effects survive a harness change.** The two rules with the largest measured
uplift replicate exactly. The weaker ones do not, and two of them go the wrong way.

That is the honest reading: a large effect is portable, a marginal one is not evidence of anything
outside the harness it was measured in.

## A non-Anthropic model, in a non-Claude harness

`opencode --pure` with `openrouter/qwen/qwen3.7-max`. n=1 per arm, $0.48 total.

| rule | control | +core |
|---|---|---|
| `STATE-1` | no | **yes** |
| `DATA-2` | no, used `Double` | **yes**, wrote a money type |
| `ASYNC-5` | no | **yes** |
| `STATE-4` | no | **yes** |
| `DATA-4` | yes | yes |
| `L10N-1` | yes | yes |
| `A11Y-1` | yes | yes |
| `ASYNC-2` | no | no |

n=1 per arm, so this is a smoke test rather than a measurement. What it establishes is narrow and
worth having: the skills are not shaped to one vendor's model or one vendor's harness, and four rules
moved on a model from a different family entirely.
