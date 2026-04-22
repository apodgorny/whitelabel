# WhiteLabel invariants 3

## Python carrier law

- Any `.py` file that is loaded through `py.py` is an own-module source file by law.
- Such a file must define exactly one loadable class with the required `snake_to_camel` relationship between filename and class name.
- That class must extend `wl.Module`.
- If a `.py` file does not satisfy that contract, it is not a valid WL carrier and must not load through `WL` or `O`.

## Scope

This file is a supplement to `whitelabel_invariants1.md` and `whitelabel_invariants2.md`.
It captures only the later refinements established after those notes.
If an item here conflicts with an earlier note, this supplement is newer for that specific point.

---

## Code-location vs namespace-path law

Two different locations must be kept distinct.

### 1. `__lib_path__`

- `__lib_path__` is the absolute directory where the current library class file resides.
- It is derived from the current module file location.
- It belongs to the intrinsic code anatomy of the library.

### 2. `__path__`

- `__path__` is the library namespace root used for ordinary WL resolution.
- It is where names such as `Foo` are resolved as directories or file stems.
- If not supplied explicitly, it may default to `os.path.join(__lib_path__, 'root')`.

Summary formula:

- `__lib_path__` = where the library code is
- `__path__` = what namespace root the library resolves

These must not be collapsed.

---

## Plugin source law

- Plugins are not loaded from `__path__`.
- Plugins are loaded from the intrinsic code-near directory:
  - `os.path.join(__lib_path__, 'plugins')`
- This means plugin implementation lives near the library code, not inside the resolved namespace root.

Equivalent wording:

- `root/` is for resolved names
- `plugins/` is for loader capability implementation

---

## Ordered plugin activation law

- Plugin activation order is declared explicitly in class definition, e.g. `plugins=['Py']`.
- This list expresses only ordered activation law.
- The plugin class implementations are then loaded from the library-local `plugins/` directory.
- Plugin instances are inserted into `__PLUGINS__` in that declared order.
- Dict insertion order is therefore semantic plugin priority.

Summary formula:

- class definition declares plugin order
- plugin directory supplies plugin classes
- insertion order is resolution priority

---

## Plugin loading law

- Plugin class lookup is performed through `Common.get_class(class_name, plugins_path)`.
- The plugin path is derived from `__lib_path__`, not from `__path__`.
- The loaded class is instantiated and stored in `__PLUGINS__`.

This keeps plugin discovery intrinsic to the library implementation.

---

## Recognition-and-load unification law

- Plugins do not need separate `match()` and `load()` methods in the minimal line.
- A single `load(path)` method is sufficient.
- `load(path)` performs both:
  - recognition of whether the plugin owns the stem
  - materialization of the result
- If the plugin does not own the stem, it returns `None`.
- If it owns the stem and succeeds, it returns the loaded value.
- If it owns the stem and fails, the failure should surface.

Equivalent wording:

- plugin `load()` is both recognition and materialization
- `None` means 'not mine'

---

## Stem-to-file law

- Resolver passes an extension-less canonical stem path to plugins.
- A plugin derives its concrete filename from that stem.
- For the Python plugin, the established law is:
  - visible name `Foo`
  - stem path `.../Foo`
  - module file `.../foo.py`
  - loaded class `Foo`
- Therefore a plugin may transform the basename of the stem into another file naming form, such as CamelCase to snake_case.

This preserves the invariant that visible symbolic names and physical filenames may obey different naming laws.

---

## Module-ness filter law

- A plugin may impose additional ontological checks beyond file existence.
- In the Python plugin line, a discovered class is considered valid only if it is a subclass of the current library's `Module`.
- Therefore file presence alone is not sufficient for successful resolution.

Summary formula:

- file exists
- class loads
- class must satisfy module law

Only then is the result accepted.

---

## Heads-lineage traversal law

- Resolution and intrinsic lookup both traverse lineage through canonical heads, not through ordinary user instances.
- The practical minimal form is iteration over `cls.__instance__` for each class in `type(self).__mro__`, excluding `object`.
- This head-lineage traversal may be abstracted into a single iterator such as `__instances__()`.

Equivalent wording:

- one ladder
- many uses
- both intrinsic lookup and namespace resolution walk the same lineage heads

---

## Two-phase lineage lookup law

Attribute access now has two conceptual phases over the same head lineage.

### 1. Intrinsic phase

- Walk lineage heads
- Check their intrinsic state first

### 2. Resolved phase

- Walk lineage heads again
- Resolve the requested name through each head's `__path__` in order

This yields:

- local layer first
- then parent layer
- then grandparent layer

And preserves filesystem-backed inheritance.

---

## Local-first inherited-root law reaffirmed

- A request such as `o.Foo` must search:
  - `o/root`
  - then `llm/root`
  - then `whitelabel/root`
- The first successful resolution wins.
- This is the operational form of filesystem-backed namespace inheritance in the simplified line.

---

## Canonical route law

- The chosen term for the executable library-side traversal string is `__route__`.
- `__route__` is not merely an address label.
- It is a route because evaluating it traverses the namespace and reaches the target.
- The motivating intuition is:
  - `eval(__route__)` takes us for a ride to the address

Therefore `__route__` is preferred over weaker or more ambiguous candidates such as:
- brand-specific module markers
- `__mod__`
- plain entity labels that hide its executable traversal nature

Summary formula:

- `__route__` = executable traversal string

---

## Parallel identifier law

- In `o`, `__route__` and `__proto__` are parallel but not identical.
- `__route__` expresses executable traversal.
- `__proto__` expresses canonical identity form.
- These axes must remain distinct.

Equivalent wording:

- `__route__` says how to get there
- `__proto__` says what it is canonically

---

## Anti-branding law for core identifiers

- Core load-bearing identifiers must not be repeatedly prefixed with the current library brand.
- Therefore patterns like `__wl_module__`, `__route__`, and similar branded duplications are considered ugly and non-canonical.
- A single neutral cross-library invariant name is preferred.

This law is one of the motivations for choosing `__route__`.

---

## Name-mangling avoidance law

- Double-underscore names that are meant to be shared explicitly between metaclass, class, and canonical head can become fragile because of Python name-mangling.
- Therefore one must be careful not to use mangled names where the architecture expects literal shared attribute names.
- Cross-layer architectural fields should prefer names whose lookup meaning remains stable across metaclass/class/head interaction.

This is a practical stability law, not merely a style preference.

---

## Minimal structural formula, revised

The current simplified line may be summarized as:

- `WLMeta` derives `__lib_path__` and `__path__`
- `WLMeta` creates one canonical head per library class
- `WLMeta` loads ordered plugins from `__lib_path__/plugins`
- attribute access walks head lineage
- intrinsic lookup happens first
- resolution then walks each head's `__path__`
- directories become `Directory`
- terminal non-directories are offered to ordered plugins
- plugin `load()` both recognizes and materializes
- canonical executable traversal is named `__route__`

This line intentionally keeps the ontology small while preserving explicit invariants.
