# Choosing where a value lives

Referenced by `db STORE-1` and `STORE-3`.

## The shape test

| The value is | It lives in | Because |
|---|---|---|
| a scalar or flag, theme, onboarding-seen, last sync time | `DataStore` | typed, async, observable |
| queried, filtered, sorted, or related to other rows | the database | that is what a query engine is for |
| large and opaque, an image, a document, an export | the filesystem, path in the database | rows are not blob stores |
| a secret, token, key, credential | **not decided here** see `android/security` | the store is not the protection |

Ask what you will do with the value in six months, not what is fastest to write now. A flag that
becomes a filter becomes a query, and moving it later is a migration.

## `DataStore` over `SharedPreferences`

`SharedPreferences` is a synchronous API in front of an XML file:

- the **first read blocks** the calling thread while the file loads;
- **`apply()` is asynchronous and reports nothing** a failed write is silent, and the value you
  read back is the one in memory, so the failure surfaces after the next process start;
- **`commit()` blocks** to give you a result;
- there is **no type safety** a wrong-typed read throws at runtime, and a mistyped key returns the
  default, which looks exactly like a value someone chose.

`DataStore` addresses all four: it is coroutine-based, exposes reads as a `Flow`, surfaces write
failures to the caller, and, with `Proto DataStore`, has a schema.

**Do not migrate an existing widely-used preference just to comply.** Migration is a data-loss risk
in exchange for tidiness. Wrap it behind the class `STORE-2` asks for, and let new values go to
`DataStore`.

## The one class that owns the keys

    // not this, a string key at four call sites is four chances to mistype it
    prefs.getBoolean("has_onboarded", false)

    // this
    class AppSettings(private val store: DataStore<Preferences>) {
        private val HAS_ONBOARDED = booleanPreferencesKey("has_onboarded")
        val hasOnboarded: Flow<Boolean> = store.data.map { it[HAS_ONBOARDED] ?: false }
        suspend fun setOnboarded() = store.edit { it[HAS_ONBOARDED] = true }
    }

A mistyped key does not fail. It returns the default, and the default is indistinguishable from a
real value, so the bug presents as "the setting reset itself".

## Secrets: what changed

`androidx.security:security-crypto`, the library providing `EncryptedSharedPreferences` and
`EncryptedFile`, was **deprecated at 1.1.0-beta01 on 4 June 2025**. The release note:

> Deprecated all APIs in favour of existing platform APIs and direct use of Android Keystore.

This matters more than a normal deprecation for three reasons:

1. **It is still the top answer everywhere.** Years of documentation, courses and answers recommend
   it, and most have not been updated. Anything trained on that material recommends it confidently.
2. **Nothing fails.** It resolves, compiles, and encrypts. An app shipped on it is running
   unmaintained cryptography with no signal that anything is wrong.
3. **A community fork exists** and is explicitly not produced, endorsed or supported by Google, which is a different risk, not a solution to this one.

What replaces it is `android/security`'s subject. What belongs here is only this: **do not let the
store choice be made by reaching for the deprecated wrapper first.**

Source: [Security | Jetpack | Android Developers](https://developer.android.com/jetpack/androidx/releases/security)
