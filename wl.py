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
# 	Example usage:
# 	-----------------------------
# 	1. Create file `{self.core_path}/mymodules/my_module.py`
3
# 		import {self.lib_name}
#
# 		class MyModule({self.lib_name}.Module):
# 			def __init__(self, name):
# 				self.name = name
3
# 			def hello(self):
# 				print('Hello from', self.name, 'at', self.{self.module_attr})
# 				print('File names must be a snake case version of class name')
# 				print('Only one class is permitted per file')
#
# 	2. Create file `{self.core_path}/mymodules/my_service.py`
#
# 		import {self.lib_name}
#
# 		class MyService({self.lib_name}.Service):
# 			def initialize(self):
# 				# One time initialization goes here
# 				pass
#
# 			def hello(self):
# 				print('Services stay in memory and accessed without ()')
#
# 	3. Create file  `{self.lib_path}/main.py`
#
# 		import o
#
# 		instance = o.MyModule()
# 		instance.hello()
#
# 		o.MyService.hello()
#
# 	4. From `{self.lib_path}` run: `python main.py`
#
#
# ======================================================================

import os
import sys
import importlib.util
import re
import threading

import json
import yaml

from .core.module    import Module
from .core.namespace import Namespace
from .core.service   import Service
from .core.conf      import Conf
from .core.events    import Events
from .core.string    import String
from .core.dual      import DualMethod, DualProperty

# ======================================================================
# Common methods
# ======================================================================

_MODULE_CACHE = {}

# Get class module file
# ----------------------------------------------------------------------
def get_class_file(cls):
	module = sys.modules.get(cls.__module__)
	if module and hasattr(module, '__file__'):
		return module.__file__
	return None

# Load module
# ----------------------------------------------------------------------
def load_module(name, path):
	abspath = os.path.abspath(path)

	if abspath not in _MODULE_CACHE:
		spec   = importlib.util.spec_from_file_location(name, path)
		module = importlib.util.module_from_spec(spec)
		module.__file__ = path
		if name not in sys.modules:
			sys.modules[name] = module
		spec.loader.exec_module(module)
		_MODULE_CACHE[abspath] = module

	return _MODULE_CACHE[abspath]

# ======================================================================
# CLASS WhiteLabel
# ======================================================================

