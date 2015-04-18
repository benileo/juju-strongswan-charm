
from charmhelpers.core import hookenv
from time import sleep
from strongswan.hosts import update_hosts_file, flush_hosts_file, get_archive_ip_addrs
from strongswan.constants import PYOPENSSL_DEPENDENCIES
from strongswan.util import _check_call
from strongswan.errors import DnsError, NetworkError, AptLockError
from urllib.request import urlretrieve


# installs the strongswan packages from the archives.
def install_strongswan_archives():
	hookenv.log("Installing Strongswan from the archives" , level=hookenv.INFO )
	run_apt_command( ["apt-get" , "update", "-qq"] , 30 )
	cmd = ["apt-get" , "install", "-y", "-qq"]
	cmd.extend( strongswan_pkgs() )
	run_apt_command( cmd, 60 )


	
# installs strongswan from the most recent strongswan tarball
def install_strongswan_version( version ):
	pass


# install strongswan from github
def install_strongswan_github():
	pass

# runs apt-get command handles dpkg locks and archive server unavailability
# TODO, i believe apt-get returns if it can't contact a DNS server
# handle this error appropriately
def run_apt_command(cmd, timeout_interval ):

	apt_retry_count = 0
	apt_retry_max = 0
	apt_retry_wait = 10
	dpkg_lock_error = 100
	timed_out = False
	result = None

	while result is None or result == dpkg_lock_error :
		try:
			result = _check_call( cmd, timeout=timeout_interval, quiet=True, fatal=True )
		
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



# Installs the PyOpenssl Package into Python 3
def install_pyOpenSSL():
	hookenv.log("Installing PyOpenSSL Dependencies" , level=hookenv.INFO )
	run_apt_command( ["apt-get" , "update", "-qq"] , 30 )
	cmd = ["apt-get" , "install", "-y", "-qq"]
	cmd.extend(PYOPENSSL_DEPENDENCIES)
	run_apt_command(cmd, 300)
	_check_call( ["pip3", "install" , "pyOpenSSL"] , 
		fatal=True, 
		message="Installing pyOpenSSL into Python 3 installation", 
		quiet=True
	)
