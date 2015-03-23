#!/usr/bin/env python3
"""
File containing wrapper and helpers functions
"""

import os
import subprocess as sp

from charmhelper.core import hookenv

# returns the essential strongswan packages 
# other packages are added based on initial launch options
# other features can added be added later
# depending on how you want to set up strongswan this can differ
def ss_apt_pkgs( config ):

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

	if len(avail_pkgs) > 0 :
		hookenv.log('Strongswan Packages:')
		for pkg in avail_pkgs:
			hookenv.log(pkg)

	# just return 1 package: strongswan.. for now... 
	return [ "strongswan" ]




def ss_sysctl( config ):

	if os.path.exists( '/etc/sysctl.conf' ) : 
		sysctl_file = open( '/etc/sysctl.conf', 'r+' ) # need read and write
	else:
		hookenv.log(' unable to find the sysctl file')

	# parse the current values of the sysctl file into a dictionairy
	# start with a list of lines with config items
	for line in sysctl_file.readlines():
		buf = ""
		for ch in line:
			if ch is '#' or ch is '\n':
				break
			elif ch is ' ':
				pass
			else:
				buf += ch
		if len(buf) > 0 :
			two_values = buf.split('=')
			if len(two_values) != 2 :
				hookenv.log("There is an error in sysctl.conf. That is not good. Raising Exception")
				raise Exception("ERROR: sysctl.conf file has a configuration error, this is fatal")
			else:



	#parse out values in the existing config file.
	#check to see if the rule for ip_forwarding exists
	#if it does not exist then write the rule to the file
	#reload the file
	#either way open this file. 

def dict_from_sysctl_conf( sysctl_file ):

	_dict = {}

	for line in sysctl_file.readlines:
		buf = ""

		for ch in line:
			if ch == '\n' or  ch == '#':
				break
			elif ch != ' ':
				buf += ch

		if len(buf) > 0:
			key_val = buf.split('=')
			if key_val == 2:
				_dict[key_val[0]] = key_val[1]
			else:
				hookenv("Error: Config error in sysctl.conf. Fatal.")
				Exception("Error: Config error in sysctl.conf")

	return _dict

def ss_iptables():
	pass
