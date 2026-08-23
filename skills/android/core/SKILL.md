---
name: android/core
axis: core
family: android
requires: []
version: 1.0.0
authors: [ahmmedrejowan]
agent_sections: [rules]
retired: [BUILD-1, BUILD-2]
detect:
  file: ["**/src/main/AndroidManifest.xml"]
  gradle_plugin: ["com.android.application", "com.android.library"]
---

## Rules

Architecture and platform decisions. Nothing here names a language or a UI toolkit, a rule that
would read differently in Kotlin and Java, or in Compose and XML, belongs to that layer instead.
Platform and AndroidX libraries are named where they are the decision: `ViewModel`
`SavedStateHandle`, `WorkManager`.

**Scope.** These describe the shape *new* code takes. Working code in an older idiom is not a
defect. Match the file you are editing, and never open a file solely to bring it into compliance.

**When a rule here conflicts with the code you are editing** the surrounding convention wins for
style and structure, but never for a rule whose failure loses user data, leaks a credential, or
ships a crash. Fix those in their own change, not inside another one.

**When not to apply**(whole-skill): a prototype you will delete, a single-screen utility with no
persistence, or a file whose surrounding code follows a different convention consistently, local
consistency wins. Do not raise any of these in review on code that is not otherwise changing.

**Priority.** `must`, the failure is expensive and hard to reverse. `should`, real exceptions
exist; name yours.

### Boundaries

- **BOUND-1** `must`: Dependencies point one way: ui → domain → data. A file under `data/` never
 imports from `ui/`.
 *Why:* the direction is what makes the data layer testable without a device and reusable by a
 second consumer. A back-edge is invisible until something needs to reuse it.
 *Not when:* a single-module app with one screen, where the layers are folders, not boundaries.

- **BOUND-2** `must`: Each layer's public surface uses types it owns. A third-party SDK's types
 its exceptions, and its error codes stop at the layer that imports the SDK.
 *Why:* a vendor type in a function signature spreads to every caller, and swapping the vendor
 then edits the UI. Vendor exceptions reaching a state holder mean the UI is deciding what an
 HTTP 409 means.
 *Not when:* the type is a platform type (`Uri`, `Bitmap`) rather than a vendor's.

- **BOUND-3** `should`: Add a layer when a second consumer of the same data appears, not before.
 *Why:* on a two-screen app the full stack is ceremony, and ceremony written early is the version
 everyone copies.
 *Not when:* the codebase already has the layer, match it.

### State

- **STATE-1** `must`: Design for process death, not rotation. Save what *rebuilds* the screen, a filter, a query, a scroll position, an id, through `SavedStateHandle`. Never save what
 *fills* it: fetched lists, typed documents, bitmaps.
 *Why:* rotation keeps the process alive, so a screen can pass every rotation test and still lose
 everything when the system reclaims the app in the background. The saved-state bundle is shared
 process-wide and enforced at transaction level, so a large value there fails at stop time, far
 from the code that wrote it.
 *Not when:* the screen holds nothing a user would be annoyed to retype or re-find.
 See `references/process-death.md`.

- **STATE-2** `must`: A displayed value is formatted where it is displayed, never stored
 formatted.
 *Why:* a string built at fetch time freezes the locale, time zone, and 12/24-hour setting that
 were current when it was built, and nothing downstream can sort, total, or re-render it. The bug
 surfaces when the user changes a system setting and the screen does not follow.
 *Not when:* the server owns the presentation and the client is a pass-through display.

- **STATE-3** `must`: The UI never claims something the code does not do. "Saved" for a write that
 only reached the device, "Will retry" with no retry, a spinner with no work behind it.
 *Why:* a user told the work is handled stops acting on it, which turns a recoverable failure into
 a silent loss. This is the one class of defect where the code is working as written and the
 product is still wrong.
 *Not when:* never. If the claim is not yet true, say what is true.

- **STATE-4** `must`: Input the user is actively producing, typed characters, a drag, a scroll
 offset, is owned by the control producing it. Send it onward at a boundary: a pause, a commit
 a submit. Never per event.
 *Why:* routing every event through an asynchronous hop and back drops and reorders them under
 fast input, and for text it breaks composition on predictive, CJK, Indic and gesture keyboards, the users least able to work around it. The control is already the source of truth for a value
 that changes faster than anything downstream consumes it.
 *Not when:* the consumer is synchronous and in-process, filtering a list already in memory has
 no hop to drop events, and adding one is ceremony. Or the consumer genuinely needs every event, a drawing canvas, a gesture recogniser, where the events *are* the data.

