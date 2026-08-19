# Skyl

**skyl** (like *skill*) — a composable registry of AI agent skills.

Most published agent skills are one large markdown file covering an entire domain, so they are
mostly irrelevant to any given project. Skyl's proposition is that expertise decomposes along
orthogonal axes, and a project should load only the intersection that applies to it.

```
android/core + kotlin + compose      ← new Compose app
android/core + java + xml            ← legacy app, same core
web/core + typescript + react
  + appwrite/core + appwrite/node    ← service layer composes sideways
```

This repository holds the skills, the format spec, and the contribution standard. The site and
the CLI live in `skyl.dev`.

## Status

Pre-alpha. Nothing here is stable. The axis model is currently being validated against a
hand-written `android/*` family before the spec is written.

## Layout

```
skills/        curated skills, one directory per family
incubating/    uncurated submissions, with a promotion path
spec/          format, axis vocabulary, contribution standard
scripts/       index / detect / marketplace generators
```

## License

MIT. See [LICENSE](./LICENSE).
