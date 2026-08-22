# Across models, harnesses and providers

Skills here are written for whatever model a project uses. Three things were varied deliberately to
check that the results are not an artifact of one setup.

## Models

Opus 5, Sonnet 5, Haiku 4.5 and qwen3.7-max, on the same task with the same prompts and the same
isolated settings.

**Capability is the variable, and it moves in one direction.** The strongest model tested satisfies
almost everything unaided. The mid-tier model drops a few. The smallest drops most of them. The rules
did not change; the model did.

**The skill closes the gap it was written for, and only below the frontier.** Nearly everything the
smaller models miss unaided is handled once the skill is loaded, and on the strongest model most
rules make no difference because it already does them.

**Two rules mark the two ends of that window.** One is satisfied unaided by the strongest model and
missed by both others, which is the rule a frontier-only evaluation would have deleted. Another is
the reverse: it only improves on the strongest model, because a smaller one cannot act on it even
when told.

That is why nothing here is curated against one model.

## Harnesses

The same model, `anthropic/claude-haiku-4.5`, run through both the `claude` CLI and `opencode`
1.17.11, with the served model confirmed on both arms. Running a different model in a different
harness moves two variables at once and measures neither.

**The largest effects survive the harness change.** The two rules with the clearest improvement
reproduce exactly. Smaller effects do not, and two of them move the other way.

That is the honest reading: a large effect is portable, and a marginal one is not evidence of
anything outside the harness it was measured in.

## Providers

Anthropic directly, and both the same and different models through OpenRouter, including
`qwen3.7-max` on a non-Anthropic model in a non-Claude harness.

That last run is a smoke test rather than a measurement, at one run per arm. What it establishes is
narrow and worth having: several rules improved on a model from a different family entirely, so the
skills are not shaped to one vendor's model or one vendor's tooling.
