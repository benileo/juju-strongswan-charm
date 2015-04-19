
import subprocess as sp
from charmhelpers.core import hookenv
from strongswan.constants import CHECK, IPTABLES, DELETE
from strongswan.errors import DnsError, NetworkError, AptLockError
from strongswan.hosts import update_hosts_file, get_archive_ip_addrs

# wrapper to check_call
def _check_call( cmd , fatal=False, 
	message=None, quiet=False, 
	timeout=60, log=True
	):
	hookenv.log("Calling {0}".format(cmd) , level=hookenv.INFO )
	try:
		if quiet:
			return ( sp.check_call( cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL, timeout=timeout ) ) 
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



# runs apt-get command handles dpkg locks and archive server unavailability
# TODO, i believe apt-get returns if it can't contact a DNS server
# handle this error appropriately
def run_apt_command(cmd, timeout=60 , apt_cmd='install'):

	apt_retry_count = 0
	apt_retry_max = 0
	apt_retry_wait = 10
	dpkg_lock_error = 100
	timed_out = False
	result = None

	# build the command list
	cmd.insert(0, '-qq' )
	if apt_cmd == 'install' :
		cmd.insert(0, '-y' )
	cmd.insert(0, apt_cmd)
	cmd.insert(0, 'apt-get')
		

	# call the apt command
	while result is None or result == dpkg_lock_error :
		try:
			result = _check_call( cmd, timeout=timeout, quiet=True, fatal=True )
		
		# Unable to get that lock
		except sp.CalledProcessError as e:
			apt_retry_count += 1
			if apt_retry_count > apt_retry_max : 
				raise AptLockError("Unable to acquire DPKG Lock")
			result = e.returncode
			sleep(apt_retry_wait)

		# The command has timed out - wonder why - lets try some DNS hacks.
		except sp.TimeoutExpired:
			hookenv.log("{0} command has timed out....".format(cmd), level=hookenv.INFO )
			if not timed_out :
				timed_out = True
				dns_entries = get_archive_ip_addrs()
				if not dns_entries:
					raise DnsError("Dns Error")
			if not dns_entries:
				raise NetworkError("Unable to contact an archive server.")
			else:
				_ip = dns_entries.pop()
				update_hosts_file( _ip , "archive.ubuntu.com" )
				update_hosts_file( _ip , "security.ubuntu.com" )
