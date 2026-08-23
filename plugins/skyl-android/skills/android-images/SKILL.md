---
name: android-images
description: "Images that arrive at runtime, fetched or picked or decoded: caching, sizing, cancellation, and what a picker actually hands back. Use when images are part of the product."
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
