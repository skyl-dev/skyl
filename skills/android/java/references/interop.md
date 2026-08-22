# The Java–Kotlin seam

Referenced by `java NULL-1`, `INTEROP-1` and `INTEROP-2`.

Most Android codebases are mixed, and will be for years. Almost everything that goes wrong at the
seam is invisible from the Kotlin side, which is why it needs to be written down.

## Platform types: the guarantee that quietly switches off

Kotlin's null safety holds for types Kotlin can reason about. Unannotated Java is not one:

    // Java, no annotation
    public String getName() { … }          // may return null

    // Kotlin, all of this compiles
    val n: String = user.getName()          // no warning
    n.length                                // no check
    repository.save(n)                      // passed on as non-null

`getName()` arrives as `String!`, a *platform type*. Kotlin will let you treat it as non-null, and
the compiler has no information to object with. The null surfaces wherever the value is finally
dereferenced, in Kotlin code that never declared it nullable.

One annotation restores the guarantee:

    @Nullable public String getName() { … }   // now String? in Kotlin, and checked

**This is the highest-value annotation in a mixed codebase.** It is not documentation; it is the
switch that turns the other half of the language back on.

### Which annotation package

Use **`androidx.annotation`** (`@Nullable`, `@NonNull`) in Android code. It is what the tooling
lint and Android Studio inspections are built around, and it is understood by the Kotlin compiler.

Worth knowing where this is going: **JSpecify** reached 1.0 in July 2024 as a cross-vendor
specification, Google, JetBrains, Eclipse and Uber had each shipped their own flavour of nullness
annotations, and the fragmentation is what it exists to fix. The Kotlin compiler recognises JSpecify
annotations and, since 2.1.0, reports nullness problems found through them as errors by default.
JSpecify also annotates *type* positions, so it can express things a declaration annotation cannot, nullability of a type argument, or of an array component.

For Android today `androidx.annotation` remains the practical answer. Do not mix packages within a
module; consistency matters more than the choice.

## What Java sees when Kotlin changes

| Kotlin | Java sees | Fix |
|---|---|---|
| `companion object { fun get() }` | `Foo.Companion.get()` | `@JvmStatic` |
| `const val TIMEOUT = 30` in a companion | `Foo.Companion.getTIMEOUT()` | `@JvmField` |
| `fun f(a: Int, b: Int = 0)` | one method, both parameters required | `@JvmOverloads` |
| `fun f()` that throws `IOException` | no checked exception declared | `@Throws(IOException::class)` |
| `var name: String` | `getName()` / `setName()` | expected, do not fight it |

None of these are visible from the Kotlin file. It compiles, it looks correct, and the break is in a
Java file nobody opened. That asymmetry is the whole problem: **the cost of forgetting lands
somewhere other than where the decision was made.**

## Converting: keep the surface still

While Java callers remain, a converted class keeps its shape, same visibility, same names, same
exception types. `internal` is not `package-private`, and Kotlin's default `public` is not the
`protected` the Java had.

The reason is reviewability. A conversion is safe to merge because a reviewer can confirm nothing
changed. Change the surface and the diff spreads across every caller, and it stops being possible to
tell a translation from an edit.

## What the automatic converter leaves

It is a syntactic tool and does not pretend otherwise. Expect to fix, every time:

- **platform types** where the Java had annotations, it cannot infer what was not written
- **`!!`** wherever it could not prove non-null, which is the converter admitting it does not know
- **`var`** for fields that were effectively final
- **nullable types on everything from an unannotated library** cascading through the file
- **lost `@JvmStatic` / `@JvmField`** on anything that was `static` and is now in a companion

Review the output as new code. It compiles; that is the only claim it makes.
