#!/usr/bin/env python3

import subprocess as sp
from charmhelpers.core import hookenv
from strongswan.constants import CHECK, IPTABLES, DELETE

# wrapper to check_call
def _check_call( cmd , fatal=False, 
	message=None, quiet=False, 
	timeout=60, log=True
	):
	hookenv.log("Calling {0}".format(cmd) , level=hookenv.INFO )
	try:
		if quiet:
			return ( sp.check_call( cmd, stdout=sp.DEVNULL, , stderr=sp.DEVNULL, timeout=timeout ) ) 
		else:
			return ( sp.check_call( cmd, timeout=timeout ) )
	except sp.CalledProcessError as err:
		if log:
			hookenv.log("\n\tMessage: {}\n\tReturn Code: {}\n\tOutput: {}\n\tCommand:{}\n\t".format(
				message,
				err.returncode,
				err.output,
				err.cmd 
				), level=hookenv.ERROR
			)
		if fatal:
			raise
	


# if the rule does not already exist, make the rule.
def make_rule(cmd, chain, rule_type):
	try:
		cmd = list(cmd)
		cmd.insert( 0, chain )
		cmd.insert( 0, CHECK )
		cmd.insert( 0, IPTABLES )
		_check_call(cmd, message="Checking IPtables rule", fatal=True, log=False, quiet=True )
	except sp.CalledProcessError:
		if rule_type != DELETE :
			cmd[1] = rule_type
			_check_call(cmd, fatal=True, message="Creating IPTables rule")
	else:
		if rule_type == DELETE :
			cmd[1] = DELETE
			_check_call(cmd, fatal=True, message="Deleting IPTables rule")
