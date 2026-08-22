# Offline writes

Referenced by `db WRITE-2`, `WRITE-3`, `SYNC-1` and `SYNC-2`.

Caching reads is the easy half and everyone does it. The hard half is a change the user made with no
network, and every way of getting it wrong is silent.

## Local first, always

    // wrong, the change exists only if the request succeeds
    api.save(id)
    dao.markSaved(id)

    // right, the user's change is real immediately; the server catches up
    dao.markSaved(id)
    outbox.enqueue(Save(id))

The first version loses the change on every failed request, and the UI has usually already said it
worked. The second is what "works offline" means in practice.

## The outbox

A pending write belongs in the store, not in memory:

| In memory | In the store |
|---|---|
| dies with the process, exactly when it was needed | survives a kill, a reboot, an update |
| invisible to the UI | can be shown as pending, or as failed |
| order lost on restart | order preserved |

Three properties make it work:

- **Ordered.** Send in the order the user made the changes. A rename followed by a delete, applied
  the other way round, is a resurrected row with an old name.
- **Identified.** Give each mutation a client-generated id and have the server deduplicate on it.
  Without that, a retry after a response that was actually delivered applies the change twice.
- **Visible on permanent failure.** A pending write dropped after its retries is a lost write the
  user believes succeeded. Leave it visible and actionable, with the reason.

Do not build this by replaying raw HTTP requests from a log. It loses ordering, has no identity, and
retries requests whose meaning has since changed.

## Tombstones

A delete that must propagate is not the absence of a row, it is a fact that has to be recorded:

    // the row is gone locally, so the next sync sees the server has one row more
    // than the client, and helpfully restores it

Keep a tombstone at least as long as a device might plausibly stay offline. That window is a product
decision, a week for a note-taking app, an hour for a chat, and it is also what sets how long the
server must retain deletions.

Not needed when deletes are local-only, or when the server sends authoritative full state and the
client simply mirrors it.

## Conflict

Two devices edit the same row while both are offline. On reconnect, something has to lose.

**Never decide by comparing device clocks.** Clocks are wrong, by seconds usually, by hours
sometimes, and the user can set them to anything. The loser of a clock comparison is overwritten
with no error raised anywhere, and it never reproduces in testing because every device in the room
is synced to the same source.

**Where the server supplies a version, sequence or ETag** send back the one you last saw. The
server then knows whether you are writing against current state and can accept, reject, or merge
under a documented rule. One authority, no ambiguity.

**Where the server supplies nothing** which is the common case, do not fill the gap with
`updatedAt` from the device. That is not conflict resolution; it is a coin flip weighted by whichever
device has the faster clock. Two options remain, and both are honest:

- **Let the server be the outcome.** Send the change, accept whatever comes back as the new truth
  and re-render. Last-writer-wins decided by arrival order at one machine is at least *one* clock.
- **Surface it.** Keep both versions and ask. Expensive in UI, correct in data, and the right answer
  when the content is something the user would hate to lose silently.

Not arbitrating is a valid behaviour. Arbitrating badly is not.

Using the device clock for **cache staleness** is a different thing and is fine, being wrong about
whether data is an hour old costs a refetch, not a lost edit.
