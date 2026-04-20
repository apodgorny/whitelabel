import wl


class Foo(wl.Service):
	
	def initialize(self):
		print('Foo initilized')

	def run(self):
		print('Running')