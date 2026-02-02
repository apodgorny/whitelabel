# ======================================================================
# Allows same name method/property for class and instance
# 
# Usage:
# -----------------
# class MyClass:
#    @<my_lib>.DualMethod
#    def my_method(cls, self=None):
#        if self is None:
#            return do_class_stuff()
#        return do_instance_stuff()
#
# ======================================================================

from .module import Module


class DualProperty(Module):
    def __init__(self, property):
        self.property = property

    def __get__(self, instance, owner):
		# Parameters are swapped for cognitive simplicity
		# Left to right from abstract to concrete.
		# def my_method(cls, self)
		# Also, self is optional, to the right of cls – non optional

        return self.property(owner, instance)
		

class DualMethod(Module):
	def __init__(self, method):
		self.method = method

	def __get__(self, instance, owner):
		# Parameters are swapped for cognitive simplicity
		# Left to right from abstract to concrete.
		# def my_method(cls, self)
		# Also, self is optional, to the right of cls – non optional

		def call(*args, **kwargs):
			return self.method(owner, instance, *args, **kwargs)
			
		return call
