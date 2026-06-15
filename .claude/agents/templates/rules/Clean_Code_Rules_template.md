# Clean Code Rules

**Applies to:** Developer (before writing source code), Technical Lead (during code review)  
**Skip for:** documentation-only, API spec, Dockerfile, docker-compose, migration SQL, or config-only stories

---

## 1. Meaningful Names

### Use Intention-Revealing Names
- A name should tell you *why* it exists, *what* it does, and *how* it is used.
- If a name requires a comment, the name does not reveal its intent.
- For measurements, include what is measured and the unit: `elapsedTimeInDays`, `fileAgeInDays`.

### Avoid Disinformation
- Do not use names whose common meaning conflicts with intent (e.g., do not call something `accountList` if it is not actually a `List`).
- Do not encode container type into the name at all.
- Avoid names that differ only subtly — nearly identical names are nearly impossible to distinguish at a glance.

### Make Meaningful Distinctions
- Number-series naming (`a1`, `a2`) is noninformative — avoid it.
- Noise words (`Info`, `Data`, `Object`, `Variable`, `Table`) add nothing — `ProductInfo` vs `Product` means nothing different.
- If names must be different, they must *mean* something different.

---

## 2. Functions

### Do One Thing
- A function should do one thing, do it well, do it only.
- If you can extract another function from it with a name that is not merely a restatement of its implementation, it is doing more than one thing.
- Functions that do one thing cannot be reasonably divided into sections.

### The Stepdown Rule
- Every function should be followed by those at the next level of abstraction — code reads top-to-bottom, descending one abstraction level at a time.
- Read it as a set of *TO* paragraphs: *"To do X, we do A, then B, then C."*

### Have No Side Effects
- A function should do exactly what its name says — nothing else.
- Avoid output arguments (taking input, mutating it, returning nothing) — readers do not know if an argument is mutated without checking the signature, which is a cognitive break.

### Error Handling
- Prefer exceptions over returning error codes — error codes force nested `if` chains.
- Extract `try/catch` bodies into their own functions.
- A function that handles errors should do nothing else — `try` should be the first word and nothing should follow the `catch/finally` block.

### Conclusion — When to Apply These Rules
- Do not try to apply all rules on the first pass. Write it to work correctly first.
- Cover with tests, then refactor toward these rules.
- Reason: over-cleaning code that later gets changed is wasted effort.

---

## 3. Code Comments

- Avoid comments where possible — programmers cannot realistically maintain them and they become misinformation over time.
- The proper use of a comment is to compensate for a failure to express intent in code. Before writing a comment, try harder to find a better name or extract a function.
- If a block of code needs a comment to explain what it does, extract it into a well-named function instead.

### Good Comments (acceptable)
- **Legal comments** — copyright and authorship required by corporate standards.
- **Explanation of intent** — explains *why* the code is written this way, not *what* it does.
- **Clarification** — translates an obscure argument or return value when you cannot alter the code (e.g., standard library). Use with care — verify accuracy.
- **Warning of consequences** — warns about a non-obvious constraint (e.g., not thread-safe). Fix the root cause if possible; comment if not.
- **TODO comments** — marks known incomplete work or a planned change. Do not leave them indefinitely.
- **Amplification** — highlights something that looks inconsequential but is actually critical.
- **Javadoc / godoc on public APIs** — document public interfaces so consumers understand the contract.

### Bad Comments (avoid)
- **Mumbling** — only the author understands it; forces readers to cross-reference source code.
- **Redundant comments** — restates what the code already clearly says.
- **Misleading comments** — incorrect information about what the code does.
- **Mandated comments** — blanket rules that every function must have a doc comment; produces noise.
- **Journal comments** — changelog entries in code; use Git history instead.
- **Noise comments** — restate the obvious and provide no new information.
- **Comment when a function or variable would do** — if renaming or extracting makes the intent clear, do that instead.
- **Closing brace comments** — indicates the function is too long; shorten it instead.
- **Commented-out code** — delete it; Git will preserve it if it is ever needed again.
- **Nonlocal information** — a comment should describe the code immediately around it, not system-wide behaviour.
- **Inobvious connection** — the link between a comment and the code it describes must be obvious without further investigation.

---

## 4. Object and Data Structure

- **Objects** hide data behind abstractions and expose functions that operate on it. **Data structures** expose data and have no meaningful functions.
- **Procedural code** (data structures) makes it easy to add new functions without changing existing data structures — but hard to add new data structures because all functions must change.
- **OO code** (objects) makes it easy to add new types without changing existing functions — but hard to add new functions because all classes must change. Choose the style that fits what is more likely to change.
- Avoid hybrid structures that are half object, half data structure — they expose data *and* have significant behaviour. They are the worst of both worlds.
- Hiding implementation is not just putting functions in front of variables — it is exposing abstract interfaces that let callers manipulate the essence of the data without knowing its implementation.
- **Law of Demeter** — objects should expose behaviour and hide data; do not reach through an object to manipulate the internals of another.

---

## 5. Error Handling

