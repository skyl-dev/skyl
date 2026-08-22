# Evidence: `android/xml`

The View system: adapters and lists, the seam where Compose is hosted inside a View hierarchy, and
the layout and resource decisions that break at runtime rather than at compile time.

## What was run

**1 eval, 36 recorded runs**, on Haiku 4.5 and Sonnet 5. Every run is archived: the generated
sources, the prompt each arm received, and the model each one reported.

Control against `+core` against `+core+xml`.

## What loading the skill changed

Five rules improved. Two of them on both models with every run moving the same way: how a list
adapter is built, and how its items are identified. Two more improved on one model each and were
already handled by the other. One covers hosting Compose inside a Fragment, where the default
disposal point keeps a composition alive on the back stack.

## The finding this skill demonstrates

**Four of the five rules that improved have no support anywhere in the 3,845-file corpus this family
was drafted from.** They were found by running a control arm rather than by reading what others had
written down.

In the same file, the two rules that *are* well documented elsewhere are satisfied by every arm
including the controls. Within one skill, the rules drawn from measurement were the entire effect and
the rules drawn from the corpus were already known to the models.
