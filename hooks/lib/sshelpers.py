#!/usr/bin/env python3
"""
File containing wrapper and helpers functions
"""

import os
import subprocess as sp

from charmhelper.core import hookenv

IPV4_FORWARD = "net.ipv4.ip_forward"
IPV6_FORWARD = "net.ipv6.conf.all.forwarding"

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

	hookenv.log("Opening /etc/sysctl.conf")
	if os.path.exists( '/etc/sysctl.conf' ) : 
		sysctl_file = open( '/etc/sysctl.conf', 'r+' ) # need read and write
	else:
		hookenv.log(' unable to find the sysctl file')

	# load all current sys ctl values
	hookenv.log("Parsing sysctl.conf....")
	sysctl_dict = dict_from_sysctl_file(sysctl_file)

	# sync dictionairy to config.yaml
	if config.get("ip_forward") :
		sysctl_dict[IPV4_FORWARD] = "1"
	else:
		if sysctl_dict.get(IPV4_FORWARD):
			del(sysctl_dict[IPV4_FORWARD])
			





	if config.get("ip6_forward") :
		pass

	# open a new file for writing
	# write the new values to the file
	# restart sys control 



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

def ss_iptables():
	pass
