# WhiteLabel

WhiteLabel is a small runtime utility for building Python libraries whose public API is defined by the filesystem layout.

A WhiteLabel-based library behaves like a normal importable module (`import mylib`), but attribute access is resolved dynamically from disk on first access.

---

## What it does (at a glance)

- Replaces a Python module with a live runtime object (registered in `sys.modules`)
- Resolves attributes lazily via `__getattr__`
- Maps folders → namespaces
- Maps files → classes or data
- Loads Python, YAML, and JSON when accessed
- Caches everything after first load
- Keeps user code import-free (no explicit internal imports)

---

## What you get when you `import mylib`

You do **not** get a normal Python module.

You get an **instance** of a `WhiteLabel` subclass:
- stored in `sys.modules['mylib']`
- responsible for resolving `mylib.<anything>` dynamically

Example:

```python
import mylib

mylib.models.Encoder
mylib.config.defaults
