import os


class Text:

	exts = ('txt', 'md')

	def load(self, lib, path, route):
		value     = None
		file_path = None

		for ext in self.exts:
			current_path = f'{path}.{ext}'

			if os.path.isfile(current_path):
				file_path = current_path
				break

		if file_path is not None:
			# print(f'Plugin loading text from {file_path}')

			with open(file_path, 'r', encoding='utf-8') as file:
				value = file.read()

		return value