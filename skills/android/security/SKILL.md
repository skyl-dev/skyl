---
name: android/security
axis: topic
family: android
description: "Keeping a secret on a device you do not control: key storage, backup, intents, and client-side checks that are signals rather than controls. Use when the app holds a credential or talks to a server."
requires: [android/core]
version: 1.1.1
authors: [ahmmedrejowan]
agent_sections: [rules]
retired: []
detect:
  # An app that talks to a server holds a credential, whether or not it has reached for a
  # crypto library yet. Detecting only the crypto libraries would have matched the projects
  # that already thought about this and missed the ones that have not, which is backwards
  # for a skill whose first rule is about what happens when nothing is declared.
  gradle_dependency:
    - "androidx.security:security-crypto"
    - "androidx.biometric:biometric"
    - "com.google.android.play:integrity"
    - "net.zetetic:sqlcipher-android"
    - "com.squareup.retrofit2:retrofit"
    - "com.squareup.okhttp3:okhttp"
    - "io.ktor:ktor-client-core"
    - "com.google.firebase:firebase-auth"
    - "androidx.datastore:datastore-preferences"
  manifest_attribute: ["android:allowBackup", "android:dataExtractionRules"]
---

## Rules

Keeping a secret on a device you do not control, and the surfaces where data leaves the app. `core`
owns that nothing in the binary is secret (`SEC-1`), that an exported component treats its input as
hostile (`SEC-2`), and that user data stays out of release logs (`SEC-3`). `db` owns which store a
value belongs in (`STORE-3`). `networking` owns tokens on the wire (`AUTH-1`–`3`). `permissions`
owns what the app is allowed to reach. This owns keys, the IPC surface, and what copies itself off
the device.

**This is not a threat model.** These are the failures that are common, silent, and cheap to avoid.
An app with a real adversary needs a review, not a rules file.

**Scope.** New keys, new stores of sensitive values, new components reachable from outside the app
and the manifest.

**When not to apply**(whole-skill): an app that stores nothing about the user and exposes nothing to
other apps.

**Priority.** `must`, the failure exposes data, or destroys it silently. `should`, real exceptions
exist; name yours.

### Where a secret lives

- **STORE-1** `must`: A secret is stored as **ciphertext you produced** in an ordinary store.
 `EncryptedSharedPreferences` and `EncryptedFile` are **deprecated** do not introduce them in new
 code. Encrypt with a Keystore key (`KEY-1`) and write the result to preferences, DataStore, or a
 file like any other value.
 *Why:* `androidx.security:security-crypto` was deprecated in June 2025, and nearly every published
 example still recommends it, so it is the first thing anyone reaches for and nothing fails when you
 ship it. A cryptography dependency is the one you cannot afford to leave unmaintained. Doing it
 directly is also less code than the wrapper once the key already exists, and it makes the key's
 lifetime visible, which is what `KEY-2` and `OUT-2` are about.
 *Not when:* the value is not a secret. A username, a theme, a last-opened id, those are `db`'s
 `STORE-1`, not this one.
 *(`db STORE-3` states the store-choice half of this and defers here for the alternative. This rule
 is the alternative, and it stands alone: an app with no database never loads `db`.)*

### Keys

- **KEY-1** `must`: An encryption key is generated **inside** the Keystore and never leaves it.
 Never derive one from a constant, a value in resources, a build config field, or a device
 identifier.
 *Why:* `core SEC-1` says nothing in the binary is secret; this is what follows from it. A key you
 can read out of the app is not protecting anything, and a key derived from a device identifier is
 reproducible by anyone holding the device, which is exactly the case the encryption was for. A
 Keystore key is generated in hardware where available and cannot be exported at all, so extracting
 it means extracting it from that device while it runs, not from the APK.
 *Not when:* a key that is not a secret, a checksum seed, a public verification key.

- **KEY-2** `must`: One key per purpose, generated once and reused. Never mint a key per launch, per
 session, or per record.
 *Why:* a regenerated key makes every existing ciphertext permanently unreadable, and nothing
 reports it, the app comes up with an empty store, or throws deep inside a decrypt on a screen
 that has nothing to do with keys. It is data loss that looks like a parsing bug. From Android 17
 (API 37) there is also a hard ceiling: an app targeting it may own **50,000 keys** and creation
 beyond that throws `KeyStoreException`.
 *Not when:* a key deliberately scoped to something that ends, a key destroyed at sign-out to make
 the data it wrapped unreadable is the *point* and that is one key per session by design.

### What leaves the device

