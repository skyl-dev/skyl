# The permission-free path

Read this **before** declaring any `uses-permission`. Referenced by `permissions ASK-1`, `ASK-2`
and `LEAST-1`.

Every row is a feature stated as a user outcome, the way to ship it with no runtime permission, and
what that avoids. If the row fits, there is no permission to request, no rationale UI to design, no
denial state to handle, and nothing to declare on the store listing.

| The user wants to… | Permission-free path | Avoids |
|---|---|---|
| pick photos or videos | `ActivityResultContracts.PickVisualMedia` / `PickMultipleVisualMedia` | `READ_MEDIA_IMAGES`, `READ_MEDIA_VIDEO`, `READ_EXTERNAL_STORAGE` |
| pick a document or non-media file | Storage Access Framework, `ACTION_OPEN_DOCUMENT` | storage permissions |
| save a file the user chooses | `ACTION_CREATE_DOCUMENT` | `WRITE_EXTERNAL_STORAGE` |
| use files the app itself created | app-specific storage, or `MediaStore` for its own entries | storage permissions |
| take a photo | `ACTION_IMAGE_CAPTURE` | `CAMERA`, **but see below** |
| record a video | `ACTION_VIDEO_CAPTURE` | `CAMERA` |
| scan a QR or barcode | ML Kit **Google code scanner** (`GmsBarcodeScanning`), camera runs in Play services | `CAMERA` |
| pick a contact | the system contact picker | `READ_CONTACTS` |
| share one precise location, once | the system location button (`androidx.core.locationbutton`), **alpha** | holding `ACCESS_FINE_LOCATION` |
| be located roughly | `ACCESS_COARSE_LOCATION`, or a typed address | `ACCESS_FINE_LOCATION` |

The last two rows are `LEAST-1` rather than `ASK-1`: they do not remove the permission, they take a
weaker one. A list of places sorted by distance is correct on a neighbourhood-level fix, and asking
for precision to produce it buys a scarier dialog and a higher refusal rate for nothing.

| be recognised across launches | a persisted UUID, or an installation id from your backend | hardware-identifier permissions |
| find devices on the local network | a system discovery picker (`NsdManager` with the picker flag) | `ACCESS_LOCAL_NETWORK` |

Two rows carry a caveat worth reading in full.

## `CAMERA` and `ACTION_IMAGE_CAPTURE`, the declaration is the trap

`ACTION_IMAGE_CAPTURE` needs no permission. But **if `CAMERA` is declared in the manifest and not
granted, the same intent throws `SecurityException`.** The platform reads the declaration as a
statement of intent and enforces it.

So the failure mode is a permission you never request breaking a flow that never needed it, and the
declaration does not have to be yours. The manifest that ships is the *merged* one, and a dependency
can contribute `CAMERA`:

```
./gradlew :app:processReleaseMainManifest
# then read app/build/intermediates/merged_manifests/release/AndroidManifest.xml
```

If a library put it there and the app does not use that library's camera path, remove it with
`tools:node="remove"`. If the app does use it, the permission is the app's, and it needs the full
request path like any other.

## The photo picker, no version branch

`PickVisualMedia` is backported through Google Play services to Android 4.4, and where it is
unavailable it **falls back to `ACTION_OPEN_DOCUMENT` on its own.** A `Build.VERSION.SDK_INT >=
TIRAMISU` branch around it is dead code that only removes the fallback. `isPhotoPickerAvailable()`
exists for telling the user which experience they will get, not for deciding whether to call the
contract.

Where a custom gallery UI is genuinely required, `READ_MEDIA_VISUAL_USER_SELECTED` lets the user
grant a subset rather than the library, and that subset is a partial grant, which is `GRANT-3`.

## The denial state machine

The public API cannot distinguish two of these four states, which is what `ASK-4` is about.

| State | `checkSelfPermission` | `shouldShowRequestPermissionRationale` | What the UI should do |
|---|---|---|---|
| never asked | denied | **false** | explain, then ask |
| granted | granted | false | use it |
| denied once | denied | true | explain why it matters, then ask again |
| denied twice, permanent | denied | **false** | no dialog will appear; offer Settings, or degrade |

Rows one and four are identical through the API and need opposite UI, so the app has to remember
whether it has ever asked. Internally the system flags them differently, `USER_SET` after one
denial, `USER_FIXED` after two, and that is visible while debugging:

```
adb shell dumpsys package <package> | grep -A1 <PERMISSION>
adb shell pm revoke <package> android.permission.CAMERA   # back to "never asked"
adb shell pm grant  <package> android.permission.CAMERA
```

After the second denial the system dialog never appears again for the life of the install. A
re-request returns denied immediately, so a retry loop is a frozen screen rather than a second
chance.
