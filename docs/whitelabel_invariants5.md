# WhiteLabel invariants 5

## Scope

This file supplements and corrects `whitelabel_invariants1.md` through `whitelabel_invariants4.md`.
Where specific points differ, this file is newer for those points.

---

## Published-face law (reaffirmed)

- A library class publishes a lowercase library face derived from the class name.
- The lowercase face is a projection, not a second naming source of truth.
- Manual alias lines such as `wl = WL()` remain non-canonical.
- The class name is still the sole naming source of truth.

---

## Optional initialization law (reaffirmed)

- A library may expose an explicit optional `initialize()` on its published lowercase face.
- This remains the visible boot boundary when a library needs one.
- Libraries without extra boot logic may keep initialization trivial.

Canonical example:

```python
o.initialize()
```

---

## Python-module vs library-face law (reaffirmed)

- Python module identity and published library-face identity remain distinct.
- This distinction is especially important during source loading and class materialization.
- A textual name such as `o` may refer either to the Python module or to the published library face, depending on context.

---

## Published import-face law

- Because the lowercase library face is published in `sys.modules`, ordinary Python import may be used to obtain the library face during source execution.
- This allows source files and plugins to write forms such as:

```python
import wl
import o
```

and inherit from:

```python
class Py(wl.Plugin):
	...
```

or:

```python
class T(o.Module):
	...
```

- This is preferred over ad hoc external namespace injection when the published library face is already available.

---

## Plugin ownership law (revised)

- Plugins are owned per library layer, not by a shared global registry.
- Each library class has its own `__PLUGINS__` container.
- Subclasses inherit plugin behavior through lineage traversal, not by mutating parent plugin state.
- Base libraries do not automatically gain plugins declared by subclasses.

Canonical effect:

- child sees child plugins + inherited base plugins
- base sees only base plugins

---

## Plugin resolution law

- Plugin lookup follows library lineage.
- During resolution, plugin sets are visited through library instances yielded by `__instances__()`.
- Local layer plugins should have priority before inherited layer plugins.

This preserves directional inheritance.

---

## Plugin binding law

- Plugin instances may be created bound to their owning library face.
- A plugin may therefore use its owning library context directly during execution.
- Repeated external library injection on every plugin call is optional rather than required.
- This is especially natural when each layer owns its own plugin instances.

---

## Plugin call contract law

- Plugin call shape should mirror resolver context.
- The current preferred plugin entry shape is:

```python
plugin(name, parent_path, parent_route)
```

- This matches the conceptual contract of resolution.
- Plugins then normalize concrete filesystem form and assemble the resulting `File` carrier if they own the candidate.

---

## File carrier law

- Iteration should expose filesystem children as `File` carriers rather than immediately loaded domain objects.
- A `File` is a minimal carrier containing route, path, and loading capability.
- Loading policy belongs to the consumer unless direct access semantics require eager realization.

---

## Directory-is-File law

- `Directory` is a specialized `File`, consistent with filesystem style semantics.
- Directories are branch files; terminal files are leaf files.
- A directory may implement `load()` as identity (`return self`).

---

## Dual access law

WhiteLabel supports two distinct access gestures:

### Iteration gesture

- Iteration is discovery.
- `__iter__()` returns child `File` / `Directory` carriers.
- Consumers may selectively call `load()`.

### Attribute gesture
n
- Attribute access is direct resolution.
- `__getattr__()` should return already usable realized objects.
- If resolution yields a `File`, it should be loaded automatically.
- If resolution yields a `Directory`, identity load returns the directory itself.

Equivalent summary:

- iteration is deferred
- attribute access is eager

---

## Route derivation law (reaffirmed)

- Child route should not be prematurely imposed by callers when type selection may affect normalization.
- Resolution receives child name plus parent context.
- Final child route is derived during materialization by the responsible resolver/plugin.

---

## Namespace purity law

- Visible namespace names and concrete filesystem filenames are separate concerns.
- Callers should operate in visible child names.
- Plugins may translate visible names into concrete filenames such as `.py`, `.json`, or others.
- Raw filesystem entries must not be treated as the canonical namespace surface.

This keeps namespace law separate from storage law.

---

## Directory iteration law

- `Directory.__iter__()` is a discovery gesture.
- It should enumerate immediate WL children in carrier form.
- Iteration should not collapse immediately into fully loaded domain objects.
- Iteration surface should therefore expose `File` / `Directory` children suitable for selective `load()` by the consumer.

---

## Discovery vs realization law

- Discovery enumerates possible children.
- Realization materializes a chosen child into its executable or usable form.
- WhiteLabel should preserve this distinction across APIs.

---

## Minimal structural formula, revised

- libraries own plugins per layer
- lineage grants downward plugin inheritance only
- iteration returns carriers
- direct attribute access returns realized children
- directories are files of branch kind
- routes are derived during materialization
- namespace names and storage filenames remain separate
- discovery and realization are distinct phases

