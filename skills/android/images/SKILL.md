---
name: android/images
axis: topic
family: android
requires: [android/core]
version: 1.0.0
authors: [ahmmedrejowan]
agent_sections: [rules]
retired: [MEM-2, USER-1, TEST-1]
detect:
  gradle_dependency:
    - "io.coil-kt.coil3:coil-compose"
    - "io.coil-kt:coil-compose"
    - "io.coil-kt:coil"
    - "com.github.bumptech.glide:glide"
    - "com.squareup.picasso:picasso"
---

## Rules

Images that arrive at runtime: fetched from a URL, picked by the user, or decoded from a file. `core`
owns that decoding never blocks the main thread (`WORK-1`) and that every image carries a label
(`A11Y-1`). `networking` owns the HTTP client. `db` owns what is stored. This owns what happens
between a URL and a pixel.

**Bundled assets are not this skill.** A drawable or a vector in the app's own resources is resolved
at compile time and has none of these problems. Do not route one through an image loader.

**Scope.** New image loading, new decoding, and the path that accepts an image from the user. Match
the loader already configured in the project, this skill never says to change libraries.

**When not to apply**(whole-skill): an app whose only images ship inside it.

**Priority.** `must`, the failure loses data, exhausts memory, or reaches production silently.
`should`, real exceptions exist; name yours.

### The loader

- **LOAD-1** `must`: The image loader is built **once for the application** and given the app's own
 HTTP client. Never construct one per screen, per composable, or per request.
 *Why:* the loader is a second network stack. Everything configured on the app's client, authorization interceptor, certificate pinning, headers, timeouts, proxy, connection pool, reaches
 API calls and does not reach image requests, so the symptom is precise and confusing: every
 endpoint authenticates and every authenticated image returns 401 or a placeholder. Building a
 second loader also discards the memory cache the first one holds, so images already in memory are
 fetched and decoded again.
 *Not when:* a genuinely different destination with different credentials, which is a second
 long-lived loader rather than a per-screen one.
 Extends `networking CLIENT-1` and `AUTH-1`: the client is shared and the token is attached by the
 client, which is exactly why an image request built outside it carries neither.

- **LOAD-2** `must`: Adding an image library is not enough to fetch a URL, check that the artifact
 that does the fetching is present. Coil 3 ships **no network support by default**: without
 `coil-network-okhttp` (or a Ktor equivalent) an `http(s)` model resolves to nothing, with no crash
 and no error in the log.
 *Why:* the failure looks like a broken URL or a server problem, and it is a missing line in the
 build file. Coil 3 split networking out deliberately so a project bringing its own stack is not
 forced to take OkHttp; the cost is that the default state of a new integration is silence.
 *Not when:* every image comes from local files or bundled resources.

### Memory

- **MEM-1** `must`: Decode to the size that will be displayed, never to the size of the file.
 *Why:* a decoded bitmap costs `width × height × 4` bytes, and the compressed file size predicts
 nothing about it, a 900 KB JPEG at 4000×3000 is **48 MB** in memory. A loader given a bounded
 container measures it and samples down. It cannot do that where the container is unbounded, and
 nothing does it in a hand-rolled decode: `BitmapFactory.decodeFile` allocates the full image.
 Read the bounds first, then decode with a sample size.
 The sharpest case is a photo the user just took: it arrives at full sensor resolution, so decoding
 it for a 96 dp avatar allocates tens of megabytes, and ** uploading it re-encoded but not resized
 sends all of them over the user's connection.** Re-encoding is not downscaling, quality 95 on a
 12-megapixel image is still a 12-megapixel image.
 *Not when:* the image is about to be cropped, zoomed, or exported at full resolution, then the
 full decode is the point, and it belongs off the main thread with the memory budgeted for it.

### Cache

- **CACHE-1** `must`: The cache key is the URL string. A URL carrying a signed token, an expiry, or
 a cache-buster is a different key every time it is generated, so nothing ever hits the cache. Where
 the URL varies but the image does not, set the cache key explicitly to the image's stable identity.
 *Why:* the symptom is not an error, it is a feed that re-downloads every avatar on every scroll
 burns the user's data, and looks like a slow network. Presigned URLs from object storage are the
 usual source, and they are invisible in review because the code is correct.
 *Not when:* the URL changing genuinely means the image changed.

- **CACHE-2** `should`: Decide what invalidates a cached image, rather than assuming HTTP caching
 applies. Coil 3 **ignores `Cache-Control` by default** and writes every response to its disk cache;
 honouring headers requires an extra artifact and an explicit cache strategy.
 *Why:* an image replaced at a URL that does not change, a profile photo, a re-uploaded document, is served from disk indefinitely, and a user who just changed their avatar sees the old one. The
 fix is a key that changes with the content, or a deliberate policy on the request; it is not a
 header the server can set.
 *Not when:* content-addressed URLs, where the URL already changes with the bytes.

### Images from the user

- **USER-2** `must`: What a picker returns is a **URI carrying a temporary read grant** not a file
 path, and the grant is narrower than it looks.
 *Why:* the underlying file often does not exist on your filesystem, it may be in another app's
 storage, behind a document provider, or a cloud file with no local copy, so building a `File` from
 it fails on exactly the devices you did not test. And the grant lasts as long as the process that
 received it: store the URI, restart, read it again, and it throws `SecurityException` unless the
 permission was explicitly taken as persistable.
 *Not when:* a file your own app wrote to its own storage.

## Why

<!-- human-only: not installed -->

