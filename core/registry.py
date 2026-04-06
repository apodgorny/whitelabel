# ======================================================================
# Registry storing named values
# ======================================================================

import os
import sys

from .module import Module


class Registry(Module):

	# ----------------------------------------------------------------------
	def __init__(self, name='Registry'):
		self._name = name
		self._data = {}

	# ----------------------------------------------------------------------
	def __getitem__(self, name):
		if name.startswith('_'):
			raise AttributeError(name)

		data = object.__getattribute__(self, '__dict__').get('_data')
		if data is None:
			raise AttributeError(name)

		if name in data:
			value = data[name]
		else:
			raise AttributeError(f'{self.__wl_module__}.{name} is not defined')

		return value

	# ----------------------------------------------------------------------
	def __setitem__(self, name, value):
		data = object.__getattribute__(self, '__dict__').get('_data')
		if data is None:
			raise AttributeError(name)

		data[name] = value

	# ----------------------------------------------------------------------
	def __getattr__(self, name):
		return self[name]

	# ----------------------------------------------------------------------
	def __setattr__(self, name, value):
		if name.startswith('_'):
			object.__setattr__(self, name, value)
		else:
			self[name] = value

	# ----------------------------------------------------------------------
	def __contains__(self, name):
		data = object.__getattribute__(self, '__dict__').get('_data')
		exists = False if data is None else name in data
		return exists

	# ----------------------------------------------------------------------
	def __repr__(self):
		data = object.__getattribute__(self, '__dict__').get('_data')
		n    = 0 if data is None else len(data)
		return f'<Registry {self._name} {n} keys>'


	# ----------------------------------------------------------------------
	def __str__(self):
		data  = object.__getattribute__(self, '__dict__').get('_data') or {}
		lines = []
		for k in sorted(data.keys()):
			lines.append(f'{k:<24}: {data[k]}')
		result = '\n'.join(lines)
		return result

	# ----------------------------------------------------------------------
	def items(self):
		data = object.__getattribute__(self, '__dict__').get('_data') or {}
		return data.items()

	# ----------------------------------------------------------------------
	def keys(self):
		data = object.__getattribute__(self, '__dict__').get('_data') or {}
		return data.keys()

	# ----------------------------------------------------------------------
	def values(self):
		data = object.__getattribute__(self, '__dict__').get('_data') or {}
		return data.values()

	# ----------------------------------------------------------------------
	def __iter__(self):
		data = object.__getattribute__(self, '__dict__').get('_data') or {}
		return iter(data)

	# ======================================================================
	# PUBLIC METHODS
	# ======================================================================

	# Get with default
	# ----------------------------------------------------------------------
	def get(self, name, default=None):
		return self._data.get(name, default)

	# To dict
	# ----------------------------------------------------------------------
	def to_dict(self):
		return dict(self._data)

	# Update registry from dict or another Registry
	# ----------------------------------------------------------------------
	def update(self, other=None, **kwargs):
		if other is not None:
			if isinstance(other, Registry):
				self._data.update(other._data)
			elif isinstance(other, dict):
				self._data.update(other)
			else:
				raise TypeError(
					f'Cannot update `{self._name}` from `{type(other)}`'
				)

		if kwargs:
			self._data.update(kwargs)

