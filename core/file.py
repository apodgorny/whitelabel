
import os
import json
import yaml

from .module    import Module
from .service   import Service
from .common    import Common
from .fs_node   import FsNode
from .string    import String
from .directory import Directory


class File(FsNode):

	# ======================================================================
	# PRIVATE METHODS
	# ======================================================================

	# Build public lib module path.
	# ----------------------------------------------------------------------
	def _get_module_name(self, abs_path):
		rel_path   = os.path.relpath(abs_path, self.lib.core_path)
		parts      = rel_path.split(os.sep)
		name       = parts.pop()
		class_name = String.snake_to_camel(name[:-3])  # .py

		parts.insert(0, self.lib.lib_name)
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
		if abs_path not in self.lib._class_cache:
			name        = self._get_module_name(abs_path)
			module      = Common.load_module(name, abs_path)
			class_name  = self._get_class_name(abs_path)
			
			cls = getattr(module, class_name, None)

			if cls is None:
				raise AttributeError(f'File `{abs_path}` defines no {class_name} class')
			if not self._is_module_class(cls):
				raise AttributeError(f'File `{abs_path}` defines no {self.lib.lib_name}.Module')

			if self._is_service_class(cls):
				cls = cls(self.lib, name)

			Common.set_lib(cls, self.lib, name)

			self.lib._class_cache[abs_path] = cls

		return self.lib._class_cache[abs_path]

	# Load data file
	# ----------------------------------------------------------------------
	def _load_data(self, path):
		if path not in self.lib._data_cache:
			ext  = os.path.splitext(path)[1].lower()
			data = None

			with open(path, 'r', encoding='utf-8') as f:
				text = f.read()

			if   ext == '.json'           : data = json.loads(text)
			elif ext in ('.yml', '.yaml') : data = yaml.safe_load(text)

			if data is not None:
				self.lib._data_cache[path] = data

		return self.lib._data_cache.get(path)

	# Load text file
	# ----------------------------------------------------------------------
	def _load_text(self, path):
		with open(path, 'r') as f:
			return f.read()

	# ======================================================================
	# PUBLIC METHODS
	# ======================================================================

	def load(self):
		result = None

		# Custom plugins
		# - - - - - - - - - - - - - - - - - - - - - - - - - 
		for plugin_name, plugin in self.lib._plugins.items():
			try:
				if plugin.match(self.path):
					result = plugin.load(self.path, self)
					break
			except Exception as e:
				print(f'Plugin `{plugin_name}` raised: `{type(e).__name__}`: `{str(e)}`')

		if result is None:

			loaders = dict(
				py   = self._load_class,
				yml  = self._load_data,
				yaml = self._load_data,
				json = self._load_data,
				txt  = self._load_text,
				md   = self._load_text
			)
			
			if self.ext in loaders and os.path.isfile(self.path):
				result = loaders[self.ext](self.path)

		return result