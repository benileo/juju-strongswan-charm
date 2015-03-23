#!/usr/bin/env python3
"""
File containing wrapper and helpers functions
"""

import os
import subprocess as sp

from charmhelper.core import hookenv

# Global Variable Declaration
IPV4_FORWARD = "net.ipv4.ip_forward"
SYSCTL_FILE_PATH = "/etc/sysctl.conf"



def ss_iptables():
	pass




# returns the essential strongswan packages 
# other packages are added based on initial launch options
# other features can added be added later
# depending on how you want to set up strongswan this can differ
def ss_apt_pkgs( config ):
	avail_pkgs = ss_apt_cache()

	if len(avail_pkgs) > 0 :
		hookenv.log('Strongswan Packages:')
		for pkg in avail_pkgs:
			hookenv.log(pkg)
	else:
		hookenv.log('No packages........Something is up....Not throwing exception though')

	# just return 1 package: strongswan.. for now... 
	return [ "strongswan" ]



# this needs to be broken down
# comments denote the start of a new function
# let the code write itself
def ss_sysctl( config ):

	hookenv.log("/etc/sysctl.conf whats up")
	if os.path.exists(SYSCTL_FILE_PATH) : 
		sysctl_file = open(SYSCTL_FILE_PATH, 'r' )
	else:
		hookenv.log('Error: Unable to find the sysctl file')
		Exception('Error: Unable to find the sysctl file')

	# load all current sys ctl values
	hookenv.log("Parsing sysctl.conf....")
	sysctl_dict = dict_from_sysctl_file(sysctl_file)

	# sync dictionairy to config.yaml
	hookenv.log("Updating ip_forward to match up to charm config.yaml file")
	if config.get("ip_forward") :
		sysctl_dict[IPV4_FORWARD] = "1"
	else:
		if sysctl_dict.get(IPV4_FORWARD):
			del(sysctl_dict[IPV4_FORWARD])

	# close for reading and open file for writing
	sysctl_file.close()
	sysctl_file = open(SYSCTL_FILE_PATH, "w")
	for key in sysctl_dict:
		s = key + '=' + sysctl[key] + '\n'
		hookenv.log(s)
		sysctl_file.write(s)
	sysctl_file.close()

	# restart sys control
	cmd = ["sysctl", "-p", SYSCTL_FILE_PATH ]
	r_val = sp.check_call(cmd)
	if r_val != 0:
		hookenv.log('Error: command to reload sysctl file has failed for unknown reasons')
		raise Exception('Error: command to reload sysctl file has failed for unknown reasons')

	return




# Parses a sys ctl file and returns a dictioniary of all values
def dict_from_sysctl_file( sysctl_file ):

	_dict = {}

	for line in sysctl_file.readlines:
		buf = ""

		for ch in line:
			if ch == '\n' or  ch == '#':
				break
			elif ch != ' ':
				buf += ch

		if len(buf) > 0 :
			key_val = buf.split('=')
			if key_val == 2 :
				_dict[key_val[0]] = key_val[1]
			else:
				hookenv("Error: Config error in sysctl.conf. Fatal.")
				Exception("Error: Config error in sysctl.conf")

	return _dict



def ss_apt_cache():
	avail_pkgs = []

	cmd = ["apt-cache", "search", "strongswan"]
	try:
		handler = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE )
		data = handler.communicate()[0].decode('utf-8') 
	except (OSError, sp.TimeoutExpired, ValueError) as error : 
		hookenv.log(error)

	for s in ( data.split('\n') ):
		t = s.split(' ')
		avail_pkgs.append(t[0])

	return avail_pkgs