### Data

- **DATA-1** `should`: One source of truth per piece of data. Anything that outlives the screen
 that fetched it is read from local storage, and the network writes into that store rather than
 into the UI.
 *Why:* two copies diverge, and the screen that shows the stale one is not the screen with the
 bug. *Not when:* the data is genuinely ephemeral, a live price, a presence indicator, where a
 store adds a staleness problem that did not exist.

- **DATA-2** `must`: Money is an integer of minor units plus its currency code, never a floating
 point number. Take the exponent from the platform's currency data, not from a constant 100.
 *Why:* binary floating point cannot represent most decimal amounts, so totals drift by cents over
 a long enough list. And the exponent belongs to the currency: yen has none, several dinars have
 three, so dividing by 100 renders a ¥1,000 order as ¥10.
 *Not when:* the value is never summed, compared, or displayed as currency.
 See `references/money.md`.

- **DATA-3** `must`: A value that fails to parse is absent, not defaulted. No `?: 0` for an
 unreadable amount, no epoch for an unreadable date.
 *Why:* a default renders wrong data as though it were right, and corrupts anything that sorts
 totals, or filters on it. Absence is recoverable and visible; a zero is neither.
 *Not when:* the default is the domain's genuine identity value and the absence is impossible.

- **DATA-4** `must`: Data scoped to an account is destroyed when that account's session ends
 including the endings the app did not initiate: a revoked token, an account removed in system
 settings. Delete the rows; filtering queries by account id leaves them on disk.
 *Why:* this is the cost of DATA-1. Once a screen reads from local storage, the data outlives the
 session that fetched it, and a device backup or the next unfiltered query still reaches it.
 *Not when:* the app has no concept of an account.

### Work

- **WORK-1** `must`: Every unit of work declares whether it may be abandoned. Work whose result
 only matters to a visible screen dies with the screen. Work that must complete, a write, an
 upload, a purchase, needs **durability** not a longer-lived scope: record the intent in storage
 before starting, and let a scheduler (`WorkManager`) finish it.
 *Why:* a process-wide scope still dies with the process, and nothing runs when the system kills
 one. Cancelling a write because the user navigated away is data loss, and it reproduces only on
 slow networks and low-memory devices.
 *Not when:* the work is a read whose result nobody is waiting for, or the write is already
 idempotent and cheap to repeat on the next launch.

- **WORK-2** `should`: Abandoning work is a decision, not a failure. A cancelled operation is not
 an error to report, retry, or log as one.
 *Why:* treating cancellation as failure produces error toasts on every back press, and retry
 loops that fight the user's navigation.
 *Not when:* the cancellation happened after a partial external effect, then it is a consistency
 problem, not a cancellation.
 *(The language mechanics of re-raising cancellation belong to `android/kotlin`.)*

- **WORK-3** `must`: Nothing that can block runs on the main thread: disk, network, parsing
 image or media decoding, cryptography, and synchronous preference writes.
 *Why:* the main thread has sixteen milliseconds to produce a frame, and every one of these can
 take longer than that without being slow enough to look like a bug in testing. On a fast device
 with a warm cache it never shows; on a cheap phone with a full disk it is a frozen screen and an
 ANR. The list matters more than the principle, disk and network are the ones people remember
 and decoding, crypto and a synchronous `commit()` are the ones that ship.
 *Not when:* the work is genuinely bounded and tiny, and you know that because you timed it on a
 slow device, not because it looks small.

### Security

- **SEC-1** `must`: Nothing in the shipped binary is secret. Keys in source, in resources, in the
 manifest, or in native code are all extractable.
 *Why:* an APK is a zip file. Obfuscation changes how long extraction takes, not whether it works.
 *Not when:* the value is a public identifier that the vendor documents as public.

- **SEC-2** `must`: A component reachable by another app validates what it is given and assumes
 the caller is hostile. `exported` is declared explicitly on every component with an intent filter.
 *Why:* an exported component is public API for every app on the device, and the intent's extras
 are attacker-controlled input.
 *Not when:* never, but most components should simply not be exported.

- **SEC-3** `must`: No user data reaches a release build's logs or its crash reports.
 *Why:* device logs are readable by more than you think, and crash reports leave the device
 entirely. *Not when:* the value is already public and non-identifying.

