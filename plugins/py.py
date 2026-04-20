import os

import wl


class Py(wl.Plugin):

	EXTENSIONS = ['py']

	def __resolve__(self, name, parent_path, parent_route):
		path       = None
		route      = None
		class_name = None

		# bar.py /mypath/foo wl
		# - - - - - - - - - - - - - - - - - - - - 
		try_path = os.path.join(parent_path, name)
		if os.path.isfile(try_path):
			class_name = self.lib.String.snake_to_camel(os.path.splitext(name)[0])
			route      = f'{parent_route}.{class_name}'
			path       = try_path

		# Bar /mypath/foo wl
		# - - - - - - - - - - - - - - - - - - - - 
		else:
			module_name = self.lib.String.camel_to_snake(name)
			for ext in self.EXTENSIONS:
				try_path = os.path.join(parent_path, f'{module_name}.{ext}')
				if os.path.isfile(try_path):
					class_name = name
					route      = f'{parent_route}.{name}'
					path       = try_path
					break

		return path, route, class_name

	def __call__(self, name, parent_path, parent_route):
		file = None
		lib  = self.lib

		path, route, class_name = self.__resolve__(name, parent_path, parent_route)

		if path is not None:
			
			# - - - - - - - - - - - - - - - - - - - - 
			# Load method
			# - - - - - - - - - - - - - - - - - - - - 
			def load_method():
				cls = lib.Import.get_class(lib, class_name, path, dict(
					__lib__   = lib,
					__route__ = route
				))
				if not issubclass(cls, (lib.Module, lib.ModuleMeta)):
					raise Exception(f'Class `{route}` does not extend from `Module`')
				elif issubclass(cls, lib.Service):
					cls = cls()
				return cls
			# - - - - - - - - - - - - - - - - - - - - 
			# Hash method
			# - - - - - - - - - - - - - - - - - - - - 
			def hash_method():
				return os.path.getmtime(path)
			# - - - - - - - - - - - - - - - - - - - - 

			file = self.lib.File(self.lib, path, route, load_method, hash_method)
		
		return file