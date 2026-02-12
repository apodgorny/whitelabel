# ======================================================================
# Time measurement module with named accumulators and summary reporting.
# ======================================================================

import time
from collections import defaultdict


class Timer:
	is_initialized = False

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
	def start(cls, name='Other'):
		cls._init()
		cls._start[name] = time.time()
		return cls

	@classmethod
	def stop(cls, name='Other', report=False):
		cls._init()
		if cls._start[name]:
			cls._times[name].append(time.time() - cls._start[name])
		cls._start[name] = False
		if report:
			cls.report_one(name)
		return cls

	@classmethod
	def report(cls, p=3, times=None):
		cls._init()
		name_len = max([len(k) for k in cls._times.keys()])
		for name in cls._times:
			cls.report_one(name)

	@classmethod
	def report_one(cls, name, p=3):
		name_len = len(name)
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