### Build

- **BUILD-3** `should`: Prefer KSP where the library ships a KSP processor, and never run KAPT
 and KSP for the same library.
 *Why:* KAPT generates Java stubs for every Kotlin source before anything else runs, which is the
 slowest step in most Android builds. Running both processors for one library generates the same
 code twice and fails with duplicate-class errors that name neither of them.
 *Not when:* the library ships no KSP processor, and then KAPT is the only option and that is fine.

### Localization and accessibility

- **L10N-1** `must`: Dates, times, numbers, and currency go through the platform's localized
 formatters, never a hand-written pattern.
 *Why:* a pattern translates the month name but keeps the source language's field order, so the
 result reads as a *different date* rather than a badly formatted one. Time of day is the trap:
 only the framework's context-aware format reads the user's 12/24-hour setting.
 *Not when:* the string is a machine-readable key or a wire format, those want a fixed
 locale-independent representation.

- **L10N-2** `must`: Never render a server token or an enum constant to a user. Map it at the UI
 edge, and give the unmapped case its own text rather than printing the fallback's name.
 *Why:* `PAYMENT_FAILED_INSUFFICIENT_FUNDS` on screen is untranslatable and unreadable, and the
 unmapped branch is the one that ships when the server adds a value.
 *Not when:* a debug surface where the raw value is the point.

- **A11Y-1** `must`: Every interactive element has a label, and every purely decorative one is
 marked as decorative.
 *Why:* an unlabelled icon button is announced as its class name. Marking decoration matters as
 much as labelling controls, an unmarked decorative image is read aloud as noise.
 *Not when:* the element already has visible text that says the same thing.

- **A11Y-2** `must`: Touch targets are at least 48dp, text contrast at least 4.5:1, and nothing is
 carried by colour alone.
 *Why:* these are the three that make a screen unusable rather than merely awkward, and all three
 are invisible on the developer's device. *Not when:* a platform-supplied control that already
 meets them.

## Why

<!-- human-only: not installed -->

**Why process death is the one to internalise.** A fragment and its view have different lifetimes
an activity and its process have different lifetimes, and almost every state bug on Android is
someone picking the wrong one. Rotation keeps the process alive, so a screen can pass every
rotation test you write and still lose everything when the user takes a call and comes back twenty
minutes later. The distinction that matters is not "does it survive rotation" but "what would this
screen need to rebuild itself from nothing", and the answer is almost always small: an id, a
filter, a query, a scroll position. If your saved state is large, you have saved the wrong half.

**Why the saved-state bundle is enforced so brutally.** It is not per-screen storage. Every saved
`Bundle` in the process is assembled into one parcel and handed across a binder transaction with a
hard ceiling, so a screen that saves a long note does not fail on its own, it fails whichever
screen happens to push the total over, at stop time, far from the code that caused it. That is why
the rule is "store payloads by id" rather than "keep it reasonably small".

**Why money is an integer.** Binary floating point cannot represent most decimal fractions, so a
list of prices that each look right sums to something that does not. But the subtler half is the
exponent: it belongs to the currency, not to the number 100. Yen and won have no minor unit, and
several dinars have three. Code that divides by 100 renders a ¥1,000 order as ¥10, and it will do
that in the one market where nobody on the team is testing.

**Why a parse failure must not become a zero.** A default is a value nobody chose, presented as a
value someone did. It corrupts everything downstream that sorts, totals, or filters on it, and it
does so silently, the screen looks fine, the numbers are wrong, and nothing in the logs points at
the field that failed. Absence is recoverable: it can be displayed, retried, or reported. Zero
cannot, because by the time anyone notices, it is indistinguishable from a real zero.

**Why clearing on sign-out is the cost of a local cache.** The moment a screen reads from local
storage rather than the network, the data outlives the session that fetched it. Filtering queries
by account id feels like the same thing and is not, the rows are still on disk, still in the
device backup, and still reachable by the next query that forgets the filter. The sign-outs that
matter are the ones the app did not initiate: a revoked token, an account removed in system
settings, a password change on another device.

**Why the UI must not overstate what the code did.** This is the one class of defect where the code
works exactly as written and the product is still wrong. A user who is told the work is handled
stops acting on it, they close the app, they stop retrying, they assume the message was sent. A
recoverable failure becomes a silent loss at the moment you reassure them. "Saved" for a write that
only reached the device is the common one.

