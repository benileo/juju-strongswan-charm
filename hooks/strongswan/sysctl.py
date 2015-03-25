#!/usr/bin/env python3
"""
Code for strongswan sysctl 
"""

import os
import subprocess as sp
from charmhelpers.core import hookenv

IPV4_FORWARD = "net.ipv4.ip_forward"
IPV6_FORWARD = "net.ipv6.conf.all.forwarding"


# Everytime config changes you need to run this updating sys control accord.
def sysctl( config ):
	sysctl_fd = get_sysctl_fd('r') # get fd of sysctl file in read mode
	sysctl_dict = dict_from_sysctl_file(sysctl_fd) # parse sysctl into dict 
	update_sysctl_dict( config, sysctl_dict )
	create_sysctl_file( sysctl_dict )  
	restart_sysctl( '/etc/sysctl.conf' ) # restart sys control
	return


# TODO i think this parser will break when encountering values with white space.
# Parses a sys ctl file and returns a dictioniary of all values
def dict_from_sysctl_file( sysctl_file ):

	hookenv.log("Info: Parsing sysctl.conf ---------->")

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
				hookenv.log("Error: Config error in sysctl.conf. Fatal.")
				Exception("Error: Config error in sysctl.conf")

	sysctl_file.close()
	return _dict


def restart_sysctl( sctl_file_path ):
	cmd = ["sysctl", "-p", sctl_file_path ]
	r_val = sp.check_call(cmd)	
	if r_val != 0:
		hookenv.log('Error: command to reload sysctl file has failed for unknown reasons')
		raise Exception('Error: command to reload sysctl file has failed for unknown reasons')

def get_sysctl_fd( mode ):
	if os.path.exists('/etc/sysctl.conf') : 
		sysctl_file = open( '/etc/sysctl.conf' , mode )
	else:
		hookenv.log('Error: Unable to find the sysctl file')
		Exception('Error: Unable to find the sysctl.conf in default ubuntu path')
	return sysctl_file


def update_sysctl_dict( config , sysctl_dict ):
	
	if config.get("ip_forward") :
		sysctl_dict[IPV4_FORWARD] = "1"
	else:
		if sysctl_dict.get(IPV4_FORWARD):
			del(sysctl_dict[IPV4_FORWARD])

	if config.get("ip6_forward") :
		sysctl_dict[IPV6_FORWARD] = "1"
	else:
		if sysctl_dict.get(IPV6_FORWARD):
			del(sysctl_dict[IPV6_FORWARD])

	hookenv.log('Updated sysctl dictionary:')
	hookenv.log(sysctl_dict)	
	return


def create_sysctl_file( sysctl_dict ):
	sysctl_file = get_sysctl_fd('w')
	for key in sysctl_dict:
		s = key + '=' + sysctl_dict[key] + '\n'
		hookenv.log(s)
		sysctl_file.write(s)
	sysctl_file.close()
	return

def cp_sysctl_file():
	cmd = ['cp', '/etc/sysctl.conf', '/etc/syctl.conf.original']
	rval = sp.check_call(cmd)
	if rval != 0 : 
		hookenv.log("Failed to copy sysctl.conf file")
	else:
		hookenv.log("Original copy of sysctl file created: /etc/sysctl.conf.original")
	return




