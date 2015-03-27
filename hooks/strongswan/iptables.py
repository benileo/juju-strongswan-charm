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
ESP = "50"
AH = "51"


class IPtables():
	def __init__(self):
		pass

	def filter_rules( self ):
		if not ( rule_exists([IPTABLES, "-C", INPUT, '-p', ESP, '-j', ACCEPT) ) :
			make_rule( [IPTABLES, "A", INPUT, '-p', ESP, '-j', ACCEPT ] )
		if not ( rule_exists([IPTABLES, "-C", OUTPUT, '-p', ESP, '-j', ACCEPT ]) ) : 
			make_rule( [IPTABLES, "A", OUTPUT, '-p', ESP, '-j', ACCEPT]) 



	def rule_exists(self, rule):
		try:
			rval = sp.check_call(rule)
		except sp.CalledProcessError:
			return False
		if rval == 0: 
			return True











# # this needs to be called again and again
# def iptables():
# 	# load in the current config 
# 	# make the logical decisions needed to setting U
# 	cmd = [ "iptables" ]
# 	tbls = ["nat", "filter", "mangle", "raw", "security"]
# 	pass




# load table rules into a data structure

# What rules are needed for the linux host to talk
# inbound 500 and 4500 of course udp 
# 

# iptables -A INPUT  -p udp --sport 500 --dport 500 -j ACCEPT
# iptables -A OUTPUT -p udp --sport 500 --dport 500 -j ACCEPT
# # ESP encrypton and authentication
# iptables -A INPUT  -p 50 -j ACCEPT
# iptables -A OUTPUT -p 50 -j ACCEPT
# uncomment for AH authentication header
# iptables -A INPUT  -p 51 -j ACCEPT
# iptables -A OUTPUT -p 51 -j ACCEPT
# if the setup is site to site, then, right 