- Use exceptions over return codes — always.
- Prefer **unchecked exceptions**; checked exceptions force every method in the call stack to declare them.
- Each exception should carry enough context to identify the source and type of failure.
- Define **few, common exception types** per area — use the exception's payload to distinguish errors, not separate classes. Use different exception classes only when you need to catch one and let the other pass through.
- **Wrap third-party APIs** in your own class that translates their exceptions into your own types — decouples you from the vendor, easier to mock in tests, consistent API for callers.
- **Special Case Pattern** — instead of throwing an exception for a predictable edge case, return a special case object that encapsulates the default behavior so callers don't need special-case logic.
- **Never return null** — throw an exception or return a Special Case object instead. Returning null forces null-checks on every caller.
- **Never pass null** — always null-check public method inputs; private methods can trust internal callers.

---

## 6. Boundaries

- Don't pass third-party interfaces (e.g., `Map`) freely across your system — wrap them in a class that hides the boundary type.
- Write **learning tests** to explore a third-party API before integrating it — controlled experiments that verify your understanding of the API.
- When a third-party interface is unclear or unstable, define your own interface that matches what you need, then write an **Adapter** that calls the third-party code. This isolates your app from the vendor and makes unit testing easier.
- Keep third-party references in as few places as possible — fewer maintenance points when the API changes.

---

## 7. Unit Tests

- Test code is as important as production code — keep it as clean.
- Tests are what make code safely changeable. Without tests, every change is a potential bug.
- Clean tests are readable above all else — use **Build-Operate-Check** (Arrange-Act-Assert) structure.
- Extract setup, operation, and assertion details into helper functions — the test body should only express intent, not mechanics.
- Build a **domain-specific testing API** for your test suite so tests read like specifications.
- **One concept per test** — minimize asserts per concept, not necessarily per test function.
- Clean tests follow **F.I.R.S.T:**
  - **Fast** — tests should run quickly
  - **Independent** — tests must not depend on each other or share state
  - **Repeatable** — must run in any environment without a network or external dependency
  - **Self-Validating** — pass or fail with a boolean output; no manual log inspection
  - **Timely** — written just before the production code that makes them pass

---

## 8. Classes

### Class Should Be Small
- Measure class size by **responsibilities**, not lines of code.
- If you can't describe a class in ~25 words without using "if," "and," "or," or "but" — it has too many responsibilities.
- Names like `Manager`, `Processor`, or `Super` are warning signs of too many responsibilities.

### Single Responsibility Principle (SRP)
- A class should have one, and only one, reason to change.
- Prefer many small, focused classes over a few large ones.

### Cohesion
- Each method in a class should manipulate one or more of its instance variables — high cohesion means methods and variables hang together as a logical whole.
- When a group of methods only share a subset of instance variables, those methods want to be their own class — split them.

### Organizing for Change
- Organize classes so adding or changing behavior touches as few classes as possible.
- Private methods that apply only to a small subset of the class are a hint the class needs splitting — extract those methods and related variables into a subclass.

### Isolating From Change (DIP)
- Depend on abstractions (interfaces), not concrete implementations.
- This decouples classes from volatile details and makes unit testing easier by enabling mocks.

---

## 9. Systems

### Separate Construction from Use
- Separate startup wiring (object creation, dependency setup) from runtime logic — don't mix them in the same method.
- Lazy initialization (`if null, create`) hides dependencies, makes testing harder, and ties you to one concrete type.
- Solutions: **Main separation** (build all objects in `main`, pass them in), **Abstract Factory** (app controls when, factory controls how), or **Dependency Injection** (container wires everything).

### Scaling Up (Incremental Architecture)
- Don't do Big Design Up Front — build only what today's stories need, then refactor and expand incrementally.
- Software architectures can grow if concerns are properly separated.
- Avoid cross-cutting concerns spread across many objects — isolate them using proxies or AOP.

### Optimal System
- Start simple and decoupled, add infrastructure as needed — make just-in-time decisions at the module level.
- Always use the simplest thing that can possibly work.
- Obscured domain logic hides bugs and slows delivery — systems must be clean too.

---

## 10. Simple Design Rules

*(Priority order — highest to lowest)*

1. **Runs All Tests** — a system that can't be verified shouldn't be deployed. Writing tests naturally pushes you toward SRP, DIP, and low coupling.
2. **No Duplication** — duplication is the primary enemy of good design. Extract shared logic; apply Template Method for algorithmic duplication. Eliminate even tiny duplication.
3. **Expressive** — code should clearly express the author's intent. Use good names, small functions and classes, standard design pattern names, and well-written tests. Take time to refactor for readability.
4. **Minimal Classes and Methods** — don't over-apply the above rules to the point of creating too many tiny classes. Keep counts low, but this is the lowest-priority rule of the four.

---

## 11. Successive Refinement

- To write clean code, you must first write dirty code — then clean it.
- To decide if code needs refactoring, ask: if we need to scale this up, would we have to change a lot of existing code? If yes, refactor.
- When multiple types share the same methods, extract a parent class with the shared methods and make each type a subclass.
- Much of good software design is about **partitioning** — creating appropriate places to put different kinds of code. Separation of concerns makes code simpler to understand and maintain.

---

## 12. Design Smells

### Temporal Coupling
- Occurs when two or more members of a class must be called in a specific order — clients have to know the implicit sequence.
- Fix: pass required dependencies via constructor or abstract factory so the coupling is explicit, or expose them as method parameters so callers know what's needed upfront.

---

## Version

**Version:** 1.4 — Added §3 Code Comments, §4 Object and Data Structure; renumbered §5–§12  
**Created:** 2026-06-10  
**Source:** Clean Code (Robert C. Martin) — All chapters