class WL:
	Module     = Module
	Namespace  = Namespace
	Service    = Service

	verbose    = True

	_instances = {}
	_lock      = threading.Lock()

	# Entry point
	# ----------------------------------------------------------------------
	def __new__(cls, lib_path=None):
		with cls._lock:
			if cls not in cls._instances:
				inst     = super().__new__(cls)
				lib_name = cls.__name__.lower()

				inst.initialize(lib_name, lib_path)
				cls._instances[cls] = inst

		return cls._instances[cls]

	# Resolve top-level attribute access.
	# ----------------------------------------------------------------------
	def __getattr__(self, name):
		if name.startswith('__'):
			raise AttributeError(name)

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
		path   = os.path.join(path, String.camel_to_snake(name))
		result = None

		# Namespace
		# - - - - - - - - - - - - - - - - - - - - - - - - - 
		if os.path.isdir(path):
			if path in self._ns_cache:
				result = self._ns_cache[path]
			else:
				result = Namespace(path)
				setattr(result, '__lib__', self)
				self._ns_cache[path] = result

		else:
			
			# Custom plugins
			# - - - - - - - - - - - - - - - - - - - - - - - - - 
			for plugin_name, plugin in self._plugins.items():
				try:
					if plugin.match(path):
						return plugin.load(path, self)  # Early return for plugins only
				except Exception as e:
					print(f'Plugin `{plugin_name}` raised: `{type(e).__name__}`: `{str(e)}`')

			# Python Class
			# - - - - - - - - - - - - - - - - - - - - - - - - - 
			if os.path.isfile(f'{path}.py'):
				result = self._load_class(f'{path}.py')

			# Data files
			# - - - - - - - - - - - - - - - - - - - - - - - - - 
			else:
				for ext in ('yml', 'yaml', 'json'):
					file_path = f'{path}.{ext}'
					if os.path.isfile(file_path):
						result = self._load_data(file_path)

		# None of the above
		# - - - - - - - - - - - - - - - - - - - - - - - - - 
		if result is None:
			raise AttributeError(f'Module `{path}` does not exist or no loading method is provided')

		return result

	# Build public lib module path.
	# ----------------------------------------------------------------------
	def _get_module_name(self, abs_path):
		rel_path   = os.path.relpath(abs_path, self.core_path)
		parts      = rel_path.split(os.sep)
		name       = parts.pop()
		class_name = String.snake_to_camel(name[:-3])  # .py

		parts.insert(0, self.lib_name)
		parts.append(class_name)

		return '.'.join(parts)

	# Get expected class name from file path.
	# ----------------------------------------------------------------------
	def _get_class_name(self, path):
		name = os.path.splitext(os.path.basename(path))[0]
		return String.snake_to_camel(name)

	# Check whether object matches lib module class contract.
	# ----------------------------------------------------------------------
	def _is_module_class(self, obj):
		return (
			isinstance(obj, type)   and
			issubclass(obj, Module) and
			obj is not Module
		)

	# Check whether object matches lib module class contract.
	# ----------------------------------------------------------------------
	def _is_service_class(self, obj):
		return (
			self._is_module_class(obj) and
			issubclass(obj, Service)   and
			obj is not Service
		)

	# Load module file and extract Module subclass
	# ----------------------------------------------------------------------
	def _load_class(self, abs_path):
		if abs_path not in self._class_cache:
			name        = self._get_module_name(abs_path)
			module      = load_module(name, abs_path)
			class_name  = self._get_class_name(abs_path)
			
			cls = getattr(module, class_name, None)

			if cls is None:
				raise AttributeError(f'File `{abs_path}` defines no {class_name} class')
			if not self._is_module_class(cls):
				raise AttributeError(f'File `{abs_path}` defines no {self.lib_name}.Module')

			setattr(cls, '__lib__', self)                                    # Set __lib__ attr on Module
			setattr(cls, self.lib_name, self)                                # Set <lib> attr on Module
			setattr(cls, self.module_attr, self._get_module_name(abs_path))  # Set __mylib_module__

			if self._is_service_class(cls):
				cls = cls()

			self._class_cache[abs_path] = cls

		return self._class_cache[abs_path]

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

	# Late-bind object to lib
	# ----------------------------------------------------------------------
	def _attach(self, name, obj):
		setattr(obj, '__lib__', self)                              # Set __lib__ attr on Module
		setattr(obj, self.lib_name, self)                          # Set <lib> attr on Module
		setattr(obj, self.module_attr, f'{self.lib_name}.{name}')  # Set __mylib_module__
		setattr(self, name, obj)

	# ======================================================================
	# PUBLIC METHODS
	# ======================================================================

	# Initialize core paths and internal caches.
	# ----------------------------------------------------------------------
	def initialize(self, lib_name, lib_path=None):
		self.lib_name     = lib_name
		self.file_name    = get_class_file(self.__class__)
		self.lib_path     = os.path.dirname(os.path.abspath(self.file_name)) if lib_path is None else lib_path
		self.core_path    = os.path.join(self.lib_path, 'core')
		self.wl_core_path = os.path.join(os.path.dirname(__file__), 'core')
		self.module_attr = f'__{self.lib_name}_module__'

		sys.modules[self.lib_name] = self

		self._class_cache = {}
		self._ns_cache    = {}
		self._data_cache  = {}
		self._pkg_cache   = {}
		self._plugins     = {}

		self._attach('Events',        Events())
		self._attach('Conf',          Conf())
		self._attach('String',        String())
		self._attach('dual_method',   DualMethod)
		self._attach('dual_property', DualProperty)

		if self.verbose:
			print(f'\nInitialized library `{self.lib_name}`')
			print('-' * 70)
			print(f'– ' + f'Main `{self.lib_name}` directory'.ljust(27, ' ') + f' : `{self.lib_path}`')
			print(f'– Import files expected under : `{self.core_path}`')
			print(f'– All modules have property   : `self.{self.module_attr}`')
			print()

	# Resolve dotted path using WL lazy resolution
	# ----------------------------------------------------------------------
	def resolve(self, module_name: str):
		obj = self
		
		parts = module_name.split('.')
		if parts[0] == self.lib_name:
			parts.pop(0)

		for part in parts:
			obj = getattr(obj, part)

		return obj

	# Allowes to remotely import concrete wl library
	# ----------------------------------------------------------------------
	@classmethod
	def imp(cls, file_path):
		lib_name = os.path.splitext(os.path.basename(file_path))[0]
		module   = load_module(lib_name, file_path)

		for obj in module.__dict__.values():
			if isinstance(obj, type) and issubclass(obj, WhiteLabel):
				return obj

		raise RuntimeError(f'No WhiteLabel instance produced by `{file_path}`')

	# The main method you will use to create your library
	# ----------------------------------------------------------------------
	@classmethod
	def define(cls, lib_name, lib_file, **attrs):
		attrs['__file__'] = lib_file
		
		bases    = (cls,)
		lib_cls  = type(lib_name, bases, attrs)
		lib_inst = lib_cls(lib_path=os.path.dirname(lib_file))
		
		return lib_inst

	# Adds plugin for custom path matching and matched file processing
	# ----------------------------------------------------------------------
	def add_plugin(self, plugin_class):
		name = plugin_class.__name__
		if name in self._plugins:
			raise ValueError(f'Plugin `{name}` already registered')
		self._plugins[name] = plugin_class()

