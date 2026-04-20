# WhiteLabel invariants 2

## Scope

This file is a supplement to `whitelabel_invariants1.md`.
It captures only the additional or refined invariants established later in the same design line.
If an item here conflicts with the earlier note, this supplement is newer for that specific point.

---

## Kernel simplification law

- The architecture was simplified by removing `File` as a first-class mandatory intermediary.
- The minimal stable ontology is now:
  - `WL` / library law
  - `Directory` / spatial continuation
  - plugins / interpretation of terminal non-directory forms
- `Resolver` is not required as a separate permanent ontology object if its logic can live directly in `WL`.
- The router may be implemented directly on `WL`, because path resolution is part of the library law itself.

Equivalent wording:

- `WL` decides how names are resolved
- `Directory` continues spatial lookup
- plugins interpret terminal forms
- `File` is optional and not load-bearing in the new minimal line

---

## Intrinsic lookup refinement

- Intrinsic lookup walks class lineage but reads live per-layer state from canonical heads.
- The traversal axis is still class `MRO`.
- The read point for live intrinsic state is the canonical head of each class, not ordinary instance inheritance.
- Class-level intrinsic law still exists and inherits automatically through Python.
- Head-level live state does not inherit automatically and therefore must be searched procedurally across lineage.

Summary formula:

- law inherits automatically
- live state inherits procedurally

---

## Explicit OS-space law

- `WL` may have OS-reaching ability, but OS-space must not be an implicit fallback of ordinary lineage module lookup.
- Ordinary authored-root inheritance and OS-space are different modes and must not be collapsed.
- Searching the full filesystem root such as `'/'` as a silent parent fallback is too broad and conceptually wrong.
- If `WL` exposes OS-space, it should do so through an explicit branch or mount-like manifestation.

Examples of acceptable expression:

- an explicit namespace such as `wl.sys.Users.Alexander`
- an explicit mount / alias such as `wl.link('sys', '/')`
- a real filesystem symlink in the authored root such as `sys -> /`

Equivalent wording:

- external worlds are linked
- they are not ordinary inherited parent roots

---

## Symlink manifestation law

- Symlinks are a valid and preferred way to expose external namespaces inside WL space.
- A mounted namespace such as `sys` can be represented as a real filesystem symlink rather than as hidden special logic.
- This is conceptually cleaner because the filesystem itself expresses the connection.
- A symlinked namespace is an explicit branch, not a fallback rule.

---

## Path canonicalization law

- Resolution should normalize candidate paths through `os.path.realpath(...)` before deciding their nature.
- This applies whether the target is a symlink or not.
- The purpose is canonical filesystem identity, not just symlink handling.
- Therefore directory resolution and plugin resolution should operate on canonicalized paths.

Consequences:

- symlinked directories and direct directories converge to the same physical target
- symlinked file stems and direct file stems converge to the same physical target
- duplicate identities through alias paths are reduced

---

## Terminal resolution law

- Resolution starts from a name and a current root path.
- The router builds the candidate stem path by joining the root and the name, then canonicalizing it with `realpath`.
- If the resulting path is a directory, resolution returns `Directory`.
- If it is not a directory, the router delegates interpretation of the terminal non-directory form to plugins.
- If no plugin recognizes the stem, the result is `Undefined` / unresolved.

Summary formula:

- name -> canonical stem path -> directory or plugin

---

## Plugin priority law

- Plugin registration order is semantic priority order.
- Ordered `dict` insertion order is sufficient for that purpose in modern Python.
- Therefore ambiguity between multiple file forms of the same stem is solved by plugin priority.
- No separate extension-priority table is required if plugin registration order is treated as law.

Equivalent wording:

- first matching plugin wins
- plugin order is resolution priority

---

## Stem matching law

- Plugins receive an extension-less canonical stem path.
- A plugin decides whether that stem has a concrete file form it understands.
- The canonical pattern is: plugin checks for the existence of `stem.<ext>`.
- A plugin loads the concrete file form corresponding to its own extension law.

Example meaning:

- a Python plugin checks `stem.py`
- a JSON plugin checks `stem.json`
- and so on

Therefore:

- resolver does not need to know extension-specific loading details
- plugin matching determines which concrete file form exists for a stem

---

## Minimal ambiguity law

- A visible name may have multiple file forms with different extensions.
- This does not require a separate ambiguity object if priority is explicit.
- The minimal invariant is:
  - one stem
  - ordered plugins
  - first match wins
- This keeps the core loop minimal while still making resolution deterministic.

---

## Plugin error law

- The core router does not need to swallow plugin exceptions.
- If a plugin declares a match and fails during load, the plugin error should surface directly.
- This keeps plugin responsibility explicit and avoids hiding real load failures behind fallback behavior.

Equivalent wording:

- match means "this is mine"
- load failure means real failure, not silent skip

---

## Process-local plugin pool law

- Plugins are not persisted on disk in this line.
- Therefore plugin mutation is process-local.
- A child layer such as `O` may extend the available plugin pool during the current process.
- Another independent program that loads `WL` afresh gets a fresh plugin pool.
- Because of this, a shared in-memory plugin dictionary across the current lineage is acceptable in this design line.

Important nuance:

- this is acceptable specifically because plugins are process-local and non-persistent
- if later per-layer persistent plugin law is desired, a stricter collection mechanism may be needed

---

## Canonical symbol law for `Undefined`

- `Undefined` is intended to be accessed as a capitalized intrinsic symbol, e.g. `o.Undefined`, not as lowercase `o.Undefined`.
- The reason is ontological clarity: this sentinel is treated as a type-like intrinsic symbol.
- The design preference is that the class object itself may behave as the sentinel instance.
- This preserves naming symmetry with other intrinsic capitalized symbols.

Equivalent wording:

- `Undefined` is a capitalized intrinsic sentinel
- it should behave as a value while remaining a type-shaped symbol

---

## Directory housing law

- A non-directory terminal form always lives inside a housing directory.
- Therefore spatial continuation can always step one level up to the containing directory when needed.
- This justifies the idea that terminal file-family interpretation belongs to the containing directory space and/or plugins, not to a free-floating isolated file ontology.

---

## Simplified structural formula

The current simplified line is:

- `WL` holds intrinsic law and the main resolution router
- each layer has one canonical head
- names resolve to a canonical stem path
- directories continue as `Directory`
- terminal non-directories are interpreted by ordered plugins
- external worlds are mounted explicitly, often through symlinks
- path identity is canonicalized with `realpath`
- `Undefined` remains an explicit intrinsic sentinel

This line intentionally minimizes special ontology objects and loops.
