
import subprocess as sp
import re
from json import dumps
from time import time, sleep
from os.path import getmtime
from urllib.request import urlretrieve
from hashlib import md5
from charmhelpers.core import hookenv
from charmhelpers.core.sysctl import create
from strongswan.constants import (
	CHECK, 
	IPTABLES, 
	DELETE, 
	DL_BASE_URL,
	CONFIG,
	IPV6_FORWARD,
	IPV4_FORWARD,
	SYSCTL_PATH,
	DPKG_LOCK_ERROR
)
from strongswan.errors import (
	NetworkError, 
	AptError, 
	InvalidHashError
)


def _check_call( cmd , fatal=False, message=None, quiet=False, 
	timeout=60, log=True, shell=False, check_output=False, log_cmd=True
	):
	"""
	@params	cmd: the list of command line args to call (can be string if Shell=True)
			fatal: do we raise an exception if one is thrown?
			message: the message to log to juju-log
			quiet: direct stdout and stderr to /dev/null
			timeout: timeout
			log: if an exception is thrown do we log to juju-log?
			shell: execute using the shell
			check_output: call check_output instead of check_call (we want output!)
			log_cmd: do we log the cmd called to juju-log? this is to silence the iptables calls
	@return None
	@description
	A wrapper to subprocess.check_output and check_call 
	"""
	if log_cmd:
		hookenv.log("Calling {0}".format(cmd) , level=hookenv.INFO )
	try:
		if quiet:
			return ( sp.check_call( cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL, 
				timeout=timeout, shell=shell) ) 
		else:
			if check_output:
				return ( sp.check_output( cmd, timeout=timeout, shell=shell ) )
			else:
				return ( sp.check_call( cmd, timeout=timeout, shell=shell) )
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
	

def make_rule(cmd, chain, rule_type, table=None ):
	"""
	@params cmd: a list of iptables command arguments (without iptables, rule_type, or chain )
			chain: the iptables chain we are modifying 
			rule_type: INSERT, DELETE, APPEND, FLUSH
			table: what table are we modifying (default is filter)
	@return None
	@description first checks to see if the rule already exists, if it does not, the check call
	will thrown an Exception, handler of the exception makes the rule. Opposite logic for delete,
	if the rule exists, then no exception will be thrown and we delete the rule.
	"""
	try:
		cmd = list(cmd)
		cmd.insert( 0, chain )
		cmd.insert( 0, CHECK )
		cmd.insert( 0, IPTABLES )
		_check_call(cmd, fatal=True, log=False, quiet=True, log_cmd=False )
	except sp.CalledProcessError:
		if rule_type != DELETE :
			cmd[1] = rule_type
			_check_call(cmd, fatal=True, log_cmd=False)
	else:
		if rule_type == DELETE :
			cmd[1] = DELETE
			_check_call(cmd, fatal=True, log_cmd=False)


def apt_install( pkgs ):
	"""
	@params: pkgs is a list of packages to install
	@description: call apt-get update then call apt-get install
	If we can't reach the first archive server, we cycle all the 
	archive servers returned from a DNS lookup by modifying the hosts file.
	@return None
	@exception AptError if we can't get the dpkg lock after 10 tries with intervals of 10 seconds.
	@exception NetworkError if we can't contact a single archive server.
	"""
	if isinstance( pkgs, list ):
		for cmd in [ "apt-get update -qq" , ["apt-get", "install", "-y", "-qq" ] ] : 
			apt_retry_count = 0
			apt_retry_max = 10
			apt_retry_wait = 10
			timed_out = False
			result = None
			while result == DPKG_LOCK_ERROR or result == None :
				try:
					if 'install' in cmd :
						_cmd = list(cmd)
						_cmd.extend(pkgs)
						result = _check_call(_cmd, timeout=300, fatal=True, quiet=True )
					else:
						result = _check_call( cmd, shell=True, timeout=100, fatal=True, quiet=True )
				except sp.CalledProcessError as e:
					apt_retry_count += 1
					if apt_retry_count > apt_retry_max : 
						raise AptError("Fatal Apt-error, check DNS or apt-lock")
					else:
						result = e.returncode
						sleep(apt_retry_wait)
				except sp.TimeoutExpired:
					hookenv.log("{0} Time Out".format(cmd), level=hookenv.INFO )
					if not timed_out : 
						dns_entries = get_archive_ip_addrs()
					if not dns_entries:
						raise NetworkError("Unable to contact archive server")
					else:
						_ip = dns_entries.pop()
						update_hosts_file( _ip , "archive.ubuntu.com" )
						update_hosts_file( _ip , "security.ubuntu.com" )
	else:
		hookenv.log("apt_install must be passed a list of packages", level=hookenv.ERROR )

def cp_hosts_file():
	"""
	Copy the hosts file for reference
	"""
	_check_call(['cp', '/etc/hosts', '/etc/hosts.original' ]) 
	

def flush_hosts_file():
	"""
	If the hosts file has been modified in the past 24 hours
	We will make sure we comment out the entries for the archive servers
	This is to prevent future upgrades from using a defined server in the hosts file
	"""
	if  ( ( time() - getmtime('/etc/hosts') ) ) < 86400 :
		update_hosts_file( '#1.2.3.4', 'archive.ubuntu.com' )
		update_hosts_file( '#1.2.3.4', 'security.ubuntu.com' )


