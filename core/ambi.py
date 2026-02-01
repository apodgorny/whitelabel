from .module import Module


class Ambi(Module):
	def __init__(self, instance_method, class_method):
		self.instance_method = instance_method
		self.class_method    = class_method

	def __get__(self, obj, cls):
		return self.instance_method if obj is None else self.class_method