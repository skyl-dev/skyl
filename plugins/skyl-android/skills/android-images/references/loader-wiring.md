# Wiring the image loader

Referenced by `images LOAD-1`, `LOAD-2`, `CACHE-1` and `CACHE-2`.

## The loader has its own HTTP stack

This is the fact everything else follows from. An image library does not use your `OkHttpClient`
because it happens to be in the graph, it builds its own unless you hand it yours.

What silently does not apply to image requests when you skip that step:

| Configured on your client | Reaches images? |
|---|---|
| authorization interceptor | no |
| certificate pinning | no |
| custom headers, user agent | no |
| timeouts | no |
| proxy / alternative routing | no |
| connection pool | no, a second pool, second handshakes |
| logging and tracing | no |

The signature failure: **every API call authenticates and every image 401s.**

## Coil 3 fetches nothing until you say how

Coil 3 ships **no network support by default**. Without a network artifact, an `https` model
resolves to nothing, no exception, no log line, an empty composable.

```kotlin
// build.gradle.kts, coil-compose alone does not fetch URLs
implementation("io.coil-kt.coil3:coil-compose:3.5.0")
implementation("io.coil-kt.coil3:coil-network-okhttp:3.5.0")   // Android / JVM
// Compose Multiplatform targets use coil-network-ktor3 instead
```

## One loader, built once, holding your client

```kotlin
// WRONG, a second network stack, and a second memory cache
// WRONG because the AuthInterceptor on the app's client never sees an image request.
@Composable
fun Avatar(url: String) {
    val loader = ImageLoader.Builder(LocalPlatformContext.current).build()
    AsyncImage(model = url, imageLoader = loader, contentDescription = null)
}

// RIGHT, provided once, and installed as the app-wide loader
@Provides @Singleton
fun imageLoader(
    @ApplicationContext context: Context
    client: Provider<OkHttpClient>): ImageLoader = ImageLoader.Builder(context)
    .components { add(OkHttpNetworkFetcherFactory(callFactory = { client.get() })) }
    .build()

class NotesApp : Application(), SingletonImageLoader.Factory {
    @Inject lateinit var imageLoader: Provider<ImageLoader>
    override fun newImageLoader(context: PlatformContext) = imageLoader.get()
}
```

`Provider` rather than a direct instance: `newImageLoader` can run before the container has
materialised the singleton.

Building a loader per screen also discards the memory cache the previous one held, so images already
decoded are fetched and decoded again.

## Cache identity

The cache key is the URL string. Ask what identity the entry actually has:

| The URL | The image | What to do |
|---|---|---|
| changes every response (presigned, expiring, cache-buster) | same | set the key to the stable id |
| never changes | replaced (new avatar, re-upload) | change the key with the content, or evict on write |
| changes with the bytes (content-addressed) | changes with it | nothing, the default is right |

```kotlin
ImageRequest.Builder(context)
    .data(photo.url)              // presigned, minted per response
    .memoryCacheKey(photo.id)     // stable identity
    .diskCacheKey(photo.id)
    .build()
```

**Coil 3 ignores `Cache-Control` by default** and writes every response to disk. Honouring headers
needs the `coil-network-cache-control` artifact and an explicit strategy, so a server that
carefully sets max-age has no effect on the device until you opt in. Decide invalidation on the
client; do not assume HTTP caching is doing it.
