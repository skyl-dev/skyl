## What this changes

<!-- One line. -->

## If this adds or edits a rule, answer all five

**Which control run gets this wrong?**
<!-- Model, task, output. No skill loaded. "Best practice" is not an answer. -->

**Would 900 of 1000 projects hit it?**

**Does a linter or the compiler already catch it?**

**Is it checkable at every token?**
<!-- If it defers an action to later, it is not a rule. There are no checklists here. -->

**What does it overlap?**
<!-- Name any rule it touches, here or in another skill. If it restates one, one of them goes. -->

## If this retires a rule

- [ ] The evidence is a control run, not a judgement
- [ ] The id is listed in `retired:` and **not reused**
- [ ] `## Provenance` says why

## Checks

- [ ] `scripts/validate.py` passes
- [ ] `scripts/leakcheck.sh` passes, no eval-speak inside installable sections
- [ ] `scripts/xrefcheck.py` passes, every cross-skill reference resolves
- [ ] `## Provenance` reports what did **not** work, not only what did
