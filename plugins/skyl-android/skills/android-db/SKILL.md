---
name: android-db
description: "Persistence and offline behaviour: where a value lives, what survives, transactions, migrations, and what happens when the network does not answer. Use when the app stores data on the device."
---

## Rules

Persistence and offline behaviour: where a value lives, what survives, and what happens when the
network does not.

`core` owns *which* data has a single source of truth (`DATA-1`) and *when* it is destroyed
(`DATA-4`). `mvvm` owns *where* the choice between sources is made (`REPO-1`). `android/security`
owns how a value is protected. This owns how the store itself behaves.

**Scope.** New code and new tables. Match the schema conventions already in the module.

**When a rule here conflicts with the code you are editing** the surrounding convention wins for
style and structure, but never for a rule whose failure loses user data, leaks a credential, or
ships a crash. Fix those in their own change, not inside another one.

**When not to apply**(whole-skill): a cache that is genuinely disposable and re-fetched every
launch, with nothing a user would miss.

**Priority.** `must`, the failure loses user data or ships a crash. `should`, real exceptions
exist; name yours.

### Choosing a store

- **STORE-1** `must`: Choose by the shape of the data: scalars and flags in a typed key-value
 store (`DataStore`), anything queried or related in the database, large blobs on the filesystem
 with the path in the database. `SharedPreferences` is not the answer in new code.
 *Why:* `SharedPreferences` is a synchronous API in front of a file. The first read blocks whichever
 thread asks, `apply()` reports nothing when the write fails, and `commit()` blocks to tell you.
 `DataStore` gives the same job an asynchronous API, a typed schema, and failures you can observe.
 *Not when:* an existing, widely-used preference. Migrating it risks losing data for no gain, wrap
 it, do not move it. See `references/storage-choice.md`.

- **STORE-2** `must`: Key-value storage is reached through one class that owns the keys, never by
 reading a key at the call site.
 *Why:* a string key repeated in four files is four chances to mistype it into a silent default
 and the default looks exactly like a real value. The wrapper is also what makes the store
 swappable and testable. *Not when:* never, this is one small file.

- **STORE-3** `must`: A secret does not belong in any store this skill describes. `android/security`
 owns where it goes and how; follow it rather than choosing here.
 *Why:* a secret has different requirements from data, a key with a lifetime, exclusion from
 backup, a store that is not the one a schema lives in, and every one of them belongs to a
 different skill. Deciding it here means deciding it twice, and the two answers drift.
 *Not when:* never, and if `android/security` is not installed on a project that stores a secret
 that is the thing to fix rather than this rule.

- **SCHEMA-1** `must`: Every schema change ships a migration. Destructive fallback is never enabled
 in a release build.
 *Why:* the fallback drops and recreates the tables, so the app updates and the user's data is gone, silently, with no crash and nothing to recover from. It is a development convenience that
 reaches production precisely because nothing fails when it does.
 *Not when:* a table that is purely a cache of remote data, and even then scope the fallback to
 that table rather than enabling it database-wide.

- **SCHEMA-2** `should`: Export the schema and commit it.
 *Why:* the exported JSON is what makes a migration testable, and what shows a reviewer that a
 column changed. Without it, migrations are written from memory against a schema nobody can see.
 *Not when:* a pre-release app with no installed users.

### Writes

- **WRITE-1** `must`: A write spanning more than one statement is one transaction. Replacing a
 cached collection, delete, then insert, is the common case.
 *Why:* a failure between the delete and the insert leaves the store empty, and a user who was
 offline now has nothing where they had stale-but-usable data a moment ago. The window is small
 which is why it survives testing and shows up in the field.
 *Not when:* a single statement, which is already atomic.

- **WRITE-2** `must`: A change the user made is applied locally first and survives without the
 network. Do not make a user-visible change conditional on a request succeeding.
 *Why:* it is the difference between an app that works on a train and one that does not. A save
 that exists only once the server acknowledges it is lost on every failed request, and the user is
 not told. *Not when:* the write genuinely cannot be resolved locally, a payment, an identifier
 the server must assign.

- **WRITE-3** `should`: A local write that must reach the server is recorded as pending in the
 store, sent in order, and stays visible if it permanently fails.
 *Why:* an in-memory retry queue dies with the process, which is exactly the moment it was needed.
 And a pending write silently dropped after its retries is a lost write the user believes
 succeeded. *Not when:* the write is local-only with no server counterpart.
 See `references/offline-writes.md`.

### Cache lifecycle

- **CACHE-1** `must`: Staleness is one rule in the data layer with a stated duration, not a
 judgement made at each call site.
 *Why:* the same question asked in three places gets three answers, and the one that refetches on
 every screen open is the one that spends the user's data. One rule, one place, one duration that
 can be changed. *Not when:* data that must always be live, and "never cache" is also a rule in
 one place.

- **CACHE-2** `must`: A forced refresh is the same path with a flag, not a second path that
 bypasses the cache.
 *Why:* two paths diverge. The one behind pull-to-refresh gains a fix the ordinary path does not
 and the two stop agreeing about what "loaded" means. *Not when:* never, if forcing needs
 different behaviour, that is a parameter.

- **CACHE-3** `must`: Never empty the cache as part of an ordinary read. Stored data stays until it
 is replaced or explicitly cleared.
 *Why:* clearing before fetching means every failed refresh costs the user their offline copy. The
 correct order is fetch, then replace, in one transaction. *Not when:* the user signed out, and
 that is `core DATA-4`, which deletes rather than clears.

### Deletes and conflict

- **SYNC-1** `should`: A delete that must propagate leaves a tombstone, kept at least as long as a
 device may plausibly stay offline.
 *Why:* without one, the next sync sees a row the server still has and the client does not, and
 restores it. The deleted item comes back, which reads to the user as the app ignoring them.
 *Not when:* deletes are local-only, or the server sends authoritative full state.

- **SYNC-2** `must`: The client does not arbitrate conflicts with a device clock. Where the server
 supplies a version, sequence or ETag, send it back and let the server decide. Where it supplies
 none, the client does not invent an ordering: send the change and accept the server's response as
 the result, or surface the conflict to the user.
 *Why:* device clocks are wrong, by seconds usually, by hours sometimes, and the user can set them
 to anything. The loser of a clock comparison is overwritten with no error raised anywhere, and it
 never reproduces in testing because every device in the room is synced to the same source.
 The common case is an API that offers no version at all, and the wrong response to that is to
 substitute `updatedAt` from the device and call it resolution. Not arbitrating is a valid
 behaviour; arbitrating badly is not.
 *Not when:* the clock is used for cache staleness rather than conflict, that is `CACHE-1`, and it
 is fine. Or writes are genuinely commutative, appending to a log, incrementing a counter, where
 there is no conflict to resolve.

### Reads

- **READ-1** `must`: The store is observed, not polled. A screen that must reflect a change made
 elsewhere reads a stream, so one write updates every reader.
 *Why:* this is what makes two screens agree without either knowing the other exists. A one-shot
 read taken at screen entry is stale the moment anything else writes.
 *Not when:* a genuinely one-shot read, an export, a migration, a background job.

- **READ-2** `must`: Never enable main-thread queries. The database library refuses main-thread
 access by default, and that refusal is the guard rail.
 *Why:* the flag exists to unblock a test and reaches production because nothing fails when it
 does. It converts a crash development would have caught into an ANR in the field, on the slowest
 devices with the largest datasets, the users least able to tolerate it.
 *Not when:* never.
