
import subprocess as sp
import re
from json import dumps
from time import time, sleep
from os.path import getmtime
from urllib.request import urlopen
from urllib.error import URLError
from hashlib import md5
from charmhelpers.core import hookenv
from charmhelpers.core.sysctl import create
from strongswan.constants import (
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
	timeout=300, log=True, shell=False, check_output=False, log_cmd=True
	):
	"""
	@params	
	cmd: the list of command line args to call (can be string if Shell=True)
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
		if quiet and not CONFIG.get("verbose_logging") :
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
		if config.get("verbose_logging"):
			apt_cmds = [ "apt-get update" , ["apt-get", "install", "-y"] ]
		else:
			apt_cmds = [ "apt-get update -qq" , ["apt-get", "install", "-y", "-qq" ] ]
		for cmd in apt_cmds : 
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
	@raises an InvalidHashError after 5 hash mismatches
	"""
	if version.upper() == 'LATEST' :
		tarball = "strongswan.tar.gz"
		md5_hash_file = "strongswan.tar.gz.md5"
	else:
		tarball = "strongswan-{}.tar.gz".format(version)
		md5_hash_file = "strongswan-{}.tar.gz.md5".format(version)

	for i in range(5):
		try:
			hookenv.log("Retrieving {}{}".format(DL_BASE_URL, tarball), level=hookenv.INFO)
			urlopen_write( DL_BASE_URL + tarball, "/tmp/" + tarball )
			urlopen_write( DL_BASE_URL + md5_hash_file, "/tmp/" + md5_hash_file )
			check_hash("/tmp/" + md5_hash_file, "/tmp/" + tarball )
		except InvalidHashError:
			if i == 4:
				raise
		else:
			break

	return ( "/tmp/" + tarball )


def configure_install(base_dir):
	"""
	@params base_dir: the base directory where the strongswan tarball was unpacked to.
	@return None
	@description pulls the comma sperated list of config options from the config file 
	and changes to the strongswan src directory and configures the install. Two options are
	included by default because we will break a lot of other stuff if they are not. 
	TODO: certain packages have dependencies, sanity check?
	TODO: this also installs strongswan make make install etc.
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
	_check_call( 'cd {}; make'.format(base_dir), shell=True, fatal=True, timeout=300, quiet=True )
	_check_call( 'cd {}; make install'.format(base_dir), shell=True, fatal=True, timeout=300, quiet=True )
	_check_call(['cp', '../scripts/strongswan.conf', '/etc/init/strongswan.conf' ])


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
	@description Enables IP Forwarding Always:
	"""
	_dict = {}
	_dict[IPV4_FORWARD] = 1
	_dict[IPV6_FORWARD] = 1
	create( dumps(_dict) , SYSCTL_PATH )


def cp_sysctl_file():
	"""
	Copies the sysctl file for future reference
	"""
	_check_call(['cp', '/etc/sysctl.conf', '/etc/sysctl.conf.original'] )
	

def urlopen_write( url, path ):
	"""
	@params url: the url to retrieve
			path: the file path to write the object to
	@return None
	@exeption URLError is raised if we can't get the url after 5 tries
	"""
	retry_count = 0
	retry_max = 5
	retry_wait = 5
	while retry_count < retry_max :
		try:
			req = urlopen(url)
			with open( path, "bw" ) as fd:
				fd.write( req.read() )
		except URLError:
			retry_count += 1
			sleep(retry_wait)
		else:
			break
	if retry_count == retry_max:
		raise URLError("Unable to retrieve " + url )


def check_hash(hash_file_path, tar_file_path):
	"""
	@params tar_file_path is the path of the tarball
			hash_file_path is the path of the hash file
	@description check the hash of the downloaded tarball
	@exception Raise InvalidHashError if the hash of the tarball
	does not match the published md5 hash.
	"""
	with open( hash_file_path, 'rb' ) as fd:
		original_hash = fd.read().split()[0].decode('utf-8')
	with open( tar_file_path, 'rb' ) as fd:
		tar_hash = md5( fd.read() ).hexdigest()
	if original_hash != tar_hash :
		raise InvalidHashError("Hash did not match")
