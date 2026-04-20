import os
import json
import yaml


class Data:

	exts = ('yml', 'yaml', 'json')

	def load(self, lib, path, route):
		value     = None
		file_path = None
		ext       = None

		for current_ext in self.exts:
			current_path = f'{path}.{current_ext}'

			if os.path.isfile(current_path):
				file_path = current_path
				ext       = current_ext
				break

		if file_path is not None:
			if ext == 'json':
				with open(file_path, 'r', encoding='utf-8') as file:
					value = json.load(file)
			else:
				with open(file_path, 'r', encoding='utf-8') as file:
					value = yaml.safe_load(file)

		return value