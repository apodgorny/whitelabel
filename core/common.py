import os
import sys
import importlib.util


_MODULE_CACHE = {}

class Common:
	@classmethod
	def set_lib(cls, obj, lib, module_name=None):
		__module_attr__       = f'__{lib.lib_name}_module__'
		__module_attr_value__ = module_name if module_name is not None else f'{lib.lib_name}.{obj.__class__.__name__}'

		setattr( obj, '__lib__',         lib)                    # Set __lib__ attr on Module
		setattr( obj, '__module_attr__', __module_attr__)        # Set name of module attr
		setattr( obj,  __module_attr__,  __module_attr_value__)  # Set __mylib_module__
		setattr( obj, '__wl_module__',   __module_attr_value__)  # Set __wl_module__, as shortcut inside lib

	# Get class module file
	# ----------------------------------------------------------------------
	@classmethod
	def get_class_file(cls, file_cls):
		module = sys.modules.get(file_cls.__module__)
		if module and hasattr(module, '__file__'):
			return module.__file__
		return None

	# Load module
	# ----------------------------------------------------------------------
	@classmethod
	def load_module(cls, name, path):
		abspath = os.path.abspath(path)

		if abspath not in _MODULE_CACHE:
			spec   = importlib.util.spec_from_file_location(name, path)
			module = importlib.util.module_from_spec(spec)
			module.__file__ = path    # Set __file__ to get later at get_class_file
			if name not in sys.modules:
				sys.modules[name] = module
			spec.loader.exec_module(module)
			_MODULE_CACHE[abspath] = module

		return _MODULE_CACHE[abspath]