# ======================================================================
# CLASS Conf
# ======================================================================

from .service import Service


class Conf(Service):

	def __init__(self):
		try:
			from dotenv import dotenv_values
			object.__setattr__(self, '_data', dict(dotenv_values()))
		except ImportError:
			object.__setattr__(self, '_data', {})

	def __getitem__(self, name):
		data = object.__getattribute__(self, '__dict__').get('_data')
		if data is None:
			raise AttributeError(name)
		try:
			return data[name]
		except KeyError:
			raise AttributeError(name)

	def __setitem__(self, name, value):
		data = object.__getattribute__(self, '__dict__').get('_data')
		if data is None:
			raise AttributeError(name)
		data[name] = value

	def __getattr__(self, name):
		return self[name]

	def __setattr__(self, name, value):
		if name.startswith('_'):
			object.__setattr__(self, name, value)
		else:
			self[name] = value

	def __contains__(self, name):
		data = object.__getattribute__(self, '__dict__').get('_data')
		return False if data is None else name in data

	def __repr__(self):
		data = object.__getattribute__(self, '__dict__').get('_data')
		n = 0 if data is None else len(data)
		return f'<Conf {n} keys>'

	def __str__(self):
		data = object.__getattribute__(self, '__dict__').get('_data') or {}
		lines = []
		for k in sorted(data.keys()):
			lines.append(f'{k:<24}: {data[k]}')
		return '\n'.join(lines)

	# ==================================================================
	# PUBLIC METHODS
	# ==================================================================

	def to_dict(self):
		return dict(self._data)