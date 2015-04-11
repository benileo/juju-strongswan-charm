#!/usr/bin/env python3

# GLOBAL VARS #

import subprocess as sp

from charmhelpers.core import hookenv

# Make sure the curl command is available
try:
	sp.call(['curl'], stderr=sp.DEVNULL )
except FileNotFoundError :
	sp.check_output( ["apt-get", "install", "-y" , "-qq" , "curl" ] )
	hookenv.log("INFO:\tInstalling curl command")


# IP TABLES 
ACCEPT = "ACCEPT"
DROP = "DROP"
INPUT = "INPUT"
OUTPUT = "OUTPUT"
FORWARD = "FORWARD"
NAT_TABLE = "nat"
IPTABLES = "iptables"
IPTABLES_SAVE = "iptables-save"
UDP = 'udp'
TCP = 'tcp'
ESP = "50"
AH = "51"
IKE = "500"
NAT_T = "4500"
SSH = '22'
INSERT = '-I'
APPEND = '-A'
DELETE = '-D'



# SYSTEM CONTROL
IPV4_FORWARD = "net.ipv4.ip_forward"
IPV6_FORWARD = "net.ipv6.conf.all.forwarding"
SYSCTL_PATH = "/etc/sysctl.conf"




# OPEN SSL 
OPENSSL = 'openssl'
REQ = 'req'
CA = 'ca'




# wrapper to check_output
def _check_output( cmd , fatal=False, message=None ):
	try:
		return ( sp.check_output( cmd ) )
	except sp.CalledProcessError as err:
		hookenv.log("ERROR:\t{}\n\tReturn Code: {}\n\tOutput: {}\n\t Command: {}\n\t".format(
			message,
			err.returncode,
			err.output,
			err.cmd 
			)
		)
		if fatal:
			raise