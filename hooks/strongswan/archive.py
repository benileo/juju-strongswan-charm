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
	flush_hosts_file
)
from time import (
	sleep
)
from strongswan import (
	CHARM_DEPENDENCIES
)



config = hookenv.config()


HOSTS_FILE_MOD_FLAG = False

# installs the strongswan packages from the archives.
def install_pkgs():

	# call apt-get update
	run_apt_command( ["apt-get" , "update", "-qq"] , 30 )

	# get the available packages from apt-cache
	# avail_pkgs = _apt_cache()

	_pkgs = ["strongswan"]
	cmd = ["apt-get" , "install", "-y", "-qq"]
	cmd.extend(_pkgs)
	cmd.extend(CHARM_DEPENDENCIES)

	run_apt_command( cmd, 60 )

	hookenv.log("Installing: {0}".format(_pkgs) , level=hookenv.INFO )
	
	# if the hosts file is modifed we should flush these entries
	if HOSTS_FILE_MOD_FLAG:
		flush_hosts_file()

	# install the openssl library for python 3
	sp.check_output( ["pip3", "install" , "pyOpenSSL" ] )

# returns the available strongswan packages from the cache.
def _apt_cache():
	avail_pkgs = []
	cmd = ["apt-cache", "search", "strongswan"]
	data = sp.check_output(cmd)
	data = data.decode('utf-8')
	for s in ( data.split('\n') ):
		t = s.split(' ')
		avail_pkgs.append(t[0])
	return avail_pkgs

# call apt-get command
# if we have a problem with the network or contacting the 
# archive servers we will see it here first
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
					raise
			if not dns_entries:
				hookenv.log('Unable to contact an archive server.', level=hookenv.ERROR )
				raise
			else:
				_ip = dns_entries.pop()
				update_hosts_file( _ip , "archive.ubuntu.com" )
				update_hosts_file( _ip , "security.ubuntu.com" )
				if not HOSTS_FILE_MOD_FLAG:
					HOSTS_FILE_MOD_FLAG = True

	hookenv.log("{0} has completed. ".format(cmd) , level=hookenv.INFO )

# returns a list with the result of dig archive.ubuntu.com			
def get_archive_ip_addrs():
	hookenv.log("Running dig command to obtain archive IP addresses", level=hookenv.INFO )
	ip_list = []
	dig = sp.check_output(['dig', 'archive.ubuntu.com'])
	dig = dig.decode('utf-8').split('\n')
	for i in dig:
		i = i.split('\t')
		if i:
			if i[0] == 'archive.ubuntu.com.' :
				ip_list.append(i[4])
	return ip_list