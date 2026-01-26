print('test')
# ======================================================================
#  WhiteLabel — lazy runtime module loader
# ======================================================================
#
#	What is this?
#	-------------
#	WhiteLabel lets you build a Python library that *looks* like a normal
#	importable module (`import mylib`), but is actually a live runtime object.
#
#	Instead of importing everything upfront, attributes are resolved
#	lazily from the filesystem *on first access*.
#
#		import mylib
#		mylib.models.Encoder
#
#	No explicit imports. No registries. No wiring.
#
#
#	Core idea
#	---------
#	- The library instance replaces the Python module via `sys.modules`
#	- Attribute access is intercepted via `__getattr__`
#	- Filesystem structure defines the public API
#	- Everything is loaded only when needed
#
#
#	Filesystem → Python path mapping
#	--------------------------------
#
#	Folder  → namespace
#	File    → class or data
#
#	Example filesystem:
#
#	mylib/
#	├─ mylib.py
#	└─ core/
#	├─ models/
#	│  └─ encoder.py
#	├─ operators/
#	│  └─ search.py
#	└─ config/
#		├─ defaults.yaml
#		└─ weights.json
#
#
#	Resolves as:
#
#	mylib.models.Encoder        → class Encoder (from encoder.py)
#	mylib.operators.Search     → class Search  (from search.py)
#	mylib.config.defaults      → dict (from defaults.yaml)
#	mylib.config.weights       → dict (from weights.json)
#
#
#	Naming rules
#	------------
#	- Folder names stay as-is
#	- File names are snake_case
#	- Class names are CamelCase
#
#	Example:
#
#	core/models/text_encoder.py
#
#	must define:
#
#	class TextEncoder(Module):
#		...
#
#	and is accessed as:
#
#	mylib.models.TextEncoder
#
#
#	Lazy loading behavior
#	---------------------
#
#	Nothing is loaded at import time.
#
#		import mylib      # almost free
#
#	Loading happens only when accessed:
#
#		mylib.models      # loads namespace
#		mylib.models.Encoder
#						# loads encoder.py
#						# extracts Encoder class
#
#	YAML / JSON files are also lazy-loaded:
#
#		mylib.config.defaults
#		mylib.config.weights
#
#	Data files are parsed once and cached.
#
#
#	What `import mylib` actually gives you
#	-------------------------------------
#
#	`mylib` is NOT a Python module.
#
#	It is an *instance* of a WhiteLabel subclass that:
#	- lives in `sys.modules['mylib']`
#	- intercepts attribute access
#	- dynamically resolves paths
#
#
#	Minimal setup example
#	---------------------
#
#	mylib.py:
#
#		from white_label import WhiteLabel
#
#		class MyLib(WhiteLabel):
#			pass
#
#		mylib = MyLib()
#
#
#	user code:
#
#		import mylib
#
#		encoder = mylib.models.Encoder()
#		config  = mylib.config.defaults
#
#
#	Design goals
#	------------
#	- Zero boilerplate for users
#	- No explicit imports inside user code
#	- Filesystem *is* the API
#	- One reusable core for many libraries
#
# ======================================================================

import os
import sys
import importlib.util
import re
import threading

import json
import yaml

# ======================================================================
# Common methods
# ======================================================================

