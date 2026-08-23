---
name: android/db
axis: topic
family: android
requires: [android/core]
version: 1.0.0
authors: [ahmmedrejowan]
agent_sections: [rules]
detect:
  gradle_dependency:
    - "androidx.room:room-runtime"
    - "androidx.datastore:datastore"
    - "androidx.datastore:datastore-preferences"
    - "app.cash.sqldelight"
  file: ["**/schemas/*.json"]
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

## Why

<!-- human-only: not installed -->

**Why the store choice is the first decision and the hardest to undo.** Everything else here can be
changed in an afternoon. Where a value lives cannot: the data is already there, in a format, on
users' devices, and moving it is a migration with a failure mode of its own. That is why
`SharedPreferences` persists in codebases long after everyone agrees it should not, the cost of
moving is real and the cost of staying is invisible until a write fails silently.

The shape test settles it without argument. A flag is a scalar. A list you filter is a query. A
photo is a file. Ask what you will do with the value in six months, not what is quickest to write
today.

**Why `EncryptedSharedPreferences` is the trap in this file.** It is the most-recommended secure
storage instruction in the published Android material, by a wide margin, and with good reason: for
years it *was* the right answer. `androidx.security:security-crypto` was deprecated in June 2025 in
favour of platform APIs and direct Keystore use, and both `EncryptedSharedPreferences` and
`EncryptedFile` went with it.

Nothing about that is enforced. The library still resolves, still compiles, still encrypts. An app
shipped on it today is running unmaintained cryptography, and the person who wrote it followed the
advice they found. This is the clearest example in the whole skill of why a rule needs its reason
attached: "use DataStore" without the deprecation is an aesthetic preference, and it loses the
argument to a hundred blog posts.

**Why offline-first is mostly about writes, not reads.** Caching reads is easy and everyone does it.
The hard half is what happens to a change the user made while they had no network. If it lives only
in memory, the process dies and so does the change. If it is sent optimistically and the request
fails, the UI has already said it worked. If it is retried without an identity, it is applied twice.
Every one of those is silent, and every one of them is the user losing something they were told
they had.

**Why the delete case is worse than the write case.** A missing write can be retried. A delete that
does not propagate is *undone* the row comes back on the next sync, because from the server's
point of view the client simply has less data than it does. To the user, the app ignored them and
then contradicted them. That is what a tombstone is for: recording that something was deliberately
absent, not merely missing.

**Why device clocks cannot arbitrate.** Two devices, two clocks, one of them wrong by an hour, and
last-write-wins silently discards the write that was actually later. It never reproduces in testing
because every device in the room is synced to the same source. A server-assigned version has one
authority and no ambiguity.

**What changed, if you learned this earlier.**| Then | Now |
|---|---|
| `SharedPreferences` for scalars | `DataStore`, async, typed, observable failures |
| `EncryptedSharedPreferences` for secrets | deprecated June 2025; platform APIs and Keystore |
| `fallbackToDestructiveMigration` while iterating | a migration per change, and the schema committed |
| a `LiveData`/one-shot read per screen | one observed stream, so every reader updates |
| retry queue in memory | pending state in the store, ordered, visible on failure |

## Pitfalls

<!-- human-only: not installed -->

- **The app updates and the user's data is gone.** Destructive fallback left enabled. No crash
 nothing in the logs, nothing to recover.
- **A setting that silently reverts.** `apply()` failed and reported nothing, or a mistyped key is
 returning the default.
- **The catalogue is empty offline after a failed refresh.** The cache was cleared before the fetch
 or the delete-then-insert was not one transaction.
- **A deleted item that keeps coming back.** No tombstone, so the next sync restores it.
- **Two devices, and the older edit wins.** Conflict decided by device clock.
- **A save the user made on the train is gone when they get off.** The write was conditional on the
 request, or queued in memory.
- **One screen shows stale data while the other is correct.** A one-shot read at screen entry
 instead of an observed stream.
- **An ANR on old devices only.** Main-thread queries enabled to unblock a test.
- **A shipped app running unmaintained cryptography.** `EncryptedSharedPreferences`, chosen from
 documentation that is still, at the time of writing, the top search result.

## Provenance

<!-- human-only: outside agent_sections, never installed -->

`WRITE-1` is measured: across the eval-08 runs, Haiku wrote delete-then-insert with no transaction
in 4 of 4 runs that used the pattern; Sonnet used one in 3 of 3. See `evals/android/eval-08-shared/`.

Eval 09 tested this skill against `core` alone and returned a null. That eval could not test it: the
task specified the behaviour most of these rules describe, and four rules had nothing to act on.
See `evals/android/eval-09-db/RESULTS.md`. Everything except `WRITE-1` is unmeasured.

`SYNC-2` was rewritten after eval 10. Its first form, "resolved by a server-assigned version
never by device clocks", failed to land in every treated run: all 10 runs that produced code used
the device clock, because the task's API supplied no version and the rule named no alternative. A
prohibition with no actionable branch for the common case is not a rule the model can follow. It now
states what to do when the server offers nothing.

`STORE-3` is a reversal, see `registers/android/REVERSALS.md`. The deprecation is recorded
against the Jetpack Security release notes, not against secondary sources.

**`STORE-3` shrank to a pointer after eval 20.** It previously named the deprecated wrapper
and deferred the alternative. Measured at the seam with four arms, `security` alone produced
Keystore-backed encryption in 2/2 Haiku runs and **`db` + `security` together produced 0/2** the
extra rule count displaced the rule that mattered, on the model least able to absorb it. Sonnet was
unaffected. Stating one hazard in two skills is the restatement case, and on a small model it is not
merely redundant but harmful. See `evals/android/eval-20-seams/RESULTS.md`.

Measurement is kept out of `## Rules` deliberately: a rule that names its own control-arm score
tells the model it is being watched and names the rule under observation.

**Added later:** the shared precedence sentence: when a rule here conflicts with the code you are
editing, the surrounding convention wins for style and structure, but never for a rule whose failure
loses user data, leaks a credential, or ships a crash. Those get their own change.

That line exists because `android/java` needed it and had to discover it: eval 11 scored `LEAK-2` as
failing, and reading the runs showed two rules in the same file disagreeing, every treated run kept
a static `Context` because `CONVERT-1` says preserve behaviour exactly, which was correct. Two models
arbitrated it without being told. The sentence writes down what they worked out, and it is reasoning
rather than measurement everywhere except `java`.
