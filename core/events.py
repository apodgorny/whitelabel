

from collections import defaultdict

from .function import Function


class Events:

	# Initialize event registry (trigger -> list of callbacks)
	# ----------------------------------------------------------------------
	def __init__(self):
		self.triggers = defaultdict(list)

	# Attach callback to trigger
	# ----------------------------------------------------------------------
	def on(self, trigger, triggered):
		trigger   = Function(trigger)
		triggered = Function(triggered)

		self.triggers[trigger].append(triggered)

	# Detach callback from trigger
	# ----------------------------------------------------------------------
	def off(self, trigger, triggered):
		trigger   = Function(trigger)
		triggered = Function(triggered)

		if trigger in self.triggers:
			if triggered in self.triggers[trigger]:
				self.triggers[trigger].remove(triggered)

	# Trigger callbacks for given execution point
	# ----------------------------------------------------------------------
	def trigger(self, trigger):
		trigger = Function(trigger)

		if trigger in self.triggers:
			for triggered in self.triggers[trigger]:
				triggered({'foo': 'bar'})

	# Was trigger attached?
	# ----------------------------------------------------------------------
	def has(self, trigger):
		trigger = Function(trigger)
		return trigger in self.triggers
