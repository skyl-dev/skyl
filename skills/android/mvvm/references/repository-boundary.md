# The repository boundary

Referenced by `mvvm REPO-3` and `REPO-4`.

## Where the interface goes

This is the whole of `REPO-4`, and it is a one-line difference that decides whether the layering is
real.

    // the boundary is decorative, ui still depends on data
    data/
      OrderRepository.kt          interface
      OrderRepositoryImpl.kt      implementation

    // the boundary is real, data depends on domain, ui depends on domain
    domain/
      OrderRepository.kt          interface, declared where it is used
    data/
      OrderRepositoryImpl.kt      implementation, depends on the interface above

The test: **delete the `data` package. Does `ui` still compile?** If yes, the arrow in
`core BOUND-1` is load-bearing. If no, you have a folder convention.

In a single-module app the compiler will not enforce this, which is exactly why it needs to be a
rule, nothing fails, and the coupling is invisible until someone tries to test the ViewModel or
swap the source.

## Repository decides, sources do

| | Repository | Data source |
|---|---|---|
| knows | that there are several origins | one origin |
| decides | cache vs network, write-through vs queue, who wins a conflict | nothing |
| contains | policy | I/O |
| in a test | real, with faked sources | faked, or real against an in-memory DB |

A repository containing a `@GET` call or a SQL string has absorbed a source. It still works, and
you can no longer fake the network without also faking the database.

**One origin means no split.** Two files where one would do is a design pretending to exist. `REPO-3`
is a `should` for this reason.

## A shape that satisfies both

    class SavedItemsRepository(
        private val remote: ProductRemoteSource,   // one origin, no policy
        private val local:  ProductLocalSource,    // one origin, no policy
    ) : SavedItemsRepository {                     // interface declared in domain

        fun products(): Flow<List<Product>> = local.observe()

        suspend fun refresh(force: Boolean = false) {
            if (!force && local.lastFetch().isFresherThan(1.hours)) return
            local.replaceAll(remote.fetch())        // the policy lives here, in one place
        }
    }

Three things are true of it, and each is a rule:

- the interface is declared where the ViewModel is, not beside this class, `REPO-4`
- the two origins are separate objects with no policy in them, `REPO-3`
- staleness and forcing are one path with a flag, not two fetch methods, `REPO-1`

## The failure this prevents

Two screens, each with a ViewModel that calls the API when online and the DAO when offline. Both
screens are correct in isolation. They agree because they happen to run the same logic, not because
anything guarantees it, and the first time one is changed, they diverge, and the bug appears in the
screen nobody edited.

That decision belongs in exactly one place. `REPO-1` is what puts it there.
