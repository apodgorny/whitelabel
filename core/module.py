# ======================================================================
# CLASS Module
# ======================================================================

from types import MethodType


class ModuleMeta(type):

	def __new__(mcls, name, bases, namespace, **kwargs):
		namespace.setdefault('__has_own_module__', False)
		return super().__new__(mcls, name, bases, namespace, **kwargs)

	# String representation
	# ----------------------------------------------------------------------
	def __repr__(cls):
		module_name = getattr(cls, cls.__lib__.module_attr, cls.__module__)
		# print(cls.__name__, module_name, cls.__o_module__, cls.__module__)
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
		gray         = '\033[38;5;242m'
		reset        = '\033[0m'
		self_verbose = getattr(self, 'verbose', None)
		verbose      = self_verbose if self_verbose is not None else self.__lib__.verbose

		if verbose:
			module_attr = getattr(self, '__wl_module__')
			print(f'{gray}{module_attr}:{reset}', *args, **kwargs)

	def warn(self, *args, **kwargs):
		word_color  = '\033[38;5;172m'
		reset       = '\033[0m'

		args = list(args)
		args.insert(0, f'⚠️{word_color} WARNING:{reset}')
		return self.print(*args, **kwargs)

	def error(self, *args, **kwargs):
		word_color  = '\033[38;5;210m'
		reset       = '\033[0m'

		args = list(args)
		args.insert(0, f'🚫{word_color}ERROR:{reset}')
		self.print(*args, **kwargs)
		exit(0)
