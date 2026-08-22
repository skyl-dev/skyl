# Evidence: `android/images`

6 rules, 3 retired. Two separations, and the sharpest control arm in the family.

## What was run

| eval | models | arms | runs |
|---|---|---|---|
| 15 | Haiku 4.5, Sonnet 5 | control / +core / +core+images | 24, two brownfield tasks |

## What separated

| rule | Haiku ctl → +core → +images | Sonnet |
|---|---|---|
| `LOAD-2` add the artifact that actually fetches | **0/2 → 0/2 → 2/2** | 2/2 in every arm |
| `MEM-1` decode at display size | **0/2 → 0/2 → 2/2** | 2/2 in every arm |

## The control arm worth reading

The task-A control produced **good-looking code that loads no images at all.** It keys the list, it
reserves each slot from the item's own aspect ratio, it labels every image:

```kotlin
items(state.photos, key = { it.id }) { photo -> PhotoItem(photo) }
...
Box(modifier = Modifier.fillMaxWidth().aspectRatio(photo.width.toFloat() / photo.height))
    AsyncImage(model = photo.url, contentDescription = photo.title, ...)
```

The image library was present and the artifact that fetches over the network was not, so every URL
resolved to nothing: blank boxes with titles underneath, no crash, no log line. **It would pass
review and ship a screen that does not work.**

## What was retired

| rule | why |
|---|---|
| reserve the image's space in a list | satisfied in 12 of 12 task-A runs, both models, every arm |
| apply EXIF orientation | the Haiku **control** wrote a complete handler with all four rotation and flip cases |
| a test that renders an image does not fetch one | a subset of `android/testing`'s rule. Two skills carrying one hazard degrades the smaller model. |

## Scoring errors, published

Three in one eval, and the first pass **would have retired one of the two rules that worked.**

`.compress(JPEG, 95)` was counted as downscaling. It is re-encoding: a twelve-megapixel image
compressed at quality 95 is still twelve megapixels. `Modifier.size(96.dp)` in the seed's own screen
was counted as a decode size. A rotation matrix call was counted as a resize.

All three were found by reading the generated code. The fixtures written beforehand passed every one
of them, because they were too clean to contain the near miss.
