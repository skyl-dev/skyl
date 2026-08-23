# Keys, and what leaves the device

Referenced by `security STORE-1`, `KEY-1`, `KEY-2`, `OUT-1` and `OUT-2`.

## Storing a secret without the deprecated wrapper

`androidx.security:security-crypto`, `EncryptedSharedPreferences` and `EncryptedFile`, was
deprecated in June 2025. It still works, nothing warns, and nearly every tutorial still teaches it.
Do the two steps yourself instead.

```kotlin
// 1. one key, created once, living in the Keystore
private fun key(): SecretKey {
    val ks = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    (ks.getEntry(ALIAS, null) as? KeyStore.SecretKeyEntry)?.let { return it.secretKey }

    return KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore").apply {
        init(
            KeyGenParameterSpec.Builder(
                ALIAS
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .build()
        )
    }.generateKey()
}
```

The lookup before the generate is the whole rule. Without it:

```kotlin
// WRONG
// WRONG because every launch makes a new key, and every value written by the last
// launch becomes permanently unreadable. Nothing reports it.
private val key = KeyGenerator.getInstance("AES", "AndroidKeyStore").apply { ... }.generateKey()
```

```kotlin
// 2. ciphertext into an ordinary store, the IV travels with it
fun put(name: String, value: String) {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding").apply { init(Cipher.ENCRYPT_MODE, key()) }
    val blob = cipher.iv + cipher.doFinal(value.toByteArray())
    prefs.edit().putString(name, Base64.encodeToString(blob, Base64.NO_WRAP)).apply()
}
```

The IV is not secret and must be stored; a fixed IV with GCM breaks the mode outright.

## Key lifetime

| Want | Do |
|---|---|
| a value that survives sign-out | one long-lived key, created once |
| a value unreadable after sign-out | one key per session, **destroyed** at sign-out, deleting the key is the erase |
| a value gated on biometrics | `setUserAuthenticationRequired(true)` and unlock via `CryptoObject` |
| a key per record | don't, Android 17 caps an app targeting API 37 at **50,000** keys |

Destroying a key is the cheapest way to make data unreadable: one `deleteEntry` beats walking every
row. That is the one case where a key per session is correct rather than a bug.

## Backup

Auto Backup is **on by default** for anything targeting API 23+. Both attributes are required, they cover different platform versions.

```xml
<application
    android:allowBackup="true"
    android:dataExtractionRules="@xml/data_extraction_rules"   <!-- API 31+ -->
    android:fullBackupContent="@xml/backup_rules">             <!-- API 30 and below -->
```

```xml
<!-- res/xml/data_extraction_rules.xml -->
<data-extraction-rules>
    <cloud-backup>
        <exclude domain="sharedpref" path="session.xml" />
    </cloud-backup>
    <device-transfer>
        <exclude domain="sharedpref" path="session.xml" />
    </device-transfer>
</data-extraction-rules>
```

`cloud-backup` and `device-transfer` are separate sections and an exclusion in one does **not** apply
to the other. A token excluded from cloud backup and not from device transfer still arrives on the
new phone.

**Always exclude anything encrypted with a Keystore key.** The key is device-bound and does not
travel; the restored ciphertext is unreadable forever, on a device where the user has no way to
understand what happened. If a value must survive a device change, it belongs behind a server, not
behind a device-bound key.
