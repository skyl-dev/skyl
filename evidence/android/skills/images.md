# Evidence: `android/images`

Images that arrive at runtime: fetched from a URL, picked by the user, or decoded from a file.

## What was run

One eval on Haiku 4.5 and Sonnet 5, two brownfield tasks, control against `+core` against
`+core+images`.

## What loading the skill changed

Two rules, both on Haiku, both consistent across runs. Sonnet handled both unaided.

**Adding the artifact that actually fetches.** The unaided task-A run is the sharpest control arm in
this family. It keys its list, reserves each slot from the item's own aspect ratio, and labels every
image, and it loads nothing at all: the image library was present and the network artifact was not,
so every URL resolved to nothing. Blank boxes with titles underneath, no crash, no log line. It would
pass review and ship a screen that does not work.

**Decoding at display size on the upload path.** Re-encoding is not downscaling: a twelve-megapixel
photo compressed at quality 95 is still twelve megapixels.

## What the tested models already handle

Reserving an image's space in a list, and applying EXIF orientation, were done unaided in every run,
the second by an unaided run writing a complete handler with all four rotation and flip cases. Both
were dropped.
