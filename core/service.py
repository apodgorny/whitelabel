# ======================================================================
# CLASS Service
# ======================================================================

import threading

from .module import Module


class Service(Module):
	_instance    = None
	_lock        = threading.Lock()
	_initialized = False

	def __new__(cls, *args, **kwargs):
		if cls._instance is None:
			with cls._lock:
				# Double-check pattern to prevent race conditions
				if cls._instance is None:
					cls._instance = super().__new__(cls)
		return cls._instance

	def __init__(self):
		if not self._initialized:
			self._initialized = True
			self.initialize()

	# Perform one-time initialization logic.
	# ------------------------------------------------------------------
	def initialize(self):
		raise NotImplementedError

