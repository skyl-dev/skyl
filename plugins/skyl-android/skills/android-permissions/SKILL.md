---
name: android-permissions
description: "Runtime permissions: whether to ask at all, how to ask, and what the app does with every answer including the silent ones. Use when the app touches the camera, location, microphone, files or notifications."
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
