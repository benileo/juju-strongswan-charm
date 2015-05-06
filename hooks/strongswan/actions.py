
from strongswan.util import _check_call
from charmhelpers.core import hookenv
from json import loads 

def action_get():
	"""
	:return: Action arguments in a dictionary
	"""
	try:
		data = _check_call([ "action-get", "--format", "json" ], 
					check_output=True)
		if data:
			data = loads(data.decode('utf-8'))
	except ValueError:
		action_fail("Action Get: Invalid json")
	return data


def action_fail( message ):
	"""
	Call action-fail command with error message
	:param message: error message as a string
	"""
	cmd = """action-fail "{}" """.format(message) 
	_check_call( cmd, shell=True )
	hookenv.log( message, level=hookenv.ERROR )


def action_set( **kwargs ):
	"""
	Set a variable number of key, value pairs using action-set
	:params kwargs	
	"""
	cmd = "action-set"
	for key, value in kwargs.items():
		cmd = """{} {}="{}" """.format(
			cmd,
			key,
			value
		)
	_check_call( cmd, shell=True )
	