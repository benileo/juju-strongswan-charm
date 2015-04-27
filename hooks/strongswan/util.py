
import subprocess as sp
import re
from time import time, sleep
from os.path import getmtime
from urllib.request import urlretrieve
from hashlib import md5
from charmhelpers.core import hookenv
from strongswan.constants import (
	CHECK, 
	IPTABLES, 
	DELETE, 
	DL_BASE_URL,
	CONFIG
)
from strongswan.errors import (
	DnsError, 
	NetworkError, 
	AptLockError, 
	InvalidHashError
)


# wrapper to check_call
def _check_call( cmd , fatal=False, 
	message=None, quiet=False, 
	timeout=60, log=True, shell=False,
	check_output=False, log_cmd=True
	):
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
	


# if the rule does not already exist, make the rule.
def make_rule(cmd, chain, rule_type):
	try:
		cmd = list(cmd)
		cmd.insert( 0, chain )
		cmd.insert( 0, CHECK )
		cmd.insert( 0, IPTABLES )
		_check_call(cmd, message="Checking IPtables rule", fatal=True, 
			log=False, quiet=True, log_cmd=False )
	except sp.CalledProcessError:
		if rule_type != DELETE :
			cmd[1] = rule_type
			_check_call(cmd, fatal=True, message="Creating IPTables rule", log_cmd=False)
	else:
		if rule_type == DELETE :
			cmd[1] = DELETE
			_check_call(cmd, fatal=True, message="Deleting IPTables rule", log_cmd=False)



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


# make copy of hosts file for reference
def cp_hosts_file():
	_check_call(['cp', '/etc/hosts', '/etc/hosts.original' ]) 
	

# If the host file has been modified in the past 24 hours
# Comment out entries for achive.ubuntu.com & security.ubuntu.com
def flush_hosts_file():
	hookenv.log("/etc/hosts last modifed: ".format(getmtime('/etc/hosts')) )
	hookenv.log("current time: ".format( time() ) )
	if  ( ( time() - getmtime('/etc/hosts') ) ) < 86400 :
		update_hosts_file( '#1.2.3.4', 'archive.ubuntu.com' )
		update_hosts_file( '#1.2.3.4', 'security.ubuntu.com' )



# add the alias to /etc/hosts if it does not exist already
def update_hosts_file( ip_addr , hostname ):
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


# returns a list of archive ip addresses 			
def get_archive_ip_addrs():
	hookenv.log("Running dig command to obtain archive IP addresses", level=hookenv.INFO )
	ip_list = []
	ip_addrs = _check_call(['dig', 'archive.ubuntu.com'], 
			check_output=True, fatal=True ).decode('utf-8').split('\n')
	for i in ip_addrs:
		i = i.split('\t')
		if i:
			if i[0] == 'archive.ubuntu.com.' :
				ip_list.append(i[4])
	return ip_list


# downloads the tarball and checks the hash
def get_tarball( version ):

		# build urls
	if version == 'latest' :
		tarball = "strongswan.tar.gz"
		md5_hash_file = "strongswan.tar.gz.md5"
	else:
		tarball = "strongswan-{}.tar.gz".format(version)
		md5_hash_file = "strongswan-{}.tar.gz.md5".format(version)

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

	cmd  = 'cd {}; '.format(base_dir)
	cmd += ' ./configure --prefix=/usr --sysconfdir=/etc'

	added_items = ["--prefix=/usr", "--sysconfdir=/etc"]

	# In particular EAP-RADIUS,, not sure exactly what will go here			
	# TODO depending on type of authentication we may have to append some extra
	# should we have a sanity check on what the valid config options are? or
	# trust that the sys admin knows what they are doing...!
	

	# add the items in the config if they are not already added.
	for item in CONFIG.get("config_options").split(',') :
		if item:
			if item not in added_items:
				cmd += ' {}'.format(item)
				added_items.append(item)

	_check_call(cmd, shell=True, fatal=True, quiet=True )



def convert_to_seconds( lifetime ) :
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