- **OUT-1** `must`: Backup is **on by default**. Decide explicitly what is copied off the device
 and say it twice: `dataExtractionRules` for API 31+, `fullBackupContent` for below.
 *Why:* every app targeting API 23 or higher participates in Auto Backup automatically, so a token
 written to preferences is on Google's servers and on the user's next phone without anyone choosing
 that. One set of rules is not enough, the two attributes cover different platform versions, and
 supplying only the newer one silently leaves older devices backing up everything.
 *Not when:* nothing the app stores is sensitive, and then that is still a decision written down
 rather than a default nobody read.

- **OUT-2** `must`: Anything encrypted with a Keystore key is excluded from backup and from
 device-to-device transfer.
 *Why:* the key is bound to the device and does not travel with the data. The ciphertext restores
 onto the new phone and cannot be decrypted by anything, ever, the user is signed out, or the app
 crashes in a decrypt, on a device where they have no history to explain it. Back up the fact that
 something existed, never the bytes only that phone could read.
 *Not when:* never. If it must survive a device change, it belongs behind a server, not behind a
 device-bound key.

### The IPC surface

- **IPC-1** `must`: An intent carrying anything sensitive names its target. Implicit intents are for
 asking the system to find *someone* which is the wrong verb for data that has an owner.
 *Why:* an implicit intent goes to whatever app has claimed the action, and any app can claim it.
 The extras go with it. This fails open and silently: on the developer's device the right app is
 installed and everything works.
 *Not when:* the point is to let the user choose, a share sheet, opening a URL, and then the
 payload is what the user chose to share.

- **IPC-2** `must`: A **mutable** `PendingIntent` names its target component or package. Never pair
 `FLAG_MUTABLE` with an implicit base intent.
 *Why:* the flag itself is not what gets forgotten, the platform throws from API 31 unless you
 choose one. The dangerous combination is the one it does not check. A mutable `PendingIntent`
 wrapping an implicit intent hands another app a blank cheque: it fills in the action and the
 target, and the result runs with **your** app's identity and permissions.
 *Not when:* immutable, which is almost always, and where the flag is all that is needed.

- **IPC-3** `must`: A component that must stay exported is protected by a permission, and identifies
 its caller from the binder, not from the intent.
 *Why:* `core SEC-2` says an exported component treats its input as hostile; this is the mechanic. A
 package name in an extra is a string the caller wrote. `Binder.getCallingUid()` is asserted by the
 kernel and cannot be forged. For components meant only for your own apps, a custom permission at
 `signature` protection level means only builds signed with your key can call it.
 *Not when:* the component is genuinely public and its input is genuinely untrusted, which is
 `SEC-2` doing its job.

### What the device can prove

- **TRUST-1** `must`: A check that runs on the device is a signal, not a control. Root detection
 emulator detection, debugger checks and integrity results evaluated on-device tell you something
 and enforce nothing.
 *Why:* the code making the decision is running on the attacker's machine, so the branch can be
 patched, the method hooked, and the boolean flipped. Anything that must actually hold, a
 purchase, an entitlement, a limit, is enforced where the attacker is not, and an integrity
 verdict is worth having only when a server verifies it. Client-side gates are worth writing when
 they raise the cost of casual tampering; they are not worth trusting.
 *Not when:* a check used to inform the server or to warn the user, which is what it is good for.

## Why

<!-- human-only: not installed -->

**Why the wrapper is the trap.** Every published example still reaches for
`EncryptedSharedPreferences`. It is deprecated, it still works, and nothing about shipping it
produces a warning anyone will see. That combination, universally recommended, silently unmaintained, and
cryptographic, is the worst shape a dependency can have.

Doing it yourself sounds harder and is not: once a Keystore key exists, encrypting a string and
putting the result in preferences is a few lines. What you get back is the thing the wrapper hid, a key with a visible lifetime, which is what both of the failures below depend on.

**Why regenerating a key is data loss, not a security issue.** A key created in the same code path
that encrypts looks harmless and is the most expensive mistake here. The next launch generates a
different key, every stored ciphertext becomes permanently unreadable, and nothing reports it. The
app comes up signed out, or throws inside a decrypt on a screen that has nothing to do with keys. It
is a data-loss bug wearing a parsing bug's clothes, and it reproduces only across restarts, which is
where nobody looks.

Android 17 adds a hard edge to the same mistake: an app targeting API 37 may own 50,000 Keystore
keys, and creation past that throws. Anything minting a key per record will find that ceiling.

