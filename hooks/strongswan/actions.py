
from strongswan.util import _check_call
from charmhelpers.core import hookenv
from json import loads 

def action_get():
	"""
	@params None
	@return action arguments in json format
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
	@params the message to log to juju-log and action-fail command
	@return None
	"""
	cmd = """action-fail "{}" """.format(message) 
	_check_call( cmd, shell=True )
	hookenv.log( message, level=hookenv.ERROR )



# python wrapper for action-set
def action_set( **kwargs ):
	"""
	@params variable number of key value pairs
	@return None
	@description Set key value pairs to return from action
	"""
	cmd = "action-set"
	for key, value in kwargs.items():
		cmd = """{} {}="{}" """.format(
			cmd,
			key,
			value
		)
	_check_call( cmd, shell=True )
	