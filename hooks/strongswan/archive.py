#!/usr/bin/env python3
"""
File containing wrapper and helpers functions
"""

import subprocess as sp

from charmhelpers.core import(
	hookenv
)
from strongswan.hosts import(
	update_hosts_file,
	flush_hosts_file,
	get_archive_ip_addrs
)
from time import (
	sleep
)
from strongswan import (
	PYOPENSSL_DEPENDENCIES,
	CHARM_CONFIG,
	_check_output
)

def install_pyOpenSSL():
	cmd = ["apt-get" , "install", "-y", "-qq"]
	cmd.extend(CHARM_DEPENDENCIES)
	run_apt_command(cmd, 60)
	_check_output( ["pip3", "install" , "pyOpenSSL" ] , fatal=True, 
		message="Installing pyOpenSSL into Python 3 installation" )

def strongswan_pkgs():
	return ["strongswan"]


# installs the strongswan packages from the archives.
def install_strongswan():
	hookenv.log("Attempting to install Strongswan from the archives" , level=hookenv.INFO )
	run_apt_command( ["apt-get" , "update", "-qq"] , 30 )
	cmd = ["apt-get" , "install", "-y", "-qq"]
	cmd.extend( strongswan_pkgs() )
	run_apt_command( cmd, 60 )
	flush_hosts_file()
	



# runs apt-get command handles dpkg locks and archive server unavailability
def run_apt_command(cmd, timeout_interval ):
	hookenv.log("Calling {0}".format(cmd) , level=hookenv.INFO )

	apt_retry_count = 0
	apt_retry_max = 0
	apt_retry_wait = 10
	dpkg_lock_error = 100
	timed_out = False
	result = None

	while result is None or result == dpkg_lock_error :
		try:
			result = sp.check_call( cmd, timeout=timeout_interval )

		except sp.CalledProcessError as e:
			apt_retry_count += 1
			if apt_retry_count > apt_retry_max : 
				raise
			result = e.returncode
			hookenv.log("Couldn't aquire DPKG lock trying again in {0}".format(apt_retry_wait) , level=hookenv.INFO )
			sleep(apt_retry_wait)

		except sp.TimeoutExpired:
			hookenv.log("{0} command has timed out.".format(cmd), level=hookenv.INFO )
			if not timed_out :
				timed_out = True
				dns_entries = get_archive_ip_addrs()
				if not dns_entries:
					hookenv.log('Do we have a DNS issue? Can\'t Resolve archive.ubuntu.com.', level=hookenv.ERROR )
					raise # TODO create your own exception class.
			if not dns_entries:
				hookenv.log('Unable to contact an archive server.', level=hookenv.ERROR )
				raise #TODO create your own exception class
			else:
				_ip = dns_entries.pop()
				update_hosts_file( _ip , "archive.ubuntu.com" )
				update_hosts_file( _ip , "security.ubuntu.com" )

	hookenv.log("{0} has completed. ".format(cmd) , level=hookenv.INFO )