**Why backup is the leak nobody chose.** Auto Backup is **on by default** for every app targeting
API 23 or higher. Write a ninety-day refresh token to preferences and it is on Google's servers and
on the user's next phone, because nobody wrote a line of code to make that happen. The default is
the decision, and it was made by someone else.

The rules also have to be stated twice, and this is where careful people still get it wrong:
`dataExtractionRules` covers API 31 and up, `fullBackupContent` covers below. Supply only the modern
one and older devices back up everything, quietly, exactly as before.

**Why backing up ciphertext is worse than backing up nothing.** A Keystore key is bound to its
device. Back up the encrypted blob and it restores perfectly onto the new phone, where nothing can
ever decrypt it. The user is signed out, or lands in a crash, on a device with no history to explain
it, and the data is not recoverable from anywhere, because the only key that could read it stayed
on a phone they have already traded in. Back up the fact that something existed. Never the bytes only
one device could read.

**Why the device cannot vouch for itself.** Root detection, emulator checks, debugger checks and
integrity results all run on the attacker's machine. The branch can be patched and the boolean
flipped. They are worth writing to raise the cost of casual tampering and worth sending to a server
as a signal, they are never worth trusting as a gate. Anything that must actually hold is enforced
where the attacker is not.

## Pitfalls

<!-- human-only: not installed -->

- **The user is signed out after an app update or a restart, with no error.** A key regenerated
 instead of reused.
- **`KeyStoreException` on key creation.** Android 17's 50,000-key ceiling, reached by minting one
 per record.
- **A refresh token on a new phone the user never signed into.** Auto Backup, on by default.
- **A crash inside a decrypt on a brand-new device.** Keystore ciphertext that was backed up; the
 key stayed behind.
- **Backup rules that work on new phones and not old ones.** `dataExtractionRules` supplied without
 `fullBackupContent`.
- **A deprecated crypto dependency in a security-sensitive path.** `androidx.security:security-crypto`
 which nearly every tutorial still recommends.
- **Another app acting with your identity.** `FLAG_MUTABLE` on a `PendingIntent` wrapping an implicit
 intent.
- **Account data delivered to whatever app claimed the action.** An implicit intent carrying extras
 that have an owner.
- **A premium feature unlocked by a patched boolean.** A client-side entitlement check.

## Provenance

<!-- human-only: outside agent_sections, never installed -->

**`STORE-1` exists because the eval found a hole in my own layering.** Of eval 17's 12 task-A runs
5 used the deprecated `EncryptedSharedPreferences` and ** 7 stored the token with no encryption at
all**; only 1 used the Keystore directly. `db STORE-3` says the wrapper is not the alternative and
defers here for what is, and the draft never caught the handoff, because `KEY-1` and `KEY-2` assumed
someone hand-rolling encryption rather than reaching for the library. Worse, `db` is detected by a
database dependency, and an app storing only a token has none, so in a project of that shape nothing
anywhere would have said it.

*(An earlier version of this note claimed all 24 runs used the wrapper. That was wrong, generalised
from one hand-checked run. See the correction in `evals/android/eval-17-security/RESULTS.md`.)*

**Eval 20 measured it properly** with four arms. `security` alone produces Keystore-backed encryption
in **4 of 4** runs; controls produce **0 of 4**. The rule works standalone, which was the point of
adding it.

**Confirmed movement:** `OUT-1` on Haiku, `0/2 → 2/2` on declaring backup rules at all. The "say it
twice" half landed in one of two runs, which is noise, so the rule reliably gets backup considered
and does not reliably get both files. Sonnet declared them in its control arm. See
`evals/android/eval-17-security/RESULTS.md`.

**Restraint held, and this is the first time this project measured it.** Task B included a case where
`IPC-1` must *not* fire, sharing a document to an app of the user's choosing. All 12 task-B runs kept the
share sheet, in every arm. The skill did not turn a legitimate implicit intent into a defect.

**Retired:** the `FLAG_IMMUTABLE` half of `IPC-2`. Present in 12 of 12 task-B runs, every arm, because the
platform throws from API 31 unless a flag is chosen, it cannot be got wrong. `IPC-2` now states only
the combination the platform does not check.

**Not reached by either task:** `KEY-1` and `KEY-2` were never tempted, since every run took the library path;
`IPC-3` and `TRUST-1` were reached by neither task; and `FLAG_MUTABLE` appears in 0 of 12 task-B runs, so
the mutable-plus-implicit case `IPC-2` now describes has not been tested.

Two facts here come from primary sources rather than the 553-row register, which contributed nothing
that measured: the Android 17 key ceiling, and that backup rules must be declared under both
attributes.
