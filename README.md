# Skyl

**skyl** (like *skill*), a composable registry of AI agent skills.

Most published agent skills are one large markdown file covering an entire domain, so most of what
they contain is irrelevant to any given project. Skyl's proposition is that expertise decomposes
along orthogonal axes, and a project should load only the intersection that applies to it.

```
android/core + kotlin + compose      ← a new Compose app
android/core + java + xml            ← a legacy app, same core
web/core + typescript + react
  + appwrite/core + appwrite/node    ← a service layer composes sideways
```

## What makes this different

Every rule here was **measured before it shipped** and rules that failed to measure were removed.

| | |
|---|---|
| skills | **13** (`android`) |
| rules | **146** |
| rules **retired** because a model already did it unprompted | **17** |
| recorded runs | **490** across 26 evals |
| models | Opus 5 · Sonnet 5 · Haiku 4.5 · qwen3.7-max |
| harnesses | `claude` CLI · `opencode` |
| providers | Anthropic · OpenRouter |

The retirements are the point. A rule is not admitted because it is *true* (most published skill
content is true) but because a model **gets it wrong without being told**. When a control arm
already does the right thing, the rule costs context and buys nothing, so it goes.

See [EVIDENCE.md](./EVIDENCE.md) for what was run, and [`evidence/`](./evidence) for what was
found, skill by skill.

## How a skill is curated

Four tests, in order. A rule ships only if it passes all four:

1. **Does the model get this wrong unprompted?** If it already does it, the rule displaces one that
   would have worked.
2. **Does a linter or the compiler already catch it?**
3. **Would 900 of 1000 projects hit it?** Interesting is not the bar.
4. **Is it checkable at every token, or a deferred action?** Deferred actions are not rules.

Then it is written, drafted against a corpus, checked against primary sources, and put in front of a
control arm that was not told the rule. What that produced is in [EVIDENCE.md](./EVIDENCE.md).

**A finding that shapes everything here:** corpus support is an *anti-signal*. The more repositories
that document a practice, the more likely a model already follows it, because the corpus and the
model's training data are the same material. Rules drawn from what everyone writes down measure
nothing. Every confirmed result in this registry came from a control arm or a primary source, and
never from corpus frequency.

## Status

Pre-alpha. The `android` family is complete and measured; the spec is being written from it rather
than ahead of it. Nothing is stable, and the CLI does not exist yet.

## Layout

```
skills/        curated skills, one directory per family
incubating/    submitted, not yet measured
evidence/      per-skill eval results, seeds, and arm prompts, replayable
spec/          format, axis vocabulary, admission bar, method
scripts/       index / validate / gates
```

## License

MIT. See [LICENSE](./LICENSE).
