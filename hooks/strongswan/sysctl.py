#!/usr/bin/env python3
"""
Code for strongswan sysctl 
"""

import os
import subprocess as sp
from charmhelpers.core import hookenv

config = hookenv.config()

# Everytime config changes you need to run this updating sys control accord.
def sysctl():
	sysctl_fd = get_sysctl_fd('r') # get fd of sysctl file in read mode
	sysctl_dict = dict_from_sysctl_file(sysctl_fd) # parse sysctl into dict 
	update_sysctl_dict(sysctl_dict )
	create_sysctl_file( sysctl_dict )  
	restart_sysctl( '/etc/sysctl.conf' ) # restart sys control
	return


# TODO : white space after the = sign
# Parses a sys ctl file and returns a dictioniary of all values
def dict_from_sysctl_file( sysctl_file ):
	hookenv.log("INFO:\tParsing /etc/sysctl.conf")

	_dict = {}

	for line in sysctl_file.readlines():
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
				Exception("ERROR:\tConfiguration error in /etc/sysctl.conf")

	sysctl_file.close()
	return _dict


def restart_sysctl( sctl_file_path ):
	cmd = ["sysctl", "-p", sctl_file_path ]
	r_val = sp.check_call(cmd)	
	if r_val != 0:
		raise Exception('ERROR:\tUnable to reload sysctl.conf file')

def get_sysctl_fd( mode ):
	if os.path.exists('/etc/sysctl.conf') : 
		sysctl_file = open( '/etc/sysctl.conf' , mode )
	else:
		Exception('ERROR:\tUnable to find the /etc/sysctl.conf in default ubuntu path')
	return sysctl_file


def update_sysctl_dict(sysctl_dict ):
	
	# Set IP 4 Forward
	if config.get("ip_forward") :
		sysctl_dict[IPV4_FORWARD] = "1"
	else:
		if sysctl_dict.get(IPV4_FORWARD):
			del(sysctl_dict[IPV4_FORWARD])

	# Set IP 6 Forward 
	if config.get("ip6_forward") :
		sysctl_dict[IPV6_FORWARD] = "1"
	else:
		if sysctl_dict.get(IPV6_FORWARD):
			del(sysctl_dict[IPV6_FORWARD])

	hookenv.log('INFO:\t Updated sysctl dictionary: {0}'.format(sysctl_dict))


# Create a sysctl.conf file from key,value pairs
def create_sysctl_file( sysctl_dict ):
	sysctl_file = get_sysctl_fd('w')
	for key in sysctl_dict:
		s = key + '=' + sysctl_dict[key] + '\n'
		hookenv.log(s)
		sysctl_file.write(s)
	sysctl_file.close()
	return

# Make copy of sysctl.conf and /etc/hosts for sys admin reference
def cp_sysctl_file():
	cmd = ['cp', '/etc/sysctl.conf', '/etc/sysctl.conf.original']
	sp.call(cmd)
	hookenv.log("INFO\tCopy of sysctl file created: /etc/sysctl.conf.original")
	