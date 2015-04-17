#!/usr/bin/env python3

# GLOBAL VARS #

import subprocess as sp

from charmhelpers.core import (	
	hookenv
)

# charm config constants
CHARM_CONFIG = hookenv.config()
AUTH = CHARM_CONFIG.get("authentication_method")
SOURCE = CHARM_CONFIG.get("source")



PYOPENSSL_DEPENDENCIES = [
	"build-essential",
	"libssl-dev",
	"libffi-dev",
	"python-dev",
	"python3-pip"
]



# IP TABLES 
ACCEPT 			= 	"ACCEPT"
DROP 			= 	"DROP"
INPUT 			= 	"INPUT"
OUTPUT 			= 	"OUTPUT"
FORWARD 		= 	"FORWARD"
NAT_TABLE 		= 	"nat"
IPTABLES 		= 	"iptables"
IPTABLES_SAVE 	= 	"iptables-save"
UDP 			= 	'udp'
TCP 			= 	'tcp'
ESP 			= 	"50"
AH 				= 	"51"
IKE 			= 	"500"
NAT_T 			= 	'4500'
SSH 			= 	'22'
DNS 			= 	'53'
DHCP 			= 	'67:68'
INSERT 			= 	'-I'
APPEND 			= 	'-A'	
DELETE 			= 	'-D'
CHECK 			= 	'-C'
ALLOW_IKE 		= 	[INPUT, '-p', UDP , '--dport' , IKE , '-j', ACCEPT ]
ALLOW_NAT_T 	= 	[INPUT, '-p', UDP, '--dport', NAT_T , '-j', ACCEPT ]
ALLOW_SSH 		= 	[INPUT, '-p',  TCP, '--dport', SSH, '-j' ACCEPT]
ALLOW_AH 		=  	[INPUT, '-p', AH, '-j', ACCEPT ]
ALLOW_ESP 		= 	[INPUT, '-p', ESP, '-j', ACCEPT ]
ALLOW_EST_CONN 	= 	[INPUT, '-m', 'conntrack', '--ctstate', 'ESTABLISHED', '-j', ACCEPT ]
ALLOW_DNS 		=	[INPUT, '-p', UDP, '--dport', DNS, '--sport', DNS, '-j', ACCEPT ]
ALLOW_DHCP 		=	[INPUT, '-p', UDP, '--dport', DHCP,'--sport', DHCP, '-j', ACCEPT ]


# SYSTEM CONTROL
IPV4_FORWARD 	= 	"net.ipv4.ip_forward"
IPV6_FORWARD 	= 	"net.ipv6.conf.all.forwarding"
SYSCTL_PATH 	= 	"/etc/sysctl.conf"



# Strongswan directory structure
IPSEC_D_PRIVATE 	= '/etc/ipsec.d/private/'
IPSEC_D_CACERTS 	= '/etc/ipsec.d/cacerts/'
IPSEC_D_CERTS 		= '/etc/ipsec.d/certs/'
IPSEC_D_CRLS		= '/etc/ipsec.d/crls/'
IPSEC_D_REQS 		= '/etc/ipsec.d/reqs/'
CA_KEY				= 'caKey.pem'
CA_CERT				= 'caCert.pem'




# wrapper to check_output
def _check_output( cmd , fatal=False, message=None ):
	hookenv.log("Calling {0}".format(cmd) , level=hookenv.INFO )
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
	hookenv.log("{0} has completed. ".format(cmd) , level=hookenv.INFO )

# if the rule does not already exist, make the rule.
def make_rule(cmd, rule_type):
	try:
		cmd.insert( 0, CHECK )
		cmd.insert( 0, IPTABLES )
		sp.check_call( rule, stdout=sp.DEVNULL, stderr=sp.DEVNULL )
	except sp.CalledProcessError:
		if rule_type != DELETE :
			cmd[1] = rule_type
			_check_output(rule, fatal=False, message="Creating IPTables rule")
	else:
		if rule_type == DELETE :
			cmd[1] = DELETE
			_check_output(rule, fatal=False, message="Deleting IPTables rule")
