# Evidence: `android/mvvm`

The boundary between a state holder and the data behind it: what a ViewModel owns, and where a
repository interface is declared.

## What was run

**2 evals, 30 recorded runs**, on Haiku 4.5 and Sonnet 5. Every run is archived: the generated
sources, the prompt each arm received, and the model each one reported.

Two different tasks.

## What loading the skill changed

**Declaring the repository interface where it is used rather than where it is implemented.** This is
the only result in the family that reproduced across two separate tasks, on both models.

**Choosing between a local and a remote origin in one place**, once a task supplied two origins for
the same data.

That second one is why task design gets its own section in how these are run. The first eval reported
it dead: that task had a single data origin, so there was nothing for the rule to act on.

## What the tested models already handle

One rule was satisfied in every arm on both tasks and was dropped.

## What the corpus said

The claim register called this skill a null: 31 high-worth claims, 5 evidenced, every one contested,
and a summary saying it had no content of its own. The measurement disagreed.
