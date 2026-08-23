---
name: android/networking
axis: topic
family: android
description: "Talking to a server: client configuration, what comes back, what happens when it does not, and how a request is authorised. Use when the app makes HTTP calls."
requires: [android/core]
version: 1.0.1
authors: [ahmmedrejowan]
agent_sections: [rules]
detect:
  gradle_dependency:
    - "com.squareup.retrofit2:retrofit"
    - "com.squareup.okhttp3:okhttp"
    - "io.ktor:ktor-client-core"
    - "io.ktor:ktor-client-android"
---

## Rules

Talking to a server: the client itself, what comes back, what happens when it does not, and how a
request is authorised. `core` owns which failures reach the user (`DATA-5`) and that a layer owns its
types (`BOUND-2`). `db` owns caching and staleness. `mvvm` owns where the source decision lives. This
owns the wire.

**When a rule here conflicts with the code you are editing** the surrounding convention wins for
style and structure, but never for a rule whose failure loses user data, leaks a credential, or
ships a crash. Fix those in their own change, not inside another one.

**Scope.** New endpoints and new clients. Match the client already configured in the module.

**When not to apply**(whole-skill): a single call to a service you control, in a prototype.

**Priority.** `must`, the failure hangs, leaks, or reaches production silently. `should`, real
exceptions exist; name yours.

### The client

- **CLIENT-1** `must`: One HTTP client for the app, built once and injected. Never constructed per
 request or inside a suspend function.
 *Why:* a client owns a connection pool and a thread pool. One per request means no connection reuse, a fresh TCP and TLS handshake every time, and the discarded clients leak threads and sockets
 until something notices. On a slow network the handshake is most of the latency.
 *Not when:* a genuinely different configuration is needed, a different host with different auth, and then it is a second long-lived client, not a per-call one.

- **CLIENT-2** `must`: Set a **whole-call** timeout, not only the per-operation ones.
 *Why:* the per-operation defaults are reasonable, OkHttp gives connect, read and write ten seconds
 each, and they do not bound the request. `callTimeout` defaults to **0, meaning no timeout** and
 it is the only one that spans the entire call: DNS, connect, sending the body, the server thinking
 reading the response, and every redirect and retry along the way. Each individual operation can
 keep resetting its own ten seconds while the call as a whole never finishes. The coroutine waiting
 on it is never resumed and the user watches a spinner with no end and no error.
 *Not when:* a deliberately long-lived connection, a stream, a large upload, which needs its own
 larger value rather than none.

- **CLIENT-3** `should`: Base URL, shared headers and content type are configured once on the
 client, not repeated per call site.
 *Why:* a hardcoded base URL cannot be pointed at staging, and a header set at forty call sites is
 set at thirty-nine after the next refactor. *Not when:* a header that genuinely varies per request.

### What comes back

- **WIRE-1** `must`: The parser tolerates unknown fields. A server adding a field must not break
 the app.
 *Why:* servers add fields without telling clients, and a strict parser turns that into a
 deserialization failure on a screen that was working, for users on an old build, with no way to
 fix it but an update. This is the most common cause of a working app breaking without a release.
 *Not when:* never for a response you do not control.

- **WIRE-2** `must`: Response fields are nullable unless the server contract guarantees them.
 Request fields are not.
 *Why:* the asymmetry is the point. A missing field in a response is a crash if the type says it
 cannot be absent, and servers omit fields, on error paths, for older accounts, in partial
 responses. A request field you are supposed to supply should fail at compile time if you do not.
 *Not when:* a field the server contractually guarantees, and then the guarantee is worth a comment.

- **WIRE-3** `should`: Wire names are declared explicitly on the model rather than inherited from
 property names.
 *Why:* otherwise renaming a Kotlin property silently changes the JSON you send and expect, and the
 break is at runtime against a server that did not change. The annotation makes the wire format a
 decision rather than a side effect of refactoring.
 *Not when:* a format you generate and consume on both ends.

