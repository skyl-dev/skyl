---
name: android/permissions
axis: topic
family: android
requires: [android/core]
version: 1.0.0
authors: [ahmmedrejowan]
agent_sections: [rules]
retired: [ASK-3]
detect:
 manifest_element: ["uses-permission"]
---

## Rules

Runtime permissions: whether to take one at all, how to ask, and what the app does with the answer.
`core` owns that an exported component treats its input as hostile (`SEC-2`). `compose` owns that a
launcher is not invoked from composition (`EFFECT-1`). `images` owns what a picker hands back
(`USER-1`). This owns the decision and the denial.

**The first question is always whether the permission is needed.** Most of what apps ask for has a
permission-free path that ships the same feature, and that path is usually newer than the code being
copied. See `references/alternatives.md` before declaring anything.

**Scope.** New permissions, new requests, and the code that reads the result. An existing granted
permission that the app genuinely uses is not a defect.

**When not to apply**(whole-skill): an app that declares no `uses-permission` beyond `INTERNET`.

**Priority.** `must`, the failure crashes, blocks the user, or ships a permission the app did not
need. `should`, real exceptions exist; name yours.

### Whether to ask at all

- **ASK-1** `must`: A permission is the last resort. Before declaring one, check whether a system
 picker or a system intent delivers the same outcome with no permission at all, picking photos
 picking files, picking a contact, taking a photo, scanning a code, and getting one precise location
 all have permission-free paths.
 *Why:* the permission-free path is not a workaround; it is the supported answer, and it is better
 on every axis, no dialog, no denial state, no rationale UI, no degraded mode to build and test
 no store declaration, and nothing to lose when the platform tightens the rule next year. Most
 permission code in the wild exists because the API that removed the need for it shipped after the
 pattern was learned. See `references/alternatives.md`.
 **Having taken the permission-free path, do not also declare the permission it replaced.** Using
 the photo picker *and* declaring a media permission is not caution, it is the permission, with
 all of its cost, plus a picker. The declaration is what the platform and the store see.
 *Not when:* the app genuinely needs the whole surface, a gallery app that must enumerate every
 photo, a camera app with a custom viewfinder. Then the permission is correct and the reason is
 worth writing down.

- **ASK-2** `must`: Do not declare a permission the app does not request. A declaration is not
 free: declaring `CAMERA` makes `ACTION_IMAGE_CAPTURE`, which needs no permission, throw
 `SecurityException` until that permission is granted.
 *Why:* the platform assumes a declared permission is one you intend to hold, so declaring it opts
 you into enforcement you did not want. Worse, the manifest you ship is the **merged** one: a
 dependency can add `CAMERA` and break an intent-based flow in code you never touched. Read the
 merged manifest, not the file you wrote.
 There are two fixes and they are not equal. **Remove the declaration** that is the fix, because
 the flow never needed the permission. Requesting it is the fallback, and only correct when the app
 genuinely uses the permission's own API rather than the intent.
 *Not when:* never, an unrequested declaration is either a bug or an unremoved leftover.

- **LEAST-1** `must`: When a permission is genuinely needed, request the **weakest form** of it that
 serves the feature. Coarse location rather than fine, foreground rather than background, a single
 media type rather than all of them.
 *Why:* the strength you ask for is a separate decision from whether you ask, and it is the one
 people skip, a list of nearby places sorted by distance works perfectly on a neighbourhood-level
 fix, and asking for fine location to do it costs a scarier dialog, a higher refusal rate, and a
 store declaration you did not need. Ask for precision only where losing it breaks the feature.
 *Not when:* the feature genuinely needs the stronger form, turn-by-turn navigation needs fine
 location, and then it says which and why.

### Asking

- **ASK-4** `must`: `shouldShowRequestPermissionRationale()` returning `false` does **not** mean
 permanently denied. It is also `false` before the permission has ever been requested. Record that
 the app has asked, and use that to tell the two apart.
 *Why:* the two states need opposite UI. Treating the never-asked case as permanent denial sends a
 first-time user to a Settings screen to enable something the app never offered them, a dead end
 that looks like a broken app. The system distinguishes them internally (`USER_SET` after one
 denial, `USER_FIXED` after two); the public API does not.
 *Not when:* never. There is no API that answers this on its own.

### The answer

