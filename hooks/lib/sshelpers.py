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
		buf = []
		for ch in line:
			if ch is '#' or ch is '\n':
				if len(buf) == 0 : 
					break
				else:
					pass
					#this line contains a config item:
			elif ch is ' ':
				pass
			else:
				buf.append(ch)
		
	#parse out values in the existing config file.
	#check to see if the rule for ip_forwarding exists
	#if it does not exist then write the rule to the file
	#reload the file
	#either way open this file. 



def ss_iptables():
	pass
