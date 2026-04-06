# ======================================================================
# Usage examples
# ======================================================================
#
# Timer.start('load')
# ...
# Timer.stop()
# Timer.report()
#
# Timer.start('query')
# ...
# Timer.stop(report=True)
#
# Timer.start('parse')
# ...
# Timer.stop()
# print(Timer.get_time('parse'))
#
# Timer.start('a')
# ...
# Timer.stop()
# Timer.start('a')
# ...
# Timer.stop()
# Timer.report(name='a')
#
# ======================================================================

# ======================================================================
# Time measurement module with named accumulators and summary reporting.
# ======================================================================

import time
from collections import defaultdict


class Timer:
	enabled        = True
	is_initialized = False
	last_timer     = None

	# PRIVATE METHODS
	# ======================================================================

	# Init
	# ----------------------------------------------------------------------
	@classmethod
	def _init(cls):
		if not cls.is_initialized:
			cls._times = defaultdict(list)
			cls._start = defaultdict(lambda: False)
			cls.is_initialized = True

	# Format duration
	# ----------------------------------------------------------------------
	@classmethod
	def _format_duration(cls, value):
		abs_value = abs(value)
		result    = None

		if abs_value >= 1:
			result = f'{value:.3f}s'
		elif abs_value >= 1e-3:
			result = f'{value * 1e3:.3f}ms'
		elif abs_value >= 1e-6:
			result = f'{value * 1e6:.3f}µs'
		else:
			result = f'{value * 1e9:.3f}ns'

		return result

	# Build report row
	# ----------------------------------------------------------------------
	@classmethod
	def _report_row(cls, name):
		times = cls._times[name]
		row   = [name, ':', cls._format_duration(0), '', '', '', '', '', '', '', '']

		if len(times) > 0:
			total  = sum(times)
			length = len(times)
			vmax   = max(times)
			vmin   = min(times)
			mean   = total / length

			row[2] = cls._format_duration(total)

			if length > 1:
				row[3]  = '≈'
				row[4]  = str(length)
				row[5]  = 'x'
				row[6]  = cls._format_duration(mean)
				row[7]  = '('
				row[8]  = cls._format_duration(vmin)
				row[9]  = '-'
				row[10] = cls._format_duration(vmax) + ')'

		return row

	# Print row
	# ----------------------------------------------------------------------
	@classmethod
	def _print_row(cls, row, widths):
		parts = []
		i     = 0

		for i in range(len(widths)):
			parts.append(f'{row[i]:<{widths[i]}}')

		parts.append(row[len(widths)])
		print(' '.join(parts))

	# PUBLIC METHODS
	# ======================================================================

	# Start timer
	# ----------------------------------------------------------------------
	@classmethod
	def start(cls, name):
		if cls.enabled:
			cls._init()
			cls._start[name] = time.perf_counter()
			cls.last_timer   = name
		return cls

	# Stop timer
	# ----------------------------------------------------------------------
	@classmethod
	def stop(cls, name=None, report=False):
		if cls.enabled:
			cls._init()
			name = cls.last_timer if name is None else name

			if name is not None:
				if cls._start[name]:
					cls._times[name].append(time.perf_counter() - cls._start[name])

				cls._start[name] = False
				cls.last_timer   = name

				if report:
					cls.report_one(name)

		return cls

	# Reset timers
	# ----------------------------------------------------------------------
	@classmethod
	def reset(cls):
		cls._times = defaultdict(list)
		cls._start = defaultdict(lambda: False)
		cls.last_timer = None
		cls.is_initialized = True
		return cls

	# Get total time
	# ----------------------------------------------------------------------
	@classmethod
	def get_time(cls, name=None, p=6):
		total = 0

		if cls.enabled:
			cls._init()
			name = cls.last_timer if name is None else name

			if name is not None:
				total = round(sum(cls._times[name]), p)

		return total

	# Report all timers or one timer
	# ----------------------------------------------------------------------
	@classmethod
	def report(cls, name=None):
		if cls.enabled:
			cls._init()

			if name is None:
				names = list(cls._times.keys())
			else:
				names = [name]

			rows = [cls._report_row(name) for name in names]

			if len(rows) > 0:
				widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]) - 1)]

				for row in rows:
					cls._print_row(row, widths)

		return cls

	# Report one timer
	# ----------------------------------------------------------------------
	@classmethod
	def report_one(cls, name):
		if cls.enabled:
			cls._init()
			cls.report(name=name)
		return cls