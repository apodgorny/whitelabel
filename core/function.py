# ======================================================================
# Function — stable runtime identity for executable units
# ======================================================================
#
# Python bound methods are ephemeral views:
#   obj.method creates a new object on every access and cannot be used
#   as a stable identity for events, hooks, history, or lifecycle control.
#
# Function exists to provide a canonical, hashable identity for execution:
#   - instance methods   → (object, function)
#   - class methods      → (class, function)
#   - static methods     → (None, function)
#
# This separation is required to:
#   - attach / detach callbacks reliably (on/off)
#   - unify sync and async execution
#   - address execution independent of call sites
#   - support history, replay, and agent orchestration
#
# In short:
#   bound method = how to call
#   Function     = what is being called
#
# ======================================================================


class Function:

	# Initialize from callable (method, function, staticmethod or Function)
	# ----------------------------------------------------------------------
	def __init__(self, callee):
		# Idempotent: Function(Function(...)) → same identity
		if isinstance(callee, Function):
			self.owner = callee.owner
			self.func  = callee.func
			return

		# bound method (instance or classmethod)
		if hasattr(callee, '__self__'):
			self.owner = callee.__self__     # instance | class
			self.func  = callee.__func__     # underlying function
		# plain function or staticmethod
		else:
			self.owner = None
			self.func  = callee

	# Call underlying function (sync or async)
	# ----------------------------------------------------------------------
	def __call__(self, *args, **kwargs):
		if self.owner is not None : result = self.func(self.owner, *args, **kwargs)
		else                      : result = self.func(*args, **kwargs)

		# async path: return awaitable transparently
		if hasattr(result, '__await__'):
			async def waiter():
				return await result
			return waiter()

		# sync path
		return result

	# Hash based on owner identity and function definition
	# ----------------------------------------------------------------------
	def __hash__(self):
		return hash((
			id(self.owner) if self.owner is not None else None,
			getattr(self.func, '__module__', None),
			self._func_id(),
		))

	# Equality by exact owner and function identity
	# ----------------------------------------------------------------------
	def __eq__(self, other):
		if not isinstance(other, Function):
			return False
		return (
			self.owner is other.owner and
			self.func  is other.func
		)

	# Human-readable representation for debugging and logs
	# ----------------------------------------------------------------------
	def __repr__(self):
		owner = (
			f'instance:{id(self.owner)}'
			if self.owner is not None and not isinstance(self.owner, type)
			else f'class:{self.owner.__module__}.{self.owner.__qualname__}'
			if isinstance(self.owner, type)
			else 'static'
		)
		return f'<Function {owner} {self.func.__module__}.{self.func.__qualname__}>'

	def _func_id(self):
		f = self.func
		if hasattr(f, '__qualname__') : return f.__qualname__
		if hasattr(f, '__name__')     : return f.__name__
		# fallback: type-based identity
		return f.__class__.__qualname__

	# ======================================================================
	# PUBLIC METHODS
	# ======================================================================

	# Detect whether underlying function is async (coroutine)
	# ----------------------------------------------------------------------
	def is_async(self):
		return hasattr(self.func, '__call__') and (
			hasattr(self.func, '__code__') and
			(self.func.__code__.co_flags & 0x80) != 0   # CO_COROUTINE
		)
