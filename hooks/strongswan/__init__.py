#!/usr/bin/env python3

# GLOBAL VARS #

import subprocess as sp

from charmhelpers.core import (	
	hookenv
)

CHARM_DEPENDENCIES = [
	"build-essential",
	"libssl-dev",
	"libffi-dev",
	"python-dev",
	"python3-pip"
]

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

# Strongswan directory structure
IPSEC_D_PRIVATE 	= '/etc/ipsec.d/private/'
IPSEC_D_CACERTS 	= '/etc/ipsec.d/cacerts/'
IPSEC_D_CERTS 		= '/etc/ipsec.d/certs/'
IPSEC_D_CRLS		= '/etc/ipsec.d/crls/'
IPSEC_D_REQS 		= '/etc/ipsec.d/reqs/'




# wrapper to check_output
def _check_output( cmd , fatal=False, message=None ):
	try:
		return ( sp.check_output( cmd ) )
	except sp.CalledProcessError as err:
		hookenv.log("\n\tMessage: {}\n\tReturn Code: {}\n\tOutput: {}\n\tCommand:{}\n\t".format(
			message,
			err.returncode,
			err.output,
			err.cmd 
			), level=hookenv.ERROR
		)
		if fatal:
			raise