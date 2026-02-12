# ======================================================================
# Time measurement module with named accumulators and summary reporting.
# ======================================================================

import time
from collections import defaultdict


class Timer:
	is_initialized = False
	last_timer     = None

	@classmethod
	def _init(cls):
		if not cls.is_initialized:
			cls._times = defaultdict(list)
			cls._start = defaultdict(lambda: False)
			cls.is_initialized = True

	# ======================================================================
	# PUBLIC METHODS
	# ======================================================================

	@classmethod
	def start(cls, name):
		cls._init()
		cls._start[name] = time.time()
		cls.last_timer   = name
		return cls

	@classmethod
	def stop(cls, name=None, report=False):
		cls._init()
		name = cls.last_timer if name is None else name

		if cls._start[name]:
			cls._times[name].append(time.time() - cls._start[name])

		cls._start[name] = False
		
		if report:
			cls.report_one(name)
		else:
			cls.last_timer = name
		return cls

	@classmethod
	def get_time(cls, name=None, p=3):
		cls._init()
		name = cls.last_timer if name is None else name
		return round(sum(cls._times[name]), p)

	@classmethod
	def report(cls, p=3, name=None):
		cls._init()
		if name is not None:
			name_len = max([len(k) for k in cls._times.keys()])
			for name in cls._times:
				cls.report_one(name)
		else:
			cls.report_one(name)
		return cls

	@classmethod
	def report_one(cls, name, p=3, _name_len=None):
		cls._init()
		name_len = len(name) if _name_len is None else _name_len
		
		times    = cls._times[name]
		total    = sum(times)
		length   = len(times)
		vmax     = max(times)
		vmin     = min(times)
		mean     = total / length

		s = f'{name:<{name_len}} : '

		if length == 1:
			s += f'{total:.{p}f}s'
		else:
			s += (
				f'{total:.{p}f}s ≈ {length:.0f} x {mean:.{p}f} - '
				f'({vmin:.{p}f}-{vmax:.{p}f})'
			)
		print(s)
		return cls