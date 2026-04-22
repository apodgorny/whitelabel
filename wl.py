import os, sys

from lib.imports   import Imports
from lib.module    import Module, ModuleMeta
from lib.service   import Service
from lib.string    import String
from lib.file      import File
from lib.directory import Directory
from lib.plugin    import Plugin
from lib.undefined import Undefined
from lib.timer     import Timer
from lib.tester    import Tester



class WLMeta(type):

	# Create class
	# ----------------------------------------------------------------------
	def __new__(mcls, name, bases, namespace, path=None, plugins=None):
		module_name  = namespace.get('__module__')
		module       = sys.modules[module_name]
		lib_file     = os.path.realpath(module.__file__)
		lib_path     = os.path.dirname(lib_file)
		path         = path or os.path.join(lib_path, 'root')
		plugins_path = os.path.join(lib_path, 'plugins')

		if not os.path.exists(path):
			raise ValueError(f'Could not define class `{name}`. Path `{path}` does not exist')

		cls = super().__new__(mcls, name, bases, namespace)

		Undefined.lib = cls

		instance           = object.__new__(cls)
		instance.__name__  = name.lower()
		instance.__spec__  = None
		instance.__children__ = {}

		Imports.__lib__ = instance
		Tester.lib      = instance
		
		# Publish library name for import
		module.__dict__[instance.__name__] = instance
		sys.modules[instance.__name__]     = instance

		cls.__path__     = path
		cls.__lib_file__ = lib_file
		cls.__lib_path__ = lib_path
		cls.__instance__ = instance
		cls.__PLUGINS__  = {}
		cls.Tester       = Tester
		cls.tester       = Tester

		setattr(cls, name, cls)   # Make class available for import via instance

		for plugin_cls_name in plugins or []:
			plugin_route = f'{instance.__name__}.plugins.{plugin_cls_name}'
			plugin_cls   = Imports.get_class(instance, plugin_cls_name, plugins_path, plugin_route)
			if plugin_cls is not None:
				cls.__PLUGINS__[plugin_cls_name] = plugin_cls(instance)

		return cls


class WL(metaclass=WLMeta, plugins=['Py']): # , 'Data', 'Text'
	ModuleMeta   = ModuleMeta
	Module       = Module
	File         = File
	Directory    = Directory
	Plugin       = Plugin
	Service      = Service
	Imports      = Imports
	Undefined    = Undefined
	String       = String
	Timer        = Timer

	# Resolve attribute
	# ----------------------------------------------------------------------
	def __getattr__(self, name):
		value = None

		for instance in self.__instances__():
			value = instance.__children__.get(name)
			if value is not None:
				break

			value = instance.__resolve__(name, instance.__path__, self.__name__)
			if value is not None:
				instance.__children__[name] = value
				break

		if value is None:
			raise AttributeError(f'Library `{self.__name__}` has no attribute `{name}`')

		return value.load()

	# String representation
	# ----------------------------------------------------------------------
	def __repr__(self):
		return f'<Library `{self.__name__}`>'

	# Iterate lineage layers
	# ----------------------------------------------------------------------
	def __iter__(self):
		return Directory(self, self.__path__, self.__name__).__iter__()

	# Iterate lineage layers
	# ----------------------------------------------------------------------
	def __instances__(self):
		for cls in type(self).__mro__:
			if cls != object:
				yield cls.__instance__

	# Main resolution router
	# ----------------------------------------------------------------------
	def __resolve__(self, name, parent_path, parent_route):
		value = None
		path  = os.path.realpath(os.path.join(parent_path, name))

		if parent_path == self.__path__ and name in ['test', 'test.py']:
			value = None
		elif os.path.isdir(path):
			return Directory(self, path, f'{parent_route}.{name}')
		else:
			for instance in self.__instances__():
				for plugin_name, plugin in instance.__PLUGINS__.items():
					value = plugin(name, parent_path, parent_route)
					if value is not None: break
				if value is not None: break
		
		return value

	# ======================================================================
	# PUBLIC METHODS
	# ======================================================================

	# Called when library is fully assembled and ready to work
	# ----------------------------------------------------------------------
	def initialize(self):
		raise NotImplementedError(f'Library `{self.__name__}` must implement initialize()')

	# Create symlink
	# ----------------------------------------------------------------------
	def link(self, name, path):
		Directory(self, self.__path__, self.__name__).link(name, path)
