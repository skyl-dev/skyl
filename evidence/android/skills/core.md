# Evidence: `android/core`

Architecture and platform decisions that apply to every Android project: where state lives, what
survives process death, what the UI is allowed to claim, and what leaves the app.

## What was run

Four evals, on Opus 5, Sonnet 5, Haiku 4.5 and qwen3.7-max, through two harnesses and two providers.
Control arms had no skill loaded; treated arms had `core`. See the
[model matrix](../model-matrix.md).

## What loading the skill changed

**Saving what rebuilds a screen after process death.** The two mid-tier models tested did not do this
unaided and did it consistently once the skill was loaded. The strongest model tested already did it,
which is the clearest example in this family of a rule that a frontier-only evaluation would have
thrown away.

**Money as minor units with its currency, rather than a floating point number.** Improved on every
model that did not already do it, and reproduced through a second harness and on a non-Anthropic
model.

**Formatting money and dates through the platform's localized formatters.** Given a multi-currency
total, unaided runs hardcoded the symbol, hardcoded a divisor of one hundred, and put the symbol
where an English locale expects it. Loaded runs used the platform formatter and took the exponent
from the currency.

**Mapping server enums before they reach a screen.** Unaided runs rendered the raw value.

**Destroying account-scoped data when a session ends.** Improved on the smaller models.

## What the tested models already handle

Layer direction, one source of truth, keeping durable work out of a broadcast receiver, and putting
user-facing text in resources were all done unaided in nearly every run. Those rules cost little and
stay for models that do not.

## Where the skill did not change behaviour

A receiver declared with an intent filter and no explicit `exported` attribute stayed that way in
every run of one eval, loaded or not, and its extras went unvalidated. Stated and not acted on.
