# The admission bar

A rule ships only if it passes all four tests, **in order**.

## 1. Does the model get this wrong unprompted?

The first test, and the one that outranks correctness. A rule the model already follows costs
context and displaces one that would have worked.

This is decided by running the task with **no skill loaded** and reading what comes out. Not by
judgement, and not by how important the rule feels.

17 rules have been retired against this test. Some were rules we were confident about, the
in-context permission-timing rule is the most-repeated advice in the entire permissions corpus, and
zero of twelve control runs got it wrong.

## 2. Does a linter or the compiler already catch it?

Most of a style guide is already a compiler error, a lint warning, or something the formatter fixes.
A published survey of agent context files found 62% carrying rules a linter already enforces
occupying context for nothing.

## 3. Would 900 of 1000 projects hit it?

Not 1 in 1000. Interesting is not the bar.

**How not to score this test:** by asking whether the situation is *possible*. Almost anything is
possible. Ask whether a project that never thinks about this ships the bug, and whether the person
writing the code would recognise it.

## 4. Is it checkable at every token, or a deferred action?

Constraints that describe a property of the artifact hold under load. Constraints that defer an
action to a later moment drop sharply, while fully visible in context the whole time.

```
GOOD  (a property of the artifact)
  Money is a 64-bit integer of minor units plus a currency code, never a float.

BAD   (an action deferred to later)
  Remember to add a migration when you change the schema.
```

Both are true. Only the first is a rule. **No skill in this registry carries a checklist** because
a deferred action stated as a rule is dropped at exactly the moment it matters.

---

## A rule lives in a capability window

A rule earns its slot **between two bounds**. Above the window the model already does it; below the
window the model cannot act on it even when told.

Both bounds are real and measured:

| rule | Opus | Sonnet | Haiku |
|---|---|---|---|
| `core STATE-1` save state for process death | 6/6 unaided | 0/2 → 2/2 | 0/2 → 2/2 |
| `core STATE-4` input owned by the control | 0/6 → 6/6 | 0/2 → 1/2 | 0/2 → **0/2** |

`STATE-1` is the rule that curating against the frontier alone would have deleted: the strongest
model does not need it, and two of three do. `STATE-4` is the inverse, it separates only on the
model capable of acting on it.

**So a rule is not admitted or retired globally.** It is admitted for a window, and the registry
records which models were tested.

## Corpus support is an anti-signal

The material a rule could be drawn from and the material the model was trained on are the same
material. The more repositories document a practice, the more likely the model already follows it.

Measured repeatedly, including *within* a single skill: the rules with zero corpus support were the
entire measured effect, while the corpus-backed rules in the same file were satisfied by every arm.
Across six axes, register size has predicted result thinness rather than richness, the largest
register in the project (238 claims) produced the smallest skill (3 rules).

**Every confirmed result here came from a control arm or a primary source. None came from corpus
frequency.**

## Statuses

A rule in this registry carries one of five statuses in the [rule ledger](../evidence/rules.md):

| status | meaning |
|---|---|
| `measured` | separated in a control/treatment comparison |
| `retired` | removed, a control arm did it unprompted |
| `candidate` | a control arm satisfied it and **it is still shipping**. A retirement not yet actioned. |
| `not-landing` | the model gets it wrong **and** the rule does not fix it. Kept, and said so. |
| `unmeasured` | no task reached it |
| `null` | the whole skill was measured and nothing separated |

`not-landing`, `candidate` and `null` are published deliberately.

`candidate` is the uncomfortable one and that is the point: it is a rule our own bar says should be
removed, still present, in public, with the measurement attached. A registry that only reports its
wins is not reporting, and one that hides its own backlog is worse.
