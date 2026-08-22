# Evidence: `android/security`

Keeping a secret on a device you do not control, and the surfaces where data leaves the app.

## What was run

Two evals on Haiku 4.5 and Sonnet 5, one of them testing what happens when this skill and
`android/db` are loaded together.

## Where a secret actually goes

Storing a session token is where this skill earns its place. Across twelve unaided runs, **five used
a deprecated crypto wrapper and seven stored the token with no encryption at all.** One used the
platform keystore directly.

With the skill loaded, keystore-backed encryption appears in **every run**, against **none** of the
controls.

The rule states the alternative directly rather than deferring to the storage skill, because an app
that stores only a token has no database and would never load that skill at all.

## What loading the skill changed

**Declaring what is copied off the device.** Auto Backup is on by default, so a ninety-day refresh
token written to preferences reaches a backup server and the user's next phone without anyone
choosing that. Improved on Haiku.

## Loading two skills together

The same eval measured what happens when this skill is loaded alongside `android/db`, which carried
an overlapping rule. On Haiku, the behaviour that appeared reliably with `security` alone **stopped
appearing** when both were loaded: the extra rule count displaced the one that mattered, on the model
least able to absorb it. Sonnet was unaffected. The overlapping rule in `db` was reduced to a pointer.

## The skill knows when not to fire

One task deliberately included a case where a rule must **not** apply: sharing a document to an app
of the user's choosing, which is a legitimate implicit intent. Every run kept the share sheet, in
every arm. The skill did not turn a correct pattern into a defect.
