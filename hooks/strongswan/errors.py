


class InvalidSourceError(Exception):
	def __init__(self, arg):
		self.args = arg

	def __str__(self):
		return repr(self.value)



class DnsError(Exception):
	def __init__(self, arg):
		self.args = arg

	def __str__(self):
		return repr(self.value)



class NetworkError(Exception):
	def __init__(self, arg):
		self.args = arg

	def __str__(self):
		return repr(self.value)


class AptLockError(Exception):
	def __init__(self, arg):
		self.args = arg

	def __str__(self):
		return repr(self.value)
	