**What the previous consensus was, and why it changed.**| Then | Now |
|---|---|
| One activity per screen | One activity, screens are destinations |
| `onSaveInstanceState` for everything | `SavedStateHandle` for what rebuilds, storage for what fills |
| Rotation as the state test | Process death as the state test |
| `AsyncTask`, then Loaders, then a reactive library | Lifecycle-scoped coroutines, and durable work for what must finish |
| A background service for anything long | `WorkManager`, because the OS will kill your service |
| `Double` for prices | Minor units plus a currency code |

Each of those moved for the same reason: the platform got more aggressive about reclaiming
processes, and every mechanism that assumed "my process stays alive" stopped being true.

## Pitfalls

<!-- human-only: not installed -->

- **The screen works until the tester leaves it open overnight.** Process death. It reproduces with
 `adb shell am kill <package>`, never by rotating.
- **A crash at stop time that nobody can reproduce on their own device.** Saved-state size. The
 screen that crashes is rarely the screen that saved too much.
- **Totals drift by a cent over long lists.** `Double`. It will pass every test with two items.
- **Correct-looking prices that are wrong by 100×.** A hardcoded exponent meeting a currency with a
 different one.
- **A sorted list where a few rows sit in the wrong place.** A parse failure defaulted to zero or
 the epoch, sorting as though it were real data.
- **The next user of a shared device sees the previous account's data.** Sign-out cleared the
 session and not the store, or filtered instead of deleting.
- **A date that reads as a different date in another locale.** A hand-written pattern: it translates
 the month name and keeps the source language's field order.
- **A screen that is unusable at 200% font scale** on a device nobody on the team uses.
- **Text that drops characters on a gesture or CJK keyboard** while feeling fine on a physical one.
- **An upload that vanishes when the user navigates away** work that needed durability got a
 screen-scoped lifetime instead.

## Provenance

**Added later: four unmeasured rules.** `WORK-3` (the main-thread rule) had no home: the first
`core` outline carried it, and when the file was written `WORK-1` became the durability rule and the
general principle was dropped without a decision. The only evidence either way is `OFF-MAIN` scoring
6/6 in an **Opus** control in eval 01, one model, one eval, never probed on Haiku or Sonnet, which
is where the capability window says it would fail if it fails anywhere.

`BUILD-1`–`BUILD-3` come from the `none` bucket in the register, 763 high-worth claims with nowhere
to live, of which most are agent-workflow noise rather than rules. These three are what survived
admission. Build is in `core` rather than its own topic because every Android project has it.

**eval 19 measured all four. Two are gone.** `WORK-3` is confirmed as a real failure and a rule that does not reliably fix it. The Haiku control
calls a filesystem read and a SHA-256 straight out of `onClick`, in **both** runs; with the skill it
happens in one of two. Sonnet never does it in any arm. Kept and recorded as *does not land* the
first evidence for this rule on anything other than Opus, whose control had scored it 6/6 and so said
nothing about the models where it fails.

`BUILD-1` (shrinking) is **retired**: `isMinifyEnabled` and `proguardFiles` appear in 8 of 8 runs
every arm. `BUILD-2` (`api`/`implementation`) is **cut** as untestable and unevidenced, and the
column that reported violations was itself wrong, since a public `RoomDatabase` subclass in the
module *is* the condition that makes `api` correct.

What survives is `BUILD-3`, KSP over KAPT, and it survives on evidence that contradicts the
pre-registered falsifier: **Haiku reaches for KAPT on Room in 4 runs of 4, in both arms.** A real
model failure the rule does not fix, rather than a corpus artifact. The departure from the
pre-registration is recorded in `evals/android/eval-19-core-v12/RESULTS.md`.


<!-- human-only: outside agent_sections, never installed -->

**Added later:** the shared precedence sentence: when a rule here conflicts with the code you are
editing, the surrounding convention wins for style and structure, but never for a rule whose failure
loses user data, leaks a credential, or ships a crash. Those get their own change.

That line exists because `android/java` needed it and had to discover it: eval 11 scored `LEAK-2` as
failing, and reading the runs showed two rules in the same file disagreeing, every treated run kept
a static `Context` because `CONVERT-1` says preserve behaviour exactly, which was correct. Two models
arbitrated it without being told. The sentence writes down what they worked out, and it is reasoning
rather than measurement everywhere except `java`.
