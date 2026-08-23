---
name: android-security
description: "Keeping a secret on a device you do not control: key storage, backup, intents, and client-side checks that are signals rather than controls. Use when the app holds a credential or talks to a server."
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
