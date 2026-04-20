# Whitelabel Invariants 7

## Scope

This file records the next architectural decisions after `whitelabel_invariants6.md`.
It supplements previous invariants files.
Where specific points differ, this file is newer for those points.

---

## Namespace-face cache law

- A library face and a directory face may cache resolved child carriers.
- This cache lives in `__children__`.
- `__children__` stores `File` / `Directory` carriers, not realized loaded values.
- Therefore namespace caching and content caching remain distinct.

Formula:

- face cache = child carriers
- file cache = realized data

---

## Published access law

- Direct attribute access must return usable realized objects.
- A cached child carrier must therefore still pass through `load()` before being returned.
- Raw `File` carriers belong to discovery surfaces such as iteration, not to ordinary attribute access.

Equivalent summary:

- cache carrier on face
- realize through `load()`
- do not leak raw file carrier through normal attr access

---

## Topology vs content law

- `Directory` remains topology and routing geometry.
- `Directory` may cache child carriers in `__children__`.
- `Directory` still does not own realized content state such as `data`.
- `File` remains the owner of realized content state.

So the split is now:

- directory knows route and children
- file knows content

---

## Module authority law

- Python source module identity is owned by `sys.modules[path]`.
- A real resolved file path is the canonical execution-container key.
- Separate WL-side module registries are redundant and non-canonical.

Meaning:

- one real path
- one module object per process

---

## Class authority law

- Class objects are read from the loaded Python module namespace.
- WL should not keep a parallel class-object registry.
- The loaded module is already the authority for class definitions.

Therefore:

- module owns class namespace
- WL does not duplicate class identity storage

---

## Service singleton law

- Service singleton ownership belongs to the service class itself.
- Singleton identity should live on `cls.__instance__`.
- WL should not keep a separate service-instance registry.

Meaning:

- one service class
- one process instance

---

## File memoization law

- A `File` may memoize its realized loaded value after first load.
- Repeated `load()` calls may return memoized `self.data` directly.
- Mid-process source edits are not required to be observed automatically on every access.

Current line:

- first load realizes content
- later loads reuse in-process memoized content

This is preferred when per-access freshness probing becomes a measurable hot-path tax.

---

## Revised beauty formula

- module path owns execution container
- namespace face owns child carriers
- file owns realized content
- service class owns singleton identity

This split is preferred over duplicate WL registries and preferred over mixing topology, content, and singleton ownership in one layer.
