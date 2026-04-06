# ======================================================================
# CLASS Namespace
# ======================================================================

import os
import fnmatch
import shutil

from .fs_node   import FsNode
from .common    import Common


class Directory(FsNode):

	# def __init__(self, path=None):
	# 	self.path = path

	# Resolve attribute access through resolver.
	# ----------------------------------------------------------------------
	def __getattr__(self, name):
		module = self._load_init()
		if module is not None and hasattr(module, name):
			return getattr(module, name)

		result = self.__lib__._resolve(name, self.path)
		if result is None:
			raise AttributeError(f'Module `{self.__lib__.lib_name}.{name}` does not exist or no loading method is provided')
		return result

	# Square bracket accessor – alternative to dot notation
	# ----------------------------------------------------------------------
	def __getitem__(self, key):
		result = None

		if not os.path.isdir(self.path):
			if isinstance(key, slice):
				result = []
			else:
				raise KeyError(key)
		else:
			names = sorted(os.listdir(self.path))

			if isinstance(key, slice):
				if key.step not in (None, 1):
					raise TypeError('Directory slice step must be None or 1')

				start = key.start
				stop  = key.stop
				result = [
					self._node(os.path.join(self.path, name))
					for name in names
					if (start is None or name >= start) and (stop is None or name <= stop)
				]
			elif not isinstance(key, str):
				raise TypeError('Directory key must be a string or slice')
			else:
				has_mask = any(ch in key for ch in '*?[]')
				if has_mask:
					result = [
						self._node(os.path.join(self.path, name))
						for name in names
						if fnmatch.fnmatch(name, key)
					]
				else:
					full_path = os.path.join(self.path, key)
					if os.path.exists(full_path):
						result = self._node(full_path)
					else:
						resolved_path = self.__lib__._resolve_basename_to_file(full_path)
						if resolved_path is not None:
							result = self._node(resolved_path)
						else:
							raise KeyError(key)

		return result

	# # Delete this directory recursively.
	# # ----------------------------------------------------------------------
	# def __del__(self):
	# 	if self.exists:
	# 		if os.path.isdir(self.path) and not os.path.islink(self.path):
	# 			shutil.rmtree(self.path)
	# 		else:
	# 			os.remove(self.path)

	# # Delete entries selected by [:], [start:stop], or mask.
	# # ----------------------------------------------------------------------
	# def __delitem__(self, key):
	# 	nodes = self[key]
	# 	if not isinstance(nodes, list):
	# 		nodes = [nodes]
	# 	for node in nodes:
	# 		del node

	# Itarate contents
	# ----------------------------------------------------------------------
	def __iter__(self):
		from .file import File

		for entry in os.listdir(self.path):
			if not entry.startswith('__'):
				full_path = os.path.join(self.path, entry)

				if os.path.isdir(full_path):
					yield Directory(self.lib, full_path)
				else:
					yield File(self.lib, full_path)

	# ======================================================================
	# PRIVATE METHODS
	# ======================================================================

	# Load package __init__.py if present.
	# ----------------------------------------------------------------------
	def _load_init(self):
		module    = None
		init_path = os.path.join(self.path, '__init__.py')

		if os.path.isfile(init_path):
			cache = self.__lib__._pkg_cache
			if init_path not in cache:
				module_hash      = abs(hash(init_path))
				module           = Common.load_module(f'{self.__lib__.lib_name}.{module_hash}', init_path)
				cache[init_path] = module
			else:
				module = cache[init_path]

		return module

	# Build filesystem node by path.
	# ----------------------------------------------------------------------
	def _node(self, full_path):
		from .file import File
		result = None
		if os.path.isdir(full_path) and not os.path.islink(full_path):
			result = Directory(self.lib, full_path)
		else:
			result = File(self.lib, full_path)
		return result

	# ======================================================================
	# PUBLIC METHODS
	# ======================================================================

	# Load current directory package module if __init__.py is present.
	# ----------------------------------------------------------------------
	def load(self):
		return self._load_init()
