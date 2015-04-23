
from strongswan.util import _check_call
from charmhelpers.core import hookenv
from json import loads 


# returns actions parameters in json format
def action_get():
	try:
		data = _check_call([ "action-get", "--format", "json" ], 
					check_output=True)
		if data:
			data = loads(data.decode('utf-8'))
	except ValueError:
		action_fail("Action Get: Invalid json")
	return data

def action_fail( message ):
	cmd = """action-fail "{}" """.format(message) 
	_check_call( cmd, shell=True )
	hookenv.log( message, level=hookenv.ERROR )



def action_set():
	pass