- **WIRE-4** `must`: A field the protocol requires is sent even when it holds its default value.
 *Why:* serializers commonly omit defaults, so a constant like a version or type discriminator
 vanishes from the payload and the server rejects every request with a generic error that names
 nothing. It is invisible in the client's own logs because the object looks correct.
 *Not when:* the field is genuinely optional and the server treats absent and default alike.

### When it fails

- **FAIL-1** `must`: Distinguish no-connectivity, timeout, and a server response, and map each to a
 different domain failure.
 *Why:* they need different responses. No connectivity is retryable and the user should be told to
 check; a timeout may already have succeeded server-side; a 4xx will fail identically forever.
 Collapsing them into "network error" means the retry button is offered for the one case where it
 cannot help. *Not when:* never, this is the whole reason the layer exists.

- **FAIL-2** `must`: Retry only what is safe to repeat: transient transport failures and a server
 saying it is temporarily unavailable. Never a 4xx. Never a non-idempotent write unless the request
 carries an identity the server deduplicates on.
 *Why:* retrying a 4xx repeats a request that is wrong, forever. Retrying a POST that already
 succeeded but whose response was lost creates the order twice, and the client cannot tell that
 case from a genuine failure.
 *Not when:* the server documents the endpoint as idempotent.

- **FAIL-3** `should`: Retry with backoff and jitter, and a bounded number of attempts.
 *Why:* every client retrying on a fixed schedule after an outage arrives together and keeps the
 server down. Jitter spreads the herd; a bound stops one screen retrying forever.
 *Not when:* a single retry of a cheap read.

- **FAIL-4** `must`: Do not check connectivity before a request as a precondition. Make the request
 and handle the failure.
 *Why:* the check is a race, connectivity can drop between the check and the call, and a reported
 connection does not mean the host is reachable. A validated-connectivity signal is useful for
 telling the user why something failed, and useless as a gate.
 *Not when:* deciding whether to *schedule* deferred work, which is a different question.

### Authorisation

- **AUTH-1** `must`: The token is attached by the client, not by a parameter on each endpoint.
 *Why:* one endpoint that forgets the parameter is an unauthenticated request, and it fails as a
 401 that looks like an expired session rather than a missing header. There is no compiler check
 for the endpoint you did not annotate.
 *Not when:* an endpoint that must be called without auth, and that is an exclusion on the client
 by route, not the absence of a parameter.

- **AUTH-2** `must`: A token refresh cannot trigger itself. The refresh request is excluded from the
 attach-and-retry path, and refresh attempts are bounded.
 *Why:* otherwise a 401 on refresh triggers a refresh, which 401s, which triggers a refresh. It
 presents as the app hanging on launch and hammering the auth server, and it only happens once the
 token has actually expired, so it reaches production.
 *Not when:* never.

- **AUTH-3** `should`: Concurrent requests that hit a 401 refresh once between them, not once each.
 *Why:* a screen firing four parallel calls with an expired token performs four refreshes, and on a
 server that rotates refresh tokens three of them invalidate the fourth, signing the user out at
 the moment the app was recovering.
 *Not when:* a single-request client where concurrency is impossible.

### Streaming

- **STREAM-1** `must`: A long-lived connection is bound to the lifetime of whatever consumes it, so
 cancelling the consumer closes the connection.
 *Why:* a socket held after the screen is gone keeps the radio awake and the server holding state.
 Nothing closes it, because nothing knows the reader has left.
 *Not when:* the connection is genuinely app-scoped and intended to outlive any screen.

## Why

<!-- human-only: not installed -->

**Why the whole-call timeout is the one that matters.** The per-operation timeouts look like they
bound a request and do not. OkHttp gives connect, read and write ten seconds each, and each one
resets on activity. A server that dribbles a response a byte at a time never trips the read timeout;
a redirect chain restarts the clock at every hop. `callTimeout` is the only setting that bounds the
whole thing, DNS, connect, request body, server thinking, response body, redirects, retries, and
it defaults to **zero, meaning no timeout at all**.

