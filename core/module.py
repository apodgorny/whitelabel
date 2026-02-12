# ======================================================================
# CLASS Module
# ======================================================================

from types import MethodType


class ModuleMeta(type):

	# String representation
	# ----------------------------------------------------------------------
	def __repr__(cls):
		module_name = getattr(cls, cls.__lib__.module_attr, cls.__module__)
		return f'<class \'{module_name}\'>'


class Module(metaclass=ModuleMeta):

	_instance_counter = 0

	# Using new to avoid having to call super().__init__() everywhere
	# ----------------------------------------------------------------------
	def __new__(cls, *args, **kwargs):
		obj = super().__new__(cls)
		Module._instance_counter += 1
		obj.__instance_id__ = Module._instance_counter
		return obj

	# Intercept method access to inject event hooks
	# ----------------------------------------------------------------------
	def __getattr__(self, name):
		from .events import Events
		attr = object.__getattribute__(self, name)

		if not name.startswith('_') and callable(attr) and Events.has(attr):
			def wrapped(*args, **kwargs):
				Events.trigger(attr)
				fn = Function(attr)
				return fn(*args, **kwargs)

			return wrapped

		return attr

	# Attach callback to foreign method execution
	# ----------------------------------------------------------------------
	def on(self, foreign_method, own_method):
		Events.on(foreign_method, own_method)

	# Namespaced debug print
	# ----------------------------------------------------------------------
	def print(self, *args, **kwargs):
		gray  = '\033[38;5;242m'
		reset = '\033[0m'

		if self.__lib__.verbose:
			module_attr = getattr(self, '__wl_module__')
			print(f'{gray}{module_attr}:{reset}', *args, **kwargs)
