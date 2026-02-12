# # ======================================================================
# # CLASS Service
# # ======================================================================

# import threading

# from .module import Module


# class Service(Module):
# 	_instance    = None
# 	_lock        = threading.Lock()
# 	_initialized = False

# 	def __new__(cls, *args, **kwargs):
# 		if cls._instance is None:
# 			with cls._lock:
# 				# Double-check pattern to prevent race conditions
# 				if cls._instance is None:
# 					cls._instance = super().__new__(cls)
# 		return cls._instance

# 	def __init__(self):
# 		if not self._initialized:
# 			self._initialized = True
# 			self.initialize()

# 	# Perform one-time initialization logic.
# 	# ------------------------------------------------------------------
# 	def initialize(self):
# 		raise NotImplementedError


# ======================================================================
# CLASS Service
# ======================================================================

import threading

from .module import Module
from .common import Common


class Service(Module):

	_lock = threading.Lock()

	# New.
	# ------------------------------------------------------------------
	def __new__(cls, lib, module_name):
		with cls._lock:
			inst = lib._services.get(cls, None)
			if inst is None:
				inst = super().__new__(cls)
				lib._services[cls] = inst
				Common.set_lib(inst, lib, module_name)
				# print(f'[SERVICE NEW] {lib.lib_name}.{cls.__name__} - CREATED')
			# else:
				# print(f'[SERVICE NEW] {lib.lib_name}.{cls.__name__} - FOUND')
			return inst

	# Init.
	# ------------------------------------------------------------------
	def __init__(self, lib=None, module_name=None):
		if '_initialized' not in self.__dict__:
			self.__dict__['_initialized'] = False

		if not self.__dict__['_initialized']:
			self.__dict__['_initialized'] = True
			self.initialize()

	# Perform one-time initialization logic.
	# ------------------------------------------------------------------
	def initialize(self):
		raise NotImplementedError
