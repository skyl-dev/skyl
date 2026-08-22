# Contributing

The bar here is unusual, so read this before opening a PR.

**A rule is not admitted because it is true.** Most published skill content is true. It is admitted
because a model **gets it wrong without being told** and that has to be shown, not asserted.

## The fastest way to contribute: falsify a rule

Every rule in this registry is a claim that a model fails without it. That claim is falsifiable, and
falsifying it is the single most valuable contribution you can make.

If you can show a **control run** no skill loaded, where the model already does what a rule says
that rule is a candidate for retirement. Open a
[challenge](../../issues/new?template=challenge-a-rule.yml) with the task, the model, and the
output. 17 rules have been removed exactly this way.

This matters more over time, not less: as models improve, rules expire. A registry nobody can
falsify becomes wrong quietly.

## Proposing a skill

New skills land in `incubating/` first. To move to `skills/`, a skill needs:

1. Every rule passing the [four admission tests](./spec/ADMISSION.md)
2. The [format](./spec/FORMAT.md): decidable instruction, `Why`, `Not when`, stable ids
3. An eval: control / +core / +skill, at least two models, at least two runs per cell
4. Results written into `## Provenance`, including what did **not** work

Point 4 is not optional and not a formality. A skill whose provenance reports only successes will be
sent back.

## Proposing a rule for an existing skill

Open a PR against the skill and answer, in the PR body:

- **Which control run gets this wrong?** Model, task, and the output.
- **Would 900 of 1000 projects hit it?**
- **Does a linter already catch it?**
- **Is it checkable at every token** or is it an action deferred to later? Deferred actions are not
  rules and there are no checklists here.
- **Which existing rule does it overlap?** If it restates one, in this skill or another, one of
  them has to go. Two skills carrying one hazard measurably degrades the smaller model.

## Reporting a reversal

Platform facts go stale, and a wrong rule is worse than a missing one. If a rule cites behaviour
that has changed, an API deprecated, a default inverted, a limit introduced, open a
[reversal](../../issues/new?template=report-a-reversal.yml) with the primary source.

Four reversals have been caught this way already, including one where the recommended setting had
been inverted by a major version and the advice now asked for a state that was already the default.

## What gets rejected

- A rule that reads correctly and cannot be checked. "Use flows appropriately" is not a rule.
- A restatement of the library's own documentation. If the docs say it, the model has it.
- A checklist, or any rule that defers an action.
- A rule with no stated boundary. Without a `Not when` it will be applied everywhere.
- Anything whose evidence is "this is best practice".

## Style

Skills are written for two readers at once: an agent that will follow them literally, and a human
deciding whether to trust them. Write plainly, name the failure rather than the principle, and
prefer the standard-library answer over the clever one, a technique harder to maintain than the
problem it solves is a bug in the skill.

## Local checks

```
scripts/validate.py      frontmatter, rule shape, id stability
scripts/leakcheck.sh     no eval-speak inside installable sections
scripts/xrefcheck.py     every cross-skill rule reference resolves
```

CI runs all three on every PR.
