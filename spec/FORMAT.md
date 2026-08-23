# Skill format

A skill is one directory: a `SKILL.md`, and optional `references/`.

```
skills/android/kotlin/
├── SKILL.md
└── references/
    └── cancellation.md
```

## Frontmatter

```yaml
---
name: android/kotlin          # family/skill, the installable identity
axis: language                # core | language | framework | service | topic
family: android
requires: [android/core]      # skills that must be installed alongside
version: 1.1.0                # semver; a retirement is a minor bump
authors: [ahmmedrejowan]
agent_sections: [rules]       # which sections an installer gives the agent
retired: [ASYNC-1, TYPE-2]    # rule ids removed, and why, in Provenance
detect:                       # how a project is recognised
  gradle_dependency: ["org.jetbrains.kotlin:kotlin-stdlib"]
---
```

**`agent_sections` is the load-bearing field.** The file is written for two readers. An installer
gives the agent only the listed sections; everything else, `## Why`, `## Pitfalls`
`## Provenance`, is for the human deciding whether to trust the skill. That split is what lets a
skill carry its own evidence without spending the agent's context on it.

## Versioning

**Every skill starts at `1.0.0` when it is first published here.** Work before publication happened
in a private workspace and its version numbers were internal bookkeeping, not a release history, so
they are not carried over.

After publication, semver applies to what an installer receives:

| change | bump |
|---|---|
| a rule retired, added, or its instruction changed | minor |
| wording, `Why`, `Pitfalls`, `Provenance`, references | patch |
| a rule id renamed, or `requires` changed | major |
| `detect` widened or narrowed | minor |

Evidence is anchored to **evals**, not to versions, because the evals are published and the
pre-publication versions were not. A `## Provenance` entry says *"eval 19 measured all four"*, never
*"v1.3.0 added"*.

`detect` keys are family-defined and resolved by the index. Current keys: `gradle_dependency`
`gradle_plugin`, `file`, `manifest_element`, `manifest_attribute`.

## Sections

| section | audience | required |
|---|---|---|
| `## Rules` | the agent | yes |
| `## Why` | the human | yes for a shipped skill |
| `## Pitfalls` | the human | yes for a shipped skill |
| `## Provenance` | the human | yes for a shipped skill |

## A rule

Three parts, always:

```markdown
- **ASYNC-4** `must`: A read that can be re-triggered, a query, a filter, a refresh, is
  cancelled by the operator built for it, not by tracking jobs by hand.
  *Why:* hand-tracked jobs race their own cancellation on fast input. And cancelling a write does
  not un-send it, the request may already have reached the server.
  *Not when:* every emission must be processed, where the operator is losing work by design.
```

**A decidable instruction.** Not "use flows appropriately", a reader must be able to look at a
file and say yes or no. Undecidable text is unfalsifiable, and unfalsifiable text is unactionable.

**A `Why` that names the failure** not the principle. The reader has to be able to recognise the
bug in the wild.

**A `Not when`.** Almost nobody writes these, and their absence is what turns a rules file into a
nitpick generator. A rule without a stated boundary gets applied everywhere.

## Rule ids

`PREFIX-N`, stable for the life of the skill. **Ids are never reused.** A retired rule's id is
listed in `retired:` and stays retired, because published evidence and cross-references point at it.

## Priority

`must`, the failure is silent, expensive, or hard to reverse.
`should`, real exceptions exist, and the rule says to name yours.

## Cross-references

A rule may cite another skill's rule as `` `android/core WORK-3` ``. Every such reference is
resolved by `scripts/xrefcheck.py` in CI; a reference to a rule that does not exist fails the
build. Layers must not restate each other, see [METHOD.md](./METHOD.md).