# Load module
# ----------------------------------------------------------------------
def load_module(import_path, file_path):
	spec   = importlib.util.spec_from_file_location(import_path, file_path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module

# Convert CamelCase name to snake_case filename.
# ----------------------------------------------------------------------
def camel_to_snake(name):
	return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

# Convert snake_case name to CamelCase.
# ----------------------------------------------------------------------
def snake_to_camel(name):
	return ''.join(part.capitalize() for part in name.split('_'))


# ======================================================================
# CLASS Module
# ======================================================================

class Module:

	def print(self, *args, **kwargs):
		gray  = '\033[38;5;242m'
		reset = '\033[0m'
		if not WhiteLabel.verbose:
			module_attr = getattr(self, self.__lib__.module_attr)
			print(f'{gray}{module_attr}:{reset}', *args, **kwargs)

# ======================================================================
# CLASS Namespace
# ======================================================================

class Namespace:

	def __init__(self, path=None):
		self.path = path

	# Resolve attribute access through resolver.
	# ----------------------------------------------------------------------
	def __getattr__(self, name):
		module = self._load_init()
		if module is not None and hasattr(module, name):
			return getattr(module, name)

		return self.__lib__._resolve(name, self.path)

	# Load package __init__.py if present.
	# ----------------------------------------------------------------------
	def _load_init(self):
		module    = None
		init_path = os.path.join(self.path, '__init__.py')

		if os.path.isfile(init_path):
			cache = self.__lib__._pkg_cache
			if init_path not in cache:
				module_hash      = abs(hash(init_path))
				module           = load_module(f'{self.__lib__.lib_name}.{module_hash}', init_path)
				cache[init_path] = module
			else:
				module = cache[init_path]

		return module

# ======================================================================
# CLASS WhiteLabel
# ======================================================================

class WhiteLabel:
	Module     = Module
	Namespace  = Namespace

	verbose    = True

	_instances = {}
	_lock      = threading.Lock()

	def __new__(cls, lib_path=None):
		with cls._lock:
			if cls not in cls._instances:
				inst = super().__new__(cls)
				inst.initialize(lib_path)
				cls._instances[cls] = inst
		return cls._instances[cls]

	# Resolve top-level attribute access.
	# ----------------------------------------------------------------------
	def __getattr__(self, name):
		cls = type(self)
		if hasattr(cls, name):
			return getattr(cls, name)
		return self._resolve(name, self.core_path)

	# ======================================================================
	# PRIVATE METHODS
	# ======================================================================

	# Resolve module or namespace by name.
	# ----------------------------------------------------------------------
	def _resolve(self, name, path):
		path   = os.path.join(path, camel_to_snake(name))
		result = None

		if os.path.isdir(path):
			if path not in self._ns_cache:
				result = Namespace(path)
				setattr(result, '__lib__', self)
				self._ns_cache[path] = result

		elif os.path.isfile(f'{path}.py'):
			result = self._load_py_module(f'{path}.py')

		else:
			for ext in ('yml', 'yaml', 'json'):
				file_path = f'{path}.{ext}'
				if os.path.isfile(file_path):
					result = self._load_data(file_path)

		if result is None:
			raise AttributeError(f'Module `{self._get_module_name(path)}` does not exist')

		return result

	# Build public lib module path.
	# ----------------------------------------------------------------------
	def _get_module_name(self, path):
		rel_path   = os.path.relpath(path, self.core_path)
		parts      = rel_path.split(os.sep)
		name       = parts.pop()
		class_name = snake_to_camel(name)

		parts.insert(0, self.lib_name)
		parts.append(class_name)

		return '.'.join(parts)

	# Build importlib module path.
	# ----------------------------------------------------------------------
	def _get_import_path(self, path):
		rel_path = os.path.relpath(path, self.core_path)
		return f'{self.lib_name}.core.{rel_path[:-3].replace(os.sep, ".")}'

	# Get expected class name from file path.
	# ----------------------------------------------------------------------
	def _get_class_name(self, path):
		name = os.path.splitext(os.path.basename(path))[0]
		return snake_to_camel(name)

	# Check whether object matches lib module class contract.
	# ----------------------------------------------------------------------
	def _is_module_class(self, obj):
		return (
			isinstance(obj, type)      and
			issubclass(obj, Module) and
			obj is not Module
		)

	# Load module file and extract Module subclass
	# ----------------------------------------------------------------------
	def _get_class(self, path):
		import_path = self._get_import_path(path)
		module      = load_module(import_path, path)
		class_name  = self._get_class_name(path)
		
		cls = getattr(module, class_name, None)
		if self._is_module_class(cls):
			return cls

		return None

	# Load module file and extract Module subclass
	# ----------------------------------------------------------------------
	def _load_py_module(self, path):
		if path not in self._class_cache:
			cls = self._get_class(path)

			if cls is None:
				raise AttributeError(f'File `{path}` defines no {self.lib_name}.Module')

			self._class_cache[path] = cls

			setattr(cls, '__lib__', self)                                # Set __lib__ attr on Module
			setattr(cls, self.lib_name, self)                            # Set <lib> attr on Module
			setattr(cls, self.module_attr, self._get_module_name(path))  # Set __mylib_module__

		return self._class_cache[path]

	# Load data file.
	# ----------------------------------------------------------------------
	def _load_data(self, path):
		if path not in self._data_cache:
			ext  = os.path.splitext(path)[1].lower()
			data = None

			with open(path, 'r', encoding='utf-8') as f:
				text = f.read()

			if   ext == '.json'           : data = json.loads(text)
			elif ext in ('.yml', '.yaml') : data = yaml.safe_load(text)

			if data is not None:
				self._data_cache[path] = data

		return self._data_cache.get(path)

	# ======================================================================
	# PUBLIC METHODS
	# ======================================================================

	# Initialize core paths and internal caches.
	# ----------------------------------------------------------------------
	def initialize(self, lib_path=None):
		self.lib_name    = self.__class__.__name__.lower()
		self.lib_path    = os.path.dirname(os.path.abspath(__file__)) if lib_path is None else lib_path
		self.core_path   = os.path.join(self.lib_path, 'core')
		self.module_attr = f'__{self.lib_name}_module__'

		sys.modules[self.lib_name] = self

		self._class_cache = {}
		self._ns_cache    = {}
		self._data_cache  = {}
		self._pkg_cache   = {}

	# Allowes to remotely import concrete wl library
	# ----------------------------------------------------------------------
	@classmethod
	def imp(cls, file_path):
		module_name = os.path.splitext(os.path.basename(file_path))[0]
		module      = load_module(module_name, file_path)

		for obj in module.__dict__.values():
			if (
				isinstance(obj, type)
				and issubclass(obj, WhiteLabel)
				and obj is not WhiteLabel
			):
				# КРИТИЧНО: lib_path — папка, где лежит файл
				lib_path = os.path.dirname(os.path.abspath(file_path))

				instance = obj(lib_path=lib_path)

				# Регистрируем как модуль
				sys.modules[instance.lib_name] = instance
				return instance

		raise RuntimeError(f'No WhiteLabel subclass in `{file_path}`')
