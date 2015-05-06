
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
	DPKG_LOCK_ERROR,
	PLUGIN_DEPENDENCIES
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
	A wrapper to subprocess.check_call and subprocess.check_output 
	
	:param cmd: A string or a list of cmd line arguments	
	:param fatal: do we raise an exception if one is thrown?
	:param message: the message to log to juju-log
	:param quiet: direct stdout and stderr to /dev/null
	:param timeout: timeout
	:param log: if an exception is thrown do we log to juju-log?
	:param shell: execute using the shell
	:param check_output: call check_output instead of check_call (we want output!)
	:param log_cmd: Log cmd argument to juju-log
	
	:raises CalledProcessError: only if fatal=true  
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

def apt_install( pkgs, apt_update=True ):
	"""
	Install a list of packages using apt-get

	:param pkgs: is a list of packages to install
	:param apt_update: run apt-get update first
	
	:raises AptError
	:raises NetworkError 
	"""
	verbose_install = ["apt-get", "install", "-y"]
	verbose_update = "apt-get update"
	quiet_install = ["apt-get", "install", "-y", "-qq" ]
	quiet_update = "apt-get update -qq"
	if isinstance( pkgs, list ):
		if CONFIG.get("verbose_logging"):
			apt_cmds = [verbose_update,verbose_install] if apt_update else [verbose_install]
		else:
			apt_cmds = [quiet_update, quiet_install] if apt_update else [quiet_install]
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
	_check_call(['cp', '/etc/hosts', '/etc/hosts.original' ]) 
	

def flush_hosts_file():
	"""
	Flush archive entries from /etc/hosts
	"""
	if  ( ( time() - getmtime('/etc/hosts') ) ) < 86400 :
		update_hosts_file( '#1.2.3.4', 'archive.ubuntu.com' )
		update_hosts_file( '#1.2.3.4', 'security.ubuntu.com' )


def update_hosts_file( ip_addr , hostname ):
	"""
	Adds an alias to /etc/hosts

	:params ip_addr: dotted quad IPv4 address
	hostname: is the alias for this IP 
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
	:return: IPv4 addresses of ubuntu archive servers
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
	Gets a Strongswan release in the form of .tar.gz
	:params version: the version of strongswan to fetch
	:return: path of .tar.gz 
	:raises InvalidHashError
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
	Configures and installs StrongSwan. A comma separated list of options is passed 
	from the charm config file. Registers Strongswan.conf in /etc/init.

	:params base_dir: the base directory where the strongswan tarball was unpacked to.
	
	"""
	cmd  = 'cd {}; '.format(base_dir)
	cmd += ' ./configure --prefix=/usr --sysconfdir=/etc'
	added_items = ["--prefix=/usr", "--sysconfdir=/etc"]
	for item in CONFIG.get("configuration").split(',') :
		if item:
			if item not in added_items:
				if item in PLUGIN_DEPENDENCIES:
					apt_install( PLUGIN_DEPENDENCIES.get(item), apt_update=False ) 
				cmd += ' {}'.format(item)
				added_items.append(item)
	_check_call(cmd, shell=True, fatal=True, quiet=True )
	_check_call( 'cd {}; make'.format(base_dir), 
		shell=True, fatal=True, timeout=300, quiet=True )
	_check_call( 'cd {}; make install'.format(base_dir), 
		shell=True, fatal=True, timeout=300, quiet=True )
	_check_call(['cp', '../templates/strongswan.conf', '/etc/init/strongswan.conf' ])


def convert_to_seconds( lifetime ) :
	"""
	:params lifetime: string 10y, 10d, 10h, 10m, or 10s
	:return # of seconds as int 
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
	Enables IP Forwarding Always:
	"""
	_dict = {}
	_dict[IPV4_FORWARD] = 1
	_dict[IPV6_FORWARD] = 1
	create( dumps(_dict) , SYSCTL_PATH )


def cp_sysctl_file():
	_check_call(['cp', '/etc/sysctl.conf', '/etc/sysctl.conf.original'] )
	

def urlopen_write( url, path ):
	"""
	Opens a URL and writes the result to specified directory

	:params 
	url: the url to retrieve
	path: the file path to write the object to
	
	:raises URLError
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
	Check md5 hash
	
	:params 
	tar_file_path: file path of the tarball
	hash_file_path: file path of the hash file
	
	:raises InvalidHashError
	
	"""
	with open( hash_file_path, 'rb' ) as fd:
		original_hash = fd.read().split()[0].decode('utf-8')
	with open( tar_file_path, 'rb' ) as fd:
		tar_hash = md5( fd.read() ).hexdigest()
	if original_hash != tar_hash :
		raise InvalidHashError("Hash did not match")
