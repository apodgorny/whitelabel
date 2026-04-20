# WhiteLabel invariants 1

## Scope

This file captures only the invariants established in the current conversation about `WL` / `WhiteLabel`.
It is meant as a dense handoff note for implementation work.
Older or alternative designs are not normative unless explicitly restated here.

---

## Core ontology

- `WL` is not an ordinary directory node.
- `WL` is the loader law / world law.
- Directories and files are materialized through `WL`; they are not identical to `WL` itself.
- Class inheritance and filesystem manifestation are different axes and must not be collapsed.

---

## Naming law

- Capitalized names are intrinsic classes / typed things.
- Lowercase names are filesystem-resolved names by default.
- Rare filesystem uppercase names are acceptable as noise and do not justify changing the law.
- The most prominent spots of the architecture must not violate the naming law.

---

## Path roles

There are two different path roles and they must not be confused.

### 1. Class-side authored path

- Each library layer has its own class-side authored root.
- This is the path from which that layer loads its own modules.
- This path is supplied at class creation time.
- Current practical name: `path`.
- Earlier naming split such as `lib_path` / `core_path` is compatible in spirit, but the current line discussed here uses one class-side `path` per layer.

### 2. Instance-side runtime root

- A top world instance such as `o = O(path)` also receives a runtime root.
- This runtime root is not the same thing as the class-side authored `path`.
- Class-side module loading must not be confused with runtime-world rooting.

---

## Class creation law

- `path` must be available in metaclass `__new__`.
- This is class parameterization, not ordinary inheritance.
- The intended shape is conceptually like:

```python
class LLM(WL, path='/llm/core'):
	pass
```

- `meta.__new__` receives that `path`.
- `meta.__new__` sets `cls.path`.

---

## Canonical head law

- Each `WL`-family class has one canonical internal live head.
- This head is created in metaclass `__new__`.
- The head is stored on the class, e.g. `cls.instance`.
- The head receives the class-side `path`.
- This head is the live resolver for the layer.
- Resolution should go through the live head, not only through raw class attributes.

This is an unusual pattern and is intentional.

---

## Multipleton law

- This pattern is not an ordinary singleton and not ordinary Python instance semantics.
- It is a multipleton-like pattern.
- There is one canonical head per class in the current process / import universe.
- There may still be multiple manifestations / uses through that head.
- The head is class-canonical, not user-world state.

---

## Process boundary law

- The canonical class head is not global across all programs.
- Each terminal process / import universe creates its own class heads.
- Within one process, the class head is canonical.

---

## Shared module cache law

- Module cache must be single for all subclasses in the lineage.
- Module cache is not per-class.
- Module cache is not per-instance.
- Module cache lives on `WL` root class and is inherited/shared by subclasses.
- Therefore a declaration such as:

```python
class WL(metaclass=WLMeta):
	__MODULE_CACHE__ = {}
```

is sufficient, as long as subclasses do not rebind it.

- The cache is shared memory of the lineage.

---

## Cache ownership law

- All caches relevant to module resolution belong on class level, not instance level.
- These caches are shared across subclasses.
- Cache is part of the layer law, not part of user manifestation state.

---

## Lookup law

Resolution order is:

1. intrinsic class/body names
2. filesystem-backed module loading through current layer `path`
3. parent-layer paths through lineage / MRO
4. shared module cache

Equivalent wording:

- intrinsic first
- then local authored filesystem root
- then inherited authored roots
- with results shared through one lineage-wide cache

---

## Filesystem-backed inheritance law

- Child layers must be able to resolve modules from their own authored root first.
- If not found there, lookup continues upward through parent layers.
- So something like `O.Model` should conceptually search:
  - `O.path`
  - then `LLM.path`
  - then `WL.path`
- This is filesystem-backed namespace inheritance.

---

## Python import vs WL loading

These are different mechanisms.

### Python import

- Used to load intrinsic classes that define the layer itself.
- Example: loading the actual Python definition of `WL`, `LLM`, `O`, or intrinsic support classes.

### WL loading

- Used to materialize layer modules from authored filesystem roots during runtime resolution.
- This is not the same thing as Python import.

The two mechanisms must not be collapsed.

---

## Head responsibility law

The canonical head must not become a second world or a second storage.

The head should contain only things such as:

- layer `path`
- resolution logic
- cache access
- loading behavior

The head must not contain:

- user world data
- user manifestation state
- unrelated mutable runtime payload

---

## World state law

- World/user state does not belong on the canonical class head.
- World/user state belongs to actual world instances / manifestations.
- The canonical class head is for lawful layer resolution only.

---

## MRO usage law

- MRO is the correct traversal for lineage lookup of layer roots.
- Module loading walks class lineage through MRO.
- This applies to authored-path lookup, not to user-state traversal.

---

## Explicit kernel law

- Intrinsic core names should be installed explicitly in class bodies.
- They should not be left to accidental filesystem discovery.
- WL core anatomy should be explicit and load-bearing.

---

## Clean minimal draft shape

The current minimal intended shape is:

```python
class WLMeta(type):

	def __new__(mcls, name, bases, namespace, path=None):
		cls = super().__new__(mcls, name, bases, namespace)
		cls.path = path
		cls.instance = object.__new__(cls)
		cls.instance.path = cls.path
		return cls


class WL(metaclass=WLMeta):

	__MODULE_CACHE__ = {}
```

This is only the minimal skeleton.
The invariants above are the actual law.

---

## Summary formula

- `WL` is loader law, not directory node.
- class-side `path` is authored root.
- metaclass `__new__` receives `path`.
- metaclass `__new__` creates one canonical class head.
- lookup goes through the head.
- module cache is single across subclasses.
- caches are class-level, not instance-level.
- child layer resolves locally first, then upward through lineage.
- head carries resolver logic, not world state.
- this is an intentional multipleton pattern.