- **GRANT-1** `must`: Re-read permission state when the screen becomes visible again, not only in
 response to a request.
 *Why:* a grant made anywhere other than your own dialog produces no callback. Send the user to
 Settings, have them grant, and let them come back, and the screen that is waiting on a result it
 asked for will wait forever. The state is read from the system at the point of use; it is not a
 value the screen computed once and owns.
 *Not when:* a permission the screen never reads.

- **GRANT-2** `must`: A denial has a defined product path: the feature degrades to something that
 still works, or the UI says plainly what is unavailable and offers the one recovery that exists.
 Never re-prompt in a loop.
 *Why:* after the second denial the system dialog no longer appears at all, so a re-request is a
 no-op that returns denied instantly, which reads to the code as another denial and, in a loop
 as a frozen screen. The user has already answered; the only remaining path is Settings, and only
 if the feature is worth the trip.
 *Not when:* the app is unusable without the permission, and then it says so once rather than
 asking again.

- **GRANT-3** `should`: A partial grant is its own state, not a denial. Coarse location where fine
 was requested, and a user-selected subset of photos, both mean *granted, with less*.
 *Why:* modelling permission as a boolean turns "the user gave you what they were comfortable with"
 into "no", so the app disables a feature the user just enabled. Coarse location still places
 someone in a neighbourhood, and a selected subset is exactly the photos they meant to share.
 *Not when:* the feature genuinely cannot work at the reduced level, turn-by-turn navigation on
 coarse location, and then it says which one it needs and why.
 *(This state only ever arises if `LEAST-1` was followed. Request fine location alone and the user
 never gets the chance to grant less, so there is no partial grant to handle.)*

### What ships

- **DECL-1** `must`: Every permission in the merged manifest is one the app can justify, including
 the ones a dependency added.
 *Why:* the merged manifest is what the user sees on the store listing and what the platform
 enforces; "a library added it" is not a distinction anyone outside the codebase can make. An
 unexplained sensitive permission is also a review rejection, and the ones that arrive by merge are
 the ones nobody remembers.
 *Not when:* a permission a dependency genuinely needs on a path the app uses, and then it is a
 permission the app took, and it is documented as such.

## Why

<!-- human-only: not installed -->

**Why the first question is whether to ask at all.** Almost everything an app asks for has a
permission-free path now, and that path arrived after the pattern most code copies was learned. The
permission-free version is better on every axis at once: no dialog, no denial state, no rationale
screen, no degraded mode to build and test, nothing on the store listing to justify, and nothing to
rewrite when the platform tightens the rule next year. A permission is not a feature you turn on, it is a liability you take on, and most of the time you can decline it and ship the same thing.

This is also the one part of permissions work that cannot be fixed later. Everything else, the
timing, the rationale, the denial path, is code you can improve. The decision to take a permission
propagates into the manifest, the store listing, the review process, and every user's mental model
of your app.

**Why a declaration you never use is not harmless.** This is the trap that surprises people. The
platform treats a declared permission as a statement of intent and enforces it: declare `CAMERA`
never request it, and `ACTION_IMAGE_CAPTURE`, an intent that needs no permission at all, throws.
A line in a file you were not looking at breaks a flow that was correct.

And the manifest that ships is the merged one. A dependency can contribute the declaration, so the
bug can appear in a release where nobody touched the camera code, from an upgrade to a library that
has nothing to do with photos. The manifest you wrote is not the manifest you shipped.

**Why `false` is the ambiguous answer.** `shouldShowRequestPermissionRationale()` returns `false` in
two states that need opposite UI: before the app has ever asked, and after a permanent denial. The
system knows the difference internally, one denial flags `USER_SET`, two flags `USER_FIXED`, and
does not expose it. Treat `false` as "permanently denied" and a first-time user gets sent to a
Settings screen to enable something they were never offered, which reads as a broken app. The only
fix is to remember that you asked; there is no API for it.

After the second denial the system dialog never appears again for the life of the install, so a
re-request returns denied instantly. In a retry loop that is not a second chance, it is a frozen
screen.

**Why a grant made elsewhere is silent.** The permission callback fires for *your* request. A user
who leaves for Settings, grants, and comes back has changed the answer without your code being told
so a screen waiting on the result it asked for waits forever. Permission state is read at the point
of use, not computed once and owned.

