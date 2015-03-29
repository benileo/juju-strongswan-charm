#!/usr/bin/env python
"""
IP Tables
"""

import subprocess as sp


ACCEPT = "ACCEPT"
DROP = "DROP"
INPUT = "INPUT"
OUTPUT = "OUTPUT"
FORWARD = "FORWARD"
MANGLE_TABLE = "mangle"
NAT_TABLE = "nat"
IPTABLES = "iptables"
UDP = 'udp'
TCP = 'tcp'
ESP = "50"
AH = "51"
IKE = "500"
NAT_T = "4500"
SSH = '22'


class IPtables():
	def __init__(self, config):
		self.config = config

	def filter( self ):

		# Allow IKE and NAT-T
		make_rule( [INPUT, '-p', UDP , '--dport' , IKE , '--sport', IKE, '-j', ACCEPT ])
		make_rule( [INPUT, '-p', UDP, '--dport', NAT_T , '--sport', NAT_T, '-j', ACCEPT ] )

		if self.config.get("ipsec_protocol") == "esp" :
			make_rule( [INPUT, '-p', ESP, '-j', ACCEPT ] )
		else:
			make_rule( [INPUT, '-p', AH, '-j', ACCEPT ] )

		sp.check_output( [IPTABLES, '-I', INPUT, '-p', 'tcp', '--dport',  SSH , '-j', ACCEPT ] )
		# Nothing else gets through
		sp.check_output( [IPTABLES, '-I', INPUT, '-m', 'conntrack', '--ctstate', 'ESTABLISHED', '-j', ACCEPT ] )
		sp.check_output( [IPTABLES, '-A', INPUT, '-j', DROP ] )

		return 


	def nat(self):
		pass

	def mangle(self):
		pass

	def security(self):
		pass

	def raw(self):
		pass


# if the rule does not already exist, make the rule.
def make_rule(rule):
	try:
		rule.insert(0, "-C")
		rule.insert(0, IPTABLES)
		rval = sp.check_call(rule)
	except sp.CalledProcessError:
		rule[1] = "-I"
		sp.check_output(rule)
	return
 
def iptables_configure( config ):
	iptables = IPtables( config )
	iptables.filter()
	iptables.nat()
	iptables.mangle()
	iptables.raw()
	iptables.security()
	return