def update_hosts_file( ip_addr , hostname ):
	"""
	@params ip_addr is a dotted quad IP address
			hostname is the alias for this IP
	@return None
	@description Finds all existing (non commented) lines in the /etc/hosts
	file and adds the ip_addr, hostname to the file if and only if 
	it does not exist already. 
	"""
	hookenv.log("Adding {0}\t{1} to /etc/hosts".format(ip_addr, hostname ), level=hookenv.INFO )
	aliased_hosts = []
	output_string = ""
	with open('/etc/hosts' , 'r') as hosts_file :
		for line in hosts_file:
			elem = re.findall('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\s\S*' , line )
			if elem:
				if elem[0].split()[1] == hostname:
					output_string += "{0}\t{1}\n".format(ip_addr, hostname)
				else:
					output_string += line
				aliased_hosts.append(elem[0].split()[1])
			else:
				output_string += line
		if hostname not in aliased_hosts:
			output_string += "{0}\t{1}\n".format(ip_addr, hostname)
	with open('/etc/hosts', 'w') as hosts_file:
		hosts_file.write(output_string)

			
def get_archive_ip_addrs():
	"""
	@params None
	@return A list of IP addresses for archive.ubuntu.com
	"""
	ip_list = []
	ip_addrs = _check_call(['dig', 'archive.ubuntu.com'], 
			check_output=True, fatal=True ).decode('utf-8').split('\n')
	for i in ip_addrs:
		i = i.split('\t')
		if i:
			if i[0] == 'archive.ubuntu.com.' :
				ip_list.append(i[4])
	return ip_list


def get_tarball( version ):
	"""
	@params version: the version of strongswan to fetch
	@description: grabs the strongswan tarball for the requested version
	and checks the tarball against the md5 hash
	@returns: the file path where the tarball was downloading to /tmp/
	"""
	if version == 'latest' :
		tarball = "strongswan.tar.gz"
		md5_hash_file = "strongswan.tar.gz.md5"
	else:
		tarball = "strongswan-{}.tar.gz".format(version)
		md5_hash_file = "strongswan-{}.tar.gz.md5".format(version)

	# TODO handle retrys and bad urls
	try:
		hookenv.log("Retrieving {}{}".format(DL_BASE_URL, tarball), 
			level=hookenv.INFO)
		urlretrieve( "{}{}".format(DL_BASE_URL, tarball ),
			"/tmp/{}".format(tarball) 
		)
		urlretrieve( "{}{}".format(DL_BASE_URL, md5_hash_file ),
			"/tmp/{}".format(md5_hash_file)
		)
	except Exception as err:
		hookenv.log(err)
		raise

	with open("/tmp/{}".format(md5_hash_file), 'r' ) as fd :
		original_hash = fd.read().split()[0]
	with open("/tmp/{}".format(tarball), 'rb' ) as fd :
		tarball_hash = md5( fd.read() ).hexdigest()
	if original_hash != tarball_hash :
		raise InvalidHashError("Invalid hash of {}".format(tarball) )

	return "/tmp/{}".format(tarball)


def configure_install(base_dir):
	"""
	@params base_dir: the base directory where the strongswan tarball was unpacked to.
	@return None
	@description pulls the comma sperated list of config options from the config file 
	and changes to the strongswan src directory and configures the install. Two options are
	included by default because we will break a lot of other stuff if they are not. 
	TODO: certain packages have dependencies, sanity check?
	"""
	cmd  = 'cd {}; '.format(base_dir)
	cmd += ' ./configure --prefix=/usr --sysconfdir=/etc'
	added_items = ["--prefix=/usr", "--sysconfdir=/etc"]
	for item in CONFIG.get("config_options").split(',') :
		if item:
			if item not in added_items:
				cmd += ' {}'.format(item)
				added_items.append(item)
	_check_call(cmd, shell=True, fatal=True, quiet=True )


def convert_to_seconds( lifetime ) :
	"""
	@params lifetime of a certificate in form 10y, 10d, 10h, 10m, or 10s
	@returns Number of seconds
	"""
	s = re.split(r'(\d*)(\D)', lifetime )
	if len(s) == 1:
		return int(s[0])
	_type = s[2]
	_quantity = int(s[1]) 
	if _type == 's' : 
		return _quantity
	elif _type ==  'm' :
		return (_quantity * 60)
	elif _type == 'h' :
		return (_quantity * 60 * 60 )
	elif _type == 'd' :
		return (_quantity * 60 * 60 * 24)
	elif _type == 'y' :
		return (_quantity * 60 * 60 * 24 * 365 )


def configure_sysctl():
	"""
	@description Reads Config file, and creates a sysctl.conf file
	"""
	_dict = {}
	if CONFIG.get("ip_forward") :
		_dict[IPV4_FORWARD] = 1
		_dict[IPV6_FORWARD] = 1
	create( dumps(_dict) , SYSCTL_PATH )


def cp_sysctl_file():
	"""
	Copies the sysctl file for future reference
	"""
	_check_call(['cp', '/etc/sysctl.conf', '/etc/sysctl.conf.original'] )
	

