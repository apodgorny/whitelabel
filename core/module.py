# ======================================================================
# CLASS Module
# ======================================================================

from types import MethodType


class Module:

	# Intercept method access to inject event hooks
	# ----------------------------------------------------------------------
	def __getattribute__(self, name):
		from .events import Events
		attr = object.__getattribute__(self, name)

		if not name.startswith('_') and callable(attr) and self.__lib__.Events.has(attr):
			def wrapped(*args, **kwargs):
				Events.trigger(attr)
				fn = Function(attr)
				return fn(*args, **kwargs)

			attr = wrapped

		return attr

	# ----------------------------------------------------------------------
	# Attach callback to foreign method execution
	# ----------------------------------------------------------------------
	def on(self, foreign_method, own_method):
		Events.on(foreign_method, own_method)

	# ----------------------------------------------------------------------
	# Namespaced debug print
	# ----------------------------------------------------------------------
	def print(self, *args, **kwargs):
		gray  = '\033[38;5;242m'
		reset = '\033[0m'

		if not WhiteLabel.verbose:
			module_attr = getattr(self, self.__lib__.module_attr)
			print(f'{gray}{module_attr}:{reset}', *args, **kwargs)
