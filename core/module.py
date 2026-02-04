# ======================================================================
# CLASS Module
# ======================================================================

from types import MethodType


class ModuleMeta(type):

	# def __new__(mcls, name, bases, dct):
	# 	# Customization logic
	# 	# mcls: The metaclass itself (e.g., CustomMeta)
	# 	# name: The name of the class being created (e.g., "MyClass")
	# 	# bases: A tuple of the base classes (e.g., (object,))
	# 	# dct: A dictionary of the class attributes and methods (namespace)

	# 	# Call the superclass's __new__ to actually create the class object
	# 	new_class = super().__new__(mcls, name, bases, dct)
	# 	print('META NEW FOR', name)
	# 	# print('LIB:', new_class.__lib__)
		
	# 	# Further modifications can be made to new_class here

	# 	return new_class

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
			module_attr = getattr(self, self.__lib__.module_attr)
			print(f'{gray}{module_attr}:{reset}', *args, **kwargs)