**Why the loader is a second network stack.** This is the idea the rest of the loading rules hang
off, and it is invisible until it bites. An image library ships its own HTTP client, so everything
the team carefully configured on the app's client, the authorization interceptor, certificate
pinning, the connection pool, timeouts, the proxy, logging, applies to API calls and not to image
requests. The symptom is unusually precise: every endpoint authenticates and every authenticated
image comes back 401 or falls to a placeholder. People debug the CDN for a day.

Coil 3 sharpened this by splitting networking into a separate artifact. The reasoning is sound, a
project bringing its own stack should not be forced to take OkHttp, but it means the default state
of a fresh integration is that `https` URLs resolve to **nothing at all** with no crash and no log
line. Our own eval control arm wrote a clean, well-keyed, properly labelled feed that displayed
blank boxes, and nothing in it looks wrong.

**Why the decoded size is the only size that matters.** A bitmap costs `width × height × 4` bytes in
memory and the file size predicts none of it. A 900 KB JPEG at 4000×3000 is 48 MB decoded; three of
them is an OOM on a mid-range phone. The compression ratio is doing all the work in the file and
none of it in memory, which is why "the image is only 900 KB" is the most common wrong answer to an
image OOM.

The corollary catches people on the way out as well as in. Re-encoding is not downscaling, a photo
compressed at quality 95 is still every one of its twelve million pixels, so the upload is tens of
megabytes of the user's data for something displayed in a 96 dp circle. The failure shows up as a
timeout on a slow connection and reproduces nowhere near the office.

**Why a working cache and a broken one look identical.** The cache key is the URL string. Object
storage hands out presigned links minted per response, so the same photo has a different URL every
time the feed loads and nothing ever hits the cache, no error, no warning, just a feed that
re-downloads every image on every scroll and reads as a slow network. The code is correct, which is
why review never catches it. The inverse costs as much: an avatar replaced at a URL that does not
change is served from disk indefinitely, and Coil 3 ignores `Cache-Control` by default, so the
server cannot fix it for you. In both directions the fix is the same question, *what identity does
this cache entry actually have?*

**Why a picked image is not a file.** A picker returns a URI with a grant, and the bytes behind it
may live in another app's storage, behind a document provider, or in a cloud account with no local
copy. `File(uri.path)` works on the developer's device and on none of those. The grant is also
scoped to the receiving process, so a URI saved to disk and read after a restart throws, the code
worked in every test that did not include killing the app.

## Pitfalls

<!-- human-only: not installed -->

- **Images never appear, nothing errors, and the log is empty.** Coil 3 with no network artifact.
- **Every API call authenticates and every image 401s.** A loader that is not carrying the app's
 client.
- **A feed that re-downloads everything on every scroll, and reads as a slow network.** A presigned
 URL used as the cache key.
- **The user changes their avatar and still sees the old one.** A stable URL and a cache with no
 reason to let go of it.
- **An OOM on an image "only 900 KB".** Decoded size is `w × h × 4`, not the file size.
- **An avatar upload that times out on cellular.** Re-encoded at quality 95, never resized.
- **A camera photo displayed sideways.** `BitmapFactory` does not read EXIF orientation, `ImageDecoder` and every image loader do. This is only a risk in a hand-rolled decode.
- **`SecurityException` reading a URI after a restart.** A grant that was never taken as persistable.
- **A crash when a bitmap goes into a notification or a widget.** Anything crossing a process
 boundary shares a ~1 MB binder buffer, and a decoded bitmap does not fit.
- **`Cache-Control` set carefully on the server and ignored on the device.** Coil 3's default.

## Provenance

<!-- human-only: outside agent_sections, never installed -->

**Eval 15: two confirmed separations, both `0/2 → 2/2` on Haiku 4.5, with the `+core` arm flat.** `LOAD-2` (the network artifact) and `MEM-1` (downscaling on the upload path). Sonnet 5 satisfied both
in every arm including control, the capability window again. 24 runs, two brownfield tasks, all
model ids confirmed. See `evals/android/eval-15-images/RESULTS.md`.

**Retired as satisfied unaided.** `MEM-2` (reserve the image's space in a list) was Y in **12 of 12** task-A runs, both models, both batches, every arm. The orientation half of the original `USER-1` was
written correctly by the Haiku *control* complete with all four rotation and flip cases; it survives
only as a pitfall.

**Kept but model-dependent:** `CACHE-2` is 2/2 in Sonnet's control and 0/6 on Haiku *including with
the skill loaded*. **Not reached by either task:** the persistable half of `USER-2` was never tempted
because every run uploaded immediately.

**Removed:** `TEST-1` (a test that renders an image does not fetch one) was a subset of
`android/testing`'s `REACH-1`, a unit test reaches nothing outside the process. Eval 20 measured what
stating one hazard in two skills costs on a small model, so it is now stated once, there. It was
never reached by either task in eval 15 either.

**Corpus support was again an anti-signal.** The register held 202 rows from 17 repos, and its
saturated centre, use `AsyncImage`, one `ImageLoader`, never `SubcomposeAsyncImage` in a lazy list
set `contentDescription`, is almost entirely absent from this skill, because that is what the
models already do. Both rules that separated came from the thin edges: two rows buried in a
project-scaffolding skill, and the user-supplied half of the axis, for which the corpus had ** zero
rows**.

One corpus claim was reversed by a web check before drafting: `respectCacheHeaders(false)` is Coil-2
advice, and Coil 3 inverted the default. Recorded in `registers/android/REVERSALS.md`.
