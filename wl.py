import os
import sys
import importlib.util
import re
import threading

import json
import yaml

from .core.timer     import Timer
from .core.module    import Module
from .core.directory import Directory
from .core.file      import File
from .core.service   import Service
from .core.conf      import Conf
from .core.events    import Events
from .core.string    import String
from .core.dual      import DualMethod, DualProperty

from .core.common    import Common


# ======================================================================
# CLASS WhiteLabel
# ======================================================================

class WL:
	Module     = Module
	Directory  = Directory
	File       = File
	String     = String
	Service    = Service
	Timer      = Timer

	undefined  = '__undefined__'
	verbose    = True

	_instances = {}  # cls : inst
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

		result = self._resolve(name, self.core_path)
		if result is None:
			raise AttributeError(f'Module `{self.lib_name}.{name}` does not exist or no loading method is provided')

		return result

	# Resolve dotted path using WL lazy resolution
	# ----------------------------------------------------------------------
	def __getitem__(self, module_name):
		obj = self
		
		parts = module_name.split('.')
		if parts[0] == self.lib_name:
			parts.pop(0)

		for part in parts:
			obj = getattr(obj, part)

		return obj

	# Repr
	# ----------------------------------------------------------------------
	def __repr__(self):
		return f'<Whitelabel Library `{self.lib_name}` path="{self.lib_path}">'

	# ======================================================================
	# PRIVATE METHODS
	# ======================================================================

	# Modules are provided without ext, need to resolve
	# ----------------------------------------------------------------------
	def _resolve_basename_to_file(self, path):
		dir_path  = os.path.dirname(path)
		base_name = os.path.basename(path)

		result = None

		if os.path.isdir(dir_path):
			for file_name in os.listdir(dir_path):
				name, ext = os.path.splitext(file_name)

				if name == base_name and ext:
					result = os.path.join(dir_path, file_name)
					break

		return result

	# Resolve module or namespace by name.
	# ----------------------------------------------------------------------
	def _resolve(self, name, path):
		# print(f'[WL RESOLVE] name={name}, path={path}')
		path_no_ext = os.path.join(path, String.camel_to_snake(name))
		result      = None

		# Namespace
		# - - - - - - - - - - - - - - - - - - - - - - - - - 
		if os.path.isdir(path_no_ext):
			if path_no_ext in self._ns_cache:
				result = self._ns_cache[path_no_ext]
			else:
				result = Directory(self, path_no_ext)
				setattr(result, '__lib__', self)
				self._ns_cache[path_no_ext] = result

		# File
		# - - - - - - - - - - - - - - - - - - - - - - - - - 
		else:
			resolved_path = self._resolve_basename_to_file(path_no_ext)
			# print(f'[WL RESOLVE] resolved_path={resolved_path}')
			if resolved_path is not None:
				if resolved_path in self._file_cache:
					result = self._file_cache[resolved_path]
				else:
					result = File(self, resolved_path).load()
					self._file_cache[resolved_path] = result

		return result

	# Import additional library alongside the current
	# ----------------------------------------------------------------------
	def _imp(self, file_path):
		lib_name = os.path.splitext(os.path.basename(file_path))[0]
		module   = Common.load_module(lib_name, file_path)

		for obj in module.__dict__.values():
			if isinstance(obj, type) and issubclass(obj, WL):
				return obj

		raise RuntimeError(f'No WhiteLabel instance produced by `{file_path}`')

	# Import many libs alongside the current
	# ----------------------------------------------------------------------
	def _imp_many(self, import_libs):
		libs = {}

		if isinstance(import_libs, list):
			for import_lib in import_libs:
				self._imp(import_lib)
		
		for lib_inst in self.__class__._instances.values():
			libs[lib_inst.lib_name] = lib_inst

		return libs

	# Late-bind object to lib
	# ----------------------------------------------------------------------
	def _attach(self, name, obj, instantiate=False):
		Common.set_lib(obj, self)

		if instantiate:
			setattr(self, name, obj(self, None))
		else:
			setattr(self, name, obj)

	# ======================================================================
	# PUBLIC METHODS
	# ======================================================================

	# Initialize core paths and internal caches.
	# ----------------------------------------------------------------------
	def initialize(self, lib_name, lib_path=None, on_initialize=None):
		self.lib_name     = lib_name
		self.file_name    = Common.get_class_file(self.__class__)
		self.lib_path     = os.path.dirname(os.path.abspath(self.file_name)) if lib_path is None else lib_path
		self.core_path    = os.path.join(self.lib_path, 'core')
		self.wl_core_path = os.path.join(os.path.dirname(__file__), 'core')
		self.module_attr = f'__{self.lib_name}_module__'

		sys.modules[self.lib_name] = self
		self.__path__ = [self.lib_path]

		self._class_cache = {}
		self._file_cache  = {}
		self._ns_cache    = {}
		self._data_cache  = {}
		self._pkg_cache   = {}
		self._plugins     = {}
		self._services    = {}  # This is where instances of singleton services live for each lib

		self._attach( 'Events',        Events,       instantiate=True  )
		self._attach( 'Conf',          Conf,         instantiate=True  )
		self._attach( 'String',        String,       instantiate=True  )
		self._attach( 'dual_method',   DualMethod,   instantiate=False )
		self._attach( 'dual_property', DualProperty, instantiate=False )

		# Common.set_lib(self, Conf)
		# self.Conf = Conf(self)

		if self.verbose:
			print(f'\nInitialized library `{self.lib_name}`')
			print('-' * 70)
			print(f'– ' + f'Main `{self.lib_name}` directory'.ljust(27, ' ') + f' : `{self.lib_path}`')
			print(f'– Import files expected under : `{self.core_path}`')
			print(f'– All modules have property   : `self.{self.module_attr}`')
			print()

	# Adds plugin for custom path matching and matched file processing
	# ----------------------------------------------------------------------
	def add_plugin(self, plugin_class):
		name = plugin_class.__name__
		if name in self._plugins:
			raise ValueError(f'Plugin `{name}` already registered')
		self._plugins[name] = plugin_class()

	# The main method you will use to create your library
	# ----------------------------------------------------------------------
	@classmethod
	def define(cls, lib_name, lib_file, import_libs=None, on_initialize=None, **attrs):
		attrs['__file__'] = lib_file
		
		bases    = (cls,)
		lib_cls  = type(lib_name, bases, attrs)
		lib_inst = lib_cls(
			lib_path = os.path.dirname(lib_file),
		)

		all_libs = lib_inst._imp_many(import_libs)

		# print({lib_inst.name: lib_inst for lib_inst in cls._instances.values()})
		if callable(on_initialize):
			on_initialize(**all_libs)
		
		return lib_inst

