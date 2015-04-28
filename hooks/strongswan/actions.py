
from strongswan.util import _check_call
from charmhelpers.core import hookenv
from json import loads 

# python wrapper for action-get 
def action_get():
	try:
		data = _check_call([ "action-get", "--format", "json" ], 
					check_output=True)
		if data:
			data = loads(data.decode('utf-8'))
	except ValueError:
		action_fail("Action Get: Invalid json")
	return data


# python wrapper for action-fail
def action_fail( message ):
	cmd = """action-fail "{}" """.format(message) 
	_check_call( cmd, shell=True )
	hookenv.log( message, level=hookenv.ERROR )



# python wrapper for action-set
def action_set( **kwargs ):
	cmd = "action-set"
	for key, value in kwargs.items():
		cmd = """{} {}="{}" """.format(
			cmd,
			key,
			value
		)
	_check_call( cmd, shell=True )
	