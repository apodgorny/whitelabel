# WhiteLabel invariants 4

## Python carrier law

- Any `.py` file that is loaded through `py.py` is an own-module source file by law.
- Such a file must define exactly one loadable class with the required `snake_to_camel` relationship between filename and class name.
- That class must extend `wl.Module`.
- If a `.py` file does not satisfy that contract, it is not a valid WL carrier and must not load through `WL` or `O`.

## Scope

This file is a supplement to `whitelabel_invariants1.md`, `whitelabel_invariants2.md`, and `whitelabel_invariants3.md`.
It captures later refinements established in the current design line.
If an item here conflicts with an earlier note, this supplement is newer for that specific point.

---

## Canonical published-face law

- A library class such as `WL`, `O`, or `LLM` may expose a lowercase published face in module scope.
- The lowercase symbol is a derived projection of the class name.
- Example:
  - `WL` -> `wl`
  - `O` -> `o`
  - `LLM` -> `llm`
- The lowercase symbol must not be treated as an independent source of truth.
- The class name remains the single naming source of truth.

Equivalent wording:

- uppercase class form is canonical in Python space
- lowercase face is canonical in usage space
- one name, two projections

---

## Anti-duplicate-name law

- Manual patterns such as:

```python
wl = WL()
```

introduce a second manually-maintained naming source.
- This is considered inferior to derived publication from class creation.
- The system should prefer automatic publication over hand-maintained alias lines.

---

## Metaclass publication law

- If lowercase published faces are used, publication belongs in metaclass class-creation flow.
- Publication is part of library birth, not part of ordinary runtime calls.
- Therefore publishing from `WLMeta.__new__` is preferred over publishing from `WL()` calls.

Equivalent wording:

- names are born with the class
- names are not side effects of later calls

---

## No scope-mutation call law

- Ordinary calls such as `WL()` should not silently mutate caller scope by creating names.
- Injecting names into arbitrary caller scope during calls is too implicit.
- If publication exists, it should target the declaring module scope during class creation.

---

## Initialization timeline law

Preferred lifecycle shape:

1. class is created
2. canonical head instance is created
3. lowercase published face is exposed
4. optional explicit `initialize()` may be called
5. library becomes ready

This preserves a visible timeline.

---

## Optional initialization law

- A library may expose an explicit optional `initialize()` call on its published lowercase face.
- This call is used when the library needs a visible boot phase beyond class creation and publication.
- Libraries that do not require additional boot logic may omit meaningful initialization behavior.

Canonical example:

```python
o.initialize()
```

This preserves a visible and controllable lifecycle boundary.

---

## Head-publication distinction law

Preferred lifecycle shape:

1. class is created
2. canonical head instance is created
3. lowercase published face is exposed
4. explicit `initialize()` is called
5. library becomes ready

This preserves a visible timeline.

---

## Optional initialization law

- A library may expose an explicit optional `initialize()` call on its published lowercase face.
- This call is used when the library needs a visible boot phase beyond class creation and publication.
- Libraries that do not require additional boot logic may omit meaningful initialization behavior.

Canonical example:

```python
o.initialize()
```

This preserves a visible and controllable lifecycle boundary.

---

## Head-publication distinction law

- The published lowercase symbol refers to the canonical library head.
- The head may be created internally during metaclass flow.
- External users should not need to reference internal names such as `__instance__`.

Equivalent wording:

- internal head exists
- public face is simple

---

## Python-module vs library-face law

Two entities may share the same textual name, such as `o`:

1. Python module `o`
2. Published library face `o`

These must not be confused.

- Python import machinery may refer to the module object.
- WhiteLabel runtime usage may refer to the published library head.
- Loaders and injected namespaces must be explicit about which entity a symbol references.

---

## Loader namespace law reaffirmed

- Runtime-loaded modules inside a library space should preferably receive library symbols from the loader namespace.
- They should not rely on re-importing the parent Python module when avoidable.
- This reduces circular import pressure and keeps modules inside library space aligned with library law.

---

## Installation law

- The WhiteLabel library is installed through `pip` using the project bootstrap script `install.sh`.
- The script is the canonical convenience entrypoint for local installation and reinstallation during development.
- Typical form:

```bash
source install.sh
```

This keeps developer workflow short while preserving standard Python packaging underneath.

---

## Minimal structural formula, revised

The current line may be summarized as:

- class names remain the sole naming source of truth
- lowercase library faces are derived projections
- publication may occur during metaclass birth
- internal heads stay internal
- initialization is explicit and visible
- access resolution and lifecycle are separate concerns
- Python module identity and library-face identity must not be conflated