**Why a partial grant is not a no.** Coarse instead of fine, or a chosen subset of photos, is the
user granting what they were comfortable granting. Modelling permission as a boolean converts that
into a refusal and disables a feature the user just enabled. A neighbourhood-level location still
sorts a list of nearby stores correctly, and a selected subset is exactly the photos they meant to
share.

## Pitfalls

<!-- human-only: not installed -->

- **`SecurityException` from an intent that needs no permission.** `CAMERA` declared and never
 requested. The declaration may have come from a dependency.
- **A first-time user sent to Settings for a permission never offered.** `false` from
 `shouldShowRequestPermissionRationale()` read as permanent denial.
- **A frozen screen after two denials.** The dialog no longer appears; the re-request returns denied
 instantly and the loop never ends.
- **A user grants in Settings, comes back, and the screen still says denied.** No callback fires for
 a grant made outside your request.
- **A feature disabled after the user allowed it.** A coarse grant, or a photo subset, treated as a
 denial.
- **A store rejection for a permission nobody remembers adding.** It arrived through manifest merge.
- **A version branch around the photo picker that only removes the fallback.** `PickVisualMedia`
 falls back to `ACTION_OPEN_DOCUMENT` on its own.

## Provenance

<!-- human-only: outside agent_sections, never installed -->

**Eval 16: three confirmed movements, and the two models moved on different rules.** `ASK-2` on Haiku
(`0/2 → 2/2`), the unnecessary `CAMERA` declaration removed on Sonnet (`2/2 → 0/2` in the violation
direction), and `GRANT-1` on Sonnet (`0/2 → 2/2`, hand-confirmed, the skill arm wrote the reason
out in a comment while the control had nothing on resume). 24 runs, two brownfield tasks.
See `evals/android/eval-16-permissions/RESULTS.md`.

**The most useful finding is one the table could not see.** Haiku's control ships the exact
`SecurityException` the rule describes. With the skill it fixed the measurement ** by requesting
`CAMERA`** and building a CameraX viewfinder, which satisfies `ASK-2` while violating `ASK-1`.
Sonnet deleted the declaration and kept the intent. `ASK-2` now ranks the two fixes rather than
accepting either.

**Retired:** the in-context timing rule. Zero launch-time requests in **12 of 12** task-B runs, every
arm including both controls, the most-repeated advice in the register and the one thing no model needed
told. **Kept but not landing:** `GRANT-3` (Haiku requests fine location alone in all six runs, with
or without the skill) and the media half of `ASK-1` (Haiku declares a storage permission in all six
while also using the picker). Recorded as *the rule does not land* which is a different finding
from *the model already does it*.

**Two corrections the web pass made before drafting.** Re-checking a permission was going to be
justified by revocation during a run; Android kills the process when it revokes, so that reasoning
is wrong and `GRANT-1` is built on the Settings round-trip instead. And the system location button
is at `1.0.0-alpha01`, so it is marked alpha in the reference rather than offered as the standard
answer.

The register was the largest in the project at 375 rows. As with every axis so far, the saturated
centre contributed nothing that measured.

**two changes, both diagnosed from the eval and both unmeasured.** `GRANT-3` and the media
half of `ASK-1` were recorded as *not landing*; re-reading the runs showed why, and in both cases the
rule was on the wrong side of the request.

Haiku launched `ACCESS_FINE_LOCATION` alone in all six task-B runs, so it never reached a
partial-grant state at all, `GRANT-3` could not fire because nothing upstream asked for less.
`LEAST-1` is that upstream rule. And on task A Haiku used the photo picker *and* declared a storage
permission in all six runs: `ASK-1` said to check for a permission-free path and never said not to
declare the permission anyway, so belt-and-braces satisfied it. `ASK-1` now names that case.

**Both are now measured, and both worked.** Eval 16b re-ran the skill arm against the revised rules with the prediction
written down first. Haiku moved `0/2 → 2/2` on requesting coarse location alone, and every task-A
violation column, media permission declared, `CAMERA` declared, picker-plus-permission, went from
2/2 to **0/2**. Sonnet was already there in both versions.

The comparison carries a stated confound: the two prompts differ by four changes, not two, because
the earlier prompt was generated before the ship-time adjustment. Attribution survives it, `LEAST-1` is the only change that mentions location strength, and nothing but `ASK-1`'s clause
mentions declaring a media permission alongside a picker. See
`evals/android/eval-16b-permissions-v11/RESULTS.md`.
