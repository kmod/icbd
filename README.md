# icbd

> ICBD is a defunct project, but I'm releasing the source code in case any one is interested.

ICBD is a static type analyzer and static compiler for Python.  It originated
from the desire at Dropbox to have additional type information for our growing
codebases, without requiring programmers to add type annotations.  There are
other static type analyzers for Python out there; the goal of ICBD was to
produce one that would work well on the Dropbox codebase, which meant
concretely:

- Handling untypable code as gracefully as possible
- "Acceptable" running times for multi-100k LOC codebases
- A plugin system for handling code that is inherently not statically analyzable

These goals were somewhat met, perhaps to the limits of using whole-program type
inference; the running time for the Dropbox codebase was about 15 minutes, which
I believe is better than alternatives but is not good enough for easy use.

The plugin system was able to get anecdotally get ICBD to successfully analyze a
sufficient fraction of the Dropbox codebase, though when typing failed, it was
difficult to tell why.

### Testing it out

You need to install pygments and simplejson to run ICBD; once you do, run

```
bash icbd/type_analyzer/run.sh icbd
```

to have ICBD analyze its own codebase (it doesn't do particularly well since
there are no plugins for its getattr usage).  You can see the output at
file:///tmp/icbd_icbd/icbd/type_analyzer/type_checker.html

### Technical approach

ICBD treats every Python expression as a constraint on the allowable types of
the program: `a = o.x` encodes the constraint that "a will have the type of o's
x attribute", `f(x)` encodes the constaint that "f accepts a type argument of
type type(x)", etc.  At a high level, ICBD then does a graph fixed-point
analysis to determine a set of types that satisfy the constraints, and emits
errors when types could not be found (ex: `a, b, c = 1, 2`).

The guessed types start at the BOTTOM type, and ICBD iteratively finds
unsatisfied constraints and raises the involved types to attempt to satisfy the
constraints.  In theory, if ICBD always raises types monotonically and to the
minimum satisfying type, this process will converge on a deterministic set of
lowest (or in some sense, most descriptive) types.

In practice, this is somewhat harder because the type constraints are dependent
on other types -- for example, attribute lookup dependencies can change based on
learning that an attribute may actually be a instance attribute.  This doesn't
seem to be that big a deal, though.

### Comparison to Python type analyzers

ICBD only analyzes a single version of each function, and assumes that any
combination of seen argument types could occur together.  For example, in this
snippet:

```python
def add_int_or_str(a, b):
    return a + b

add_int_or_str(1, 2)
add_int_or_str("hello ", "world")
```

ICBD will report an error, saying that an int cannot be added to a string.
Other analyzers will notice that add_int_or_str does not actually receive an
(int, str) combination of arguments and handle this correctly, but at an
exponentially-large cost.

This means that ICBD does not handle polymorphic functions very gracefully,
but in practice this seems to net be a common thing for applications code, and
the plugin system makes it possible to handle on a one-off basis.

#### Quick note about HM

People often ask "why don't you just apply HM (Hindley-Milner) which computes
the types ideally".  Yes, it's true that HM has some nice ideality properties,
but it only applies to a fairly-restrictive type system.  I'm not a type
theorist, but my understanding is that to properly represent the Python type
system you need

- Dependent types to represent attributes, and
- Rank-n polymorphism to represent global variables

both of which I believe make the inference problem undecidable.  (Is there
really any Haskell program that uses 0 type annotations?)

Of course in theory it's possible to translate Python code into, for example,
Haskell, but I don't see any reason to believe this can be done in an automated
way such that the generated Haskell has any meaningful relation to the original
Python.  For example, one could build an X86 emulator in Haskell, and use that
to run the Python interpreter, but the types on the Haskell program have no
usefulness to the original Python programmer.

# Compiler

ICBD also includes a static compiler, in icbd/compiler.  Assuming that the type
analyzer can come up with a complete set of types for your program (a big
assumption), in theory it should be possible to compile the Python as if it were
a more traditionally-typed static language.

In practice I doubt that real code can really be 100% typed; the ICBD compiler
served as the starting point for the [Pyston](https://github.com/dropbox/pyston)
project, which replaces it.