So a request against a sick server can hang indefinitely with all three per-operation timeouts
correctly configured. The coroutine waiting on it is never resumed, and the user watches a spinner
that will never stop.

**Why unknown fields are the most common way a working app breaks.** Nothing shipped. Nobody
deployed. A backend team added a field to a response because a different client needed it, and
every install with a strict parser starts failing on a screen that worked yesterday. Those users
cannot fix it; they need a new build. The tolerance costs one setting and removes an entire class
of outage from a decision made by people who do not know your app exists.

The nullability half is the same argument from the other side. Servers omit fields, on error paths
for older accounts, in partial responses, and a non-null type turns an omission into a
deserialization crash. Request fields are the opposite: those you are supposed to supply, and the
compiler should say so.

**Why "network error" is not one thing.** No connectivity, a timeout, and a 4xx need three different
responses. Offline is retryable and the user can act on it. A timeout may have *succeeded* on the
server, the response was lost, not the work. A 4xx will fail identically forever, and offering a
retry button for it is a lie. Collapsing all three into one message means the only case where retry
cannot help is the one where it is offered.

**Why retrying a write is different from retrying a read.** A read is safe to repeat. A write that
timed out may already have been applied, the client cannot distinguish "never arrived" from
"arrived, response lost", and those need opposite handling. Retrying the second creates the order
twice. The fix is not to avoid retrying but to make the request identifiable, so the server can
recognise the repeat and return the original result.

**Why token refresh is where auth code goes wrong.** Refresh is the one request that must not be
authorised the normal way, and the one whose failure must not trigger itself. A 401 on refresh that
triggers a refresh is an infinite loop that only appears once a token has genuinely expired, so it
passes every test and reaches production. And a screen firing four parallel calls with a stale token
refreshes four times; on a server that rotates refresh tokens, three of those invalidate the fourth
and sign the user out at the exact moment the app was recovering.

## Pitfalls

<!-- human-only: not installed -->

- **A spinner that never stops, against a server that is up but sick.** No whole-call timeout.
- **The app breaks and nobody deployed anything.** A strict parser and a server that added a field.
- **A crash on some accounts and not others.** A non-null response field the server omits for older
 records.
- **The server rejects every request with a generic error.** A protocol-constant field omitted
 because it held its default value.
- **A retry button offered for an error that will never succeed.** All failures collapsed into one.
- **Two orders from one tap.** A non-idempotent write retried after a lost response.
- **The app hangs on launch and hammers the auth server.** Refresh triggering refresh.
- **Signed out at the moment the app recovered.** Four concurrent refreshes, three invalidating the
 fourth.
- **A socket held open after the user left the screen.** A stream not bound to its consumer.

## Provenance

<!-- human-only: outside agent_sections, never installed -->

Eval 13, 24 runs across two tasks on Haiku 4.5 and Sonnet 5. ** One rule separated: `CLIENT-2`, on
Haiku, 0/2 → 2/2.** It is also the rule whose reason came from a primary source rather than the
corpus, checking OkHttp's actual defaults showed the per-operation timeouts are ten seconds each
and only `callTimeout` defaults to none.

`AUTH-1`, `AUTH-2` and `AUTH-3` are satisfied unaided by both models on a task built to tempt them.
Kept anyway: they cost little, and the sample is two per cell.

`WIRE-3`, `WIRE-4`, `CLIENT-3`, `FAIL-3`, `FAIL-4` and `STREAM-1` were not exercised.

This register was the richest of any axis, 81 evidenced claims from 12 repos, and produced the
thinnest result. That is the project's pattern holding: heavy corpus backing predicts rules the
model already follows. See `evals/android/eval-13-net/RESULTS.md`.
