# ======================================================================
# String utilities for formatting, normalization, and validation.
# ======================================================================

from __future__ import annotations

import re, unicodedata

from .module import Module


class String(Module):

	# ANSI styles
	RESET         = '\033[0m'
	BOLD          = '\033[1m'
	ITALIC        = '\033[3m'
	UNDERLINE     = '\033[4m'
	STRIKETHROUGH = '\033[9m'

	# ANSI colors
	BLACK         = '\033[30m'
	RED           = '\033[31m'
	GREEN         = '\033[32m'
	YELLOW        = '\033[33m'
	BLUE          = '\033[34m'
	MAGENTA       = '\033[35m'
	CYAN          = '\033[36m'
	WHITE         = '\033[37m'

	GRAY          = '\033[90m'
	LIGHTRED      = '\033[91m'
	LIGHTGREEN    = '\033[92m'
	LIGHTYELLOW   = '\033[93m'
	LIGHTBLUE     = '\033[94m'
	LIGHTMAGENTA  = '\033[95m'
	LIGHTCYAN     = '\033[96m'
	LIGHTWHITE    = '\033[97m'
	LIGHTGRAY     = GRAY  # alias
	DARK_GRAY     = '\033[38;5;235m'

	# Convert string to a lowercase slug with a custom separator.
	# Optionally transliterate to ASCII.
	# ----------------------------------------------------------------------
	@staticmethod
	def slugify(
		text          : str,
		transliterate : bool = False,
		separator     : str  = '-'
	) -> str:
		if transliterate:
			text = unicodedata.normalize('NFKD', text)
			text = text.encode('ascii', 'ignore').decode('ascii')

		text = text.lower()
		text = re.sub(r'[^\w\s-]', '', text)
		text = re.sub(r'[\s_]+', separator, text)
		return text.strip(separator)

	# Adds `prefix` at the beginning of every non-empty line.
	# ----------------------------------------------------------------------
	@staticmethod
	def indent(text: str, prefix: str = '\t') -> str:
		return '\n'.join(
			f'{prefix}{line}' if line.strip() else line
			for line in text.splitlines()
		)

	# Removes common leading whitespace from all lines.
	# ----------------------------------------------------------------------
	@staticmethod
	def unindent(text: str) -> str:
		return re.sub(r'\n\s+', '\n', text).strip()

	# Checks if string is None or consists only of whitespace.
	# ----------------------------------------------------------------------
	@staticmethod
	def is_empty(s: str) -> bool:
		return not s or s.strip() == ''

	# Converts CamelCase or kebab-case to snake_case.
	# ----------------------------------------------------------------------
	@staticmethod
	def to_snake_case(name: str) -> str:
		import re
		name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
		return name.replace('-', '_')

	# Converts snake_case to CamelCase or camelCase depending on `capitalize` argument value.
	# ----------------------------------------------------------------------
	@staticmethod
	def snake_to_camel(name: str, capitalize=True) -> str:
		components = name.split('_')
		if capitalize:
			return ''.join(x.title() for x in components)
		return components[0] + ''.join(x.title() for x in components[1:])

	# Converts CamelCase to snake_case (preserving acronyms).
	# ----------------------------------------------------------------------
	@staticmethod
	def camel_to_snake(name: str) -> str:
		import re
		return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

	# Replaces multiple spaces/newlines with a single space.
	# ----------------------------------------------------------------------
	@staticmethod
	def normalize_whitespace(text: str) -> str:
		import re
		return re.sub(r'\s+', ' ', text).strip()

	# Underlines the given text.
	# ----------------------------------------------------------------------
	@staticmethod
	def underlined(text: str) -> str:
		return f'{String.UNDERLINE}{text}{String.RESET}'

	# Italicizes the given text.
	# ----------------------------------------------------------------------
	@staticmethod
	def italic(text: str) -> str:
		return f'{String.ITALIC}{text}{String.RESET}'

	# Strikes through the given text.
	# ----------------------------------------------------------------------
	@staticmethod
	def strikethrough(text: str) -> str:
		return f'{String.STRIKETHROUGH}{text}{String.RESET}'

	# Wraps text in ANSI color and/or styles.
	# ----------------------------------------------------------------------
	@staticmethod
	def color(text: str, color: str = None, styles: str = '') -> str:
		parts = []

		if styles:
			if 'b' in styles : parts.append(String.BOLD)
			if 'u' in styles : parts.append(String.UNDERLINE)
			if 'i' in styles : parts.append(String.ITALIC)

		if color:
			parts.append(color)

		if not parts:
			return text  # No color, no style, return unchanged

		return f"{''.join(parts)}{text}{String.RESET}"
