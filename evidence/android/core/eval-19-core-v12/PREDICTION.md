# Eval 19, pre-registered prediction

`core` v1.2.0. Four rules added without evidence: `WORK-3` and `BUILD-1`–`BUILD-3`.
Two arms only, control and `+core`, because `core` is the skill under test.

**`BUILD-1` (shrink code and resources), most likely to separate.** Both are off by default, an
empty `release` block is what every tutorial shows, and the task never says the word. Prediction:
control near 0, `+core` high.

**`WORK-3` (main thread), unknown, and the reason this eval exists.** Its only prior evidence is
`OFF-MAIN` scoring 6/6 in an *Opus* control in eval 01. The seed removes the usual scaffolding, no ViewModel, no scope, a store documented as synchronous, so if the models carry it, they carry
it unprompted. Prediction: Sonnet satisfied in control, Haiku the open question.

**`BUILD-3` (KSP over KAPT), probably satisfied unaided.** Room's own documentation leads with KSP
and has for years. Corpus-saturated, and saturation has been an anti-signal every time.

**`BUILD-2` (`implementation` over `api`), probably satisfied unaided in the direction that
matters.** Models default to `implementation` when adding a dependency. The interesting question is
whether anything *fixes* the existing `api(...)` declarations in `:core-data`, and I expect not, in
either arm, the skill says new code, and those lines are not new.

**Falsification:** if `BUILD-1` does not move, all four rules came from a corpus bucket rather than
a model failure and the build section should be cut rather than kept as unmeasured.
