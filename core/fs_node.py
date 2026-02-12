import os


class FsNode:

	def __init__(self, lib, path):
		self.lib           = lib
		self.path          = os.path.abspath(path)
		self.mod_path, ext = os.path.splitext(self.path)
		self.name          = os.path.basename(self.mod_path)
		self.ext           = ext.strip('.') if ext else None
		self.mtime         = int(os.path.getmtime(self.path)) if self.exists else None

	@property
	def parent(self):
		parent_path = os.path.dirname(self.path)
		return FsNode(self.lib, parent_path) if parent_path and parent_path != self.path else None

	@property
	def exists(self):
		return os.path.exists(self.path)

	@property
	def is_directory(self):
		return os.path.isdir(self.path)

	# Repr
	# ----------------------------------------------------------------------
	def __repr__(self):
		path = object.__getattribute__(self, 'path')
		return f'<{self.lib.__class__.__name__}.{self.__class__.__name__} path="{path}">'