


class InvalidSourceError(Exception):
	def __init__(self, arg):
		self.args = arg

	def __str__(self):
		return repr(self.value)


class NetworkError(Exception):
	def __init__(self, arg):
		self.args = arg

	def __str__(self):
		return repr(self.value)


class AptError(Exception):
	def __init__(self, arg):
		self.args = arg

	def __str__(self):
		return repr(self.value)
	


class InvalidHashError(Exception):
	def __init__(self, arg):
		self.args = arg

	def __str__(self):
		return repr(self.value)



class ExportDirDoesNotExist(Exception):
	def __init__(self, arg):
		self.args = arg

	def __str__(self):
		return repr(self.value)



class InvalidVersion(Exception):
	def __init__(self, arg):
		self.args = arg

	def __str__(self):
		return repr(self.value)