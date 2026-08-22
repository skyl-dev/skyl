# android/core v0.1.0-draft, what is claimed, and what is not

> Moved here from `drafts/android/core/EVAL-PLAN.md` on 22-Aug-2026 when the drafts
> folder was cleared. It is a **pre-registered prediction** written before the rules were
> measured, and so belongs with the eval rather than with the superseded draft.


Every rule in this draft is `test 1: UNKNOWN`. Nothing here has been in front of a control arm.
This file records a **prediction per rule before measuring** so the defect run can falsify it
rather than confirm whatever we find.

## Predictions

`likely holds` = I expect an unaided control to get this wrong.
`likely fails` = I expect the control to already do it, in which case the rule is deleted.

| Rule | Prediction | Corpus repos | Basis |
|---|---|---:|---|
| STATE-3 UI never claims what the code does not do | **likely holds** | 0 | no corpus support; models write "Saved" for local-only writes |
| DATA-2 money as minor units | **likely holds** | 25 | models reach for `Double` on prices |
| DATA-3 parse failure is absent, not defaulted | **likely holds** | 3 | `?: 0` is a reflex |
| DATA-4 destroy account data at session end | **likely holds** | 8 | rarely considered unprompted |
| WORK-1 durability vs. a longer scope | **likely holds** | | models use a screen scope for uploads |
| STATE-2 format at display | **likely holds** | 0 | no corpus support; untested |
| L10N-1 platform localized formatters | **likely holds** | 3 | `SimpleDateFormat` patterns are the default reach |
| L10N-2 never render a token or enum | **likely holds** | 0 | no corpus support |
| SEC-1 nothing in the binary is secret | uncertain | 17 | models hardcode keys in samples but often add a comment |
| BOUND-2 layer owns its types | uncertain | 3 | done when asked, skipped when not |
| BOUND-3 add a layer at the second consumer | uncertain | 1 | this is restraint, which is measured by negative cases |
| STATE-1 process death / SavedStateHandle | uncertain | 47 | most-corroborated claim in the corpus, which is a warning sign |
| DATA-1 one source of truth | uncertain | | |
| SEC-2 exported components are hostile input | uncertain | 17 | |
| SEC-3 no user data in release logs | uncertain | 30 | |
| WORK-2 cancellation is a decision | uncertain | | core half of a cluster the corpus files under kotlin |
| BOUND-1 dependencies point one way | **likely fails** | 30 | high corpus rank; models lay out layers correctly unprompted |
| A11Y-1 labels | **likely fails** | 36 | high corpus rank |
| A11Y-2 targets and contrast | **likely fails** | 26 | high corpus rank |

Eight `likely holds`, eight `uncertain`, three `likely fails`. If the three `likely fails` survive
a control, the checkpoint's Finding 1 is wrong and the corpus is a better guide than measured.

## Known problem: simultaneous applicability

A plain "build a screen that loads and displays remote data" task triggers roughly **ten** of the
nineteen rules at once: BOUND-1, BOUND-2, STATE-1, STATE-2, DATA-1, DATA-3, WORK-1, L10N-1
A11Y-1, A11Y-2.

Measured adherence collapses from 0.96 to 0.01 as simultaneously applicable rules go 1 → 6, so at
ten the set is delivered as a sample, not a set. This is the real ceiling on the draft, and it is
not fixable by editing prose.

Rules whose situation arises rarely are cheap, DATA-2 (money), DATA-4 (accounts), SEC-2 (exported
components), L10N-2 (server enums) fire on a minority of tasks. The expensive ones are the always-on
group, and that group is where the deletions have to come from.

**The defect run's first job is therefore not to validate all nineteen, it is to delete enough of
the always-on group that the rest can be followed.**

## Order for the defect run

1. **BOUND-1, A11Y-1, A11Y-2** the three `likely fails`, all always-on. Deleting them buys the
   most headroom for the least loss, and they are the cheapest predictions to falsify.
2. **STATE-1** 47 repos, the corpus's strongest consensus, and always-on. The single most
   valuable measurement in the set.
3. **STATE-3, STATE-2, L10N-2** the three with zero corpus support. Invented, or genuinely
   novel? One run answers a question that has been open since the trashed skill.
4. **DATA-2, DATA-3, DATA-4, WORK-1** the `likely holds` group, cheap because they fire rarely.

## What this draft does not have

- No measurement of any kind.
- No `Why` / `Pitfalls` sections for the human layer. The reason clauses are inline and terse;
  the teaching half is not written. `DEFINITION.md` calls the reason clause "the half that
  teaches the human", inline clauses are the minimum, not the deliverable.
- `references/process-death.md` and `references/money.md` are referenced and not yet written.
