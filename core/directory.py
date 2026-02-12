# ======================================================================
# CLASS Namespace
# ======================================================================

import os

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
				module           = Common.load_module(f'{self.__lib__.lib_name}.{module_hash}', init_path)
				cache[init_path] = module
			else:
				module = cache[init_path]

		return module

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

	# Square bracket accessor – alternative to dot notation
	# ----------------------------------------------------------------------
	def __getitem__(self, name):
		return self.__lib__._resolve(name, self.path)


