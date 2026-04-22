# Whitelabel Invariants 6

## Python carrier law

- Any `.py` file that is loaded through `py.py` is an own-module source file by law.
- Such a file must define exactly one loadable class with the required `snake_to_camel` relationship between filename and class name.
- That class must extend `wl.Module`.
- If a `.py` file does not satisfy that contract, it is not a valid WL carrier and must not load through `WL` or `O`.

## Scope

This file captures the architectural decisions from the current conversation about caching, freshness, plugins, and file objects.
It supplements previous invariants files.

---

## Core Split

- Cache ownership belongs to `File` objects, not plugins.
- Plugins resolve and load sources.
- `File` stores cached runtime state.

Canonical cached state on `File`:

- `self.data`
- `self.hash`

---

## Directory Law

- Directories do not participate in freshness caching.
- Directories are namespace / routing geometry.
- Directories are not content sources.
- Directories do not own `data` or `hash` state.

Formula:

- directory = topology
- file/plugin = content source

---

## Plugin Law

- Plugins must not own result caches.
- Plugins must stay stateless regarding loaded content.
- Plugins may determine freshness of their source.
- Plugins may load current content.

Because plugins may have arbitrary internal physics, no cheapness assumption may be imposed.

---

## Two-Method Source Contract

A single combined `load(hash)` contract incorrectly pressures plugins to hold or reason about external cache state.

Approved split:

- one method for freshness token
- one method for content load

Current approved construction shape:

```python
load_method
hash_method
```

Meaning:

- `hash_method()` returns current source token
- `load_method()` returns current authoritative content

These are passed into `File(...)` during construction.

## Hash Meaning

- `hash` means opaque freshness token.
- It need not be cryptographic hash.
- It may be mtime, version token, revision number, or equivalent.

For Python file plugin, `os.path.getmtime(path)` is acceptable current line.

---

## Shared Resolve Law

If freshness and loading need the same resolved source context, resolve must happen once during file construction.

Example resolved values:

- `path`
- `route`
- `class_name`

Then closures are created from that shared context:

```python
load_method()
hash_method()
```

This avoids:

- duplicate resolve work
- plugin-held cache state
- repeated path discovery

## File Refresh Law

`File` owns cache state:

- `self.data`
- `self.hash`

`File.load()` refresh logic:

1. call `hash_method()` if present
2. compare with `self.hash`
3. if changed, call `load_method()`
4. update `self.data`
5. update `self.hash`
6. return `self.data`

If `hash_method` is absent but `load_method` exists, `File.load()` calls `load_method()` directly.

If `load_method` is absent, `File.load()` returns cached `self.data` as-is.

`File` refresh logic:

1. call `get_hash()`
2. compare with `self.hash`
3. if same, return `self.data`
4. if changed, call `load()`
5. update `self.data`
6. update `self.hash`
7. return fresh data

---

## Class / Service Coverage

The Python plugin load path already covers two semantic outputs:

- ordinary class objects
- instantiated service objects

No extra external cache layer is required for this distinction.

---

## Beauty Formula

- plugin knows source
- file knows memory
- directory knows route

This split is preferred over dunder global caches and preferred over plugin-owned result caches.
