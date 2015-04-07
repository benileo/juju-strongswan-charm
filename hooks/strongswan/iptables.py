#!/usr/bin/env python
"""
IP Tables
"""

import subprocess as sp
from charmhelpers.core import hookenv


config = hookenv.config()


def iptables():
	_filter()
	_nat()


def _filter():

	# allow NAT-T and IKE no questions asked.
	make_rule( [INPUT, '-p', UDP , '--dport' , IKE , '--sport', IKE, '-j', ACCEPT ])
	make_rule( [INPUT, '-p', UDP, '--dport', NAT_T , '--sport', NAT_T, '-j', ACCEPT ] )

	# allow either AH or ESP
	if config.get("ipsec_protocol") == "esp":
		make_rule( [INPUT, '-p', ESP, '-j', ACCEPT ] )
	else:
		make_rule( [INPUT, '-p', AH, '-j', ACCEPT ] )

	# that's it for now....
	return 

def _nat():
	pass


# if the rule does not already exist, make the rule.
def make_rule(rule):
	try:
		rule.insert(0, "-C")
		rule.insert(0, IPTABLES)
		rval = sp.check_call( rule, stdout=sp.DEVNULL, stderr=sp.DEVNULL )
	except sp.CalledProcessError:
		rule[1] = "-I"
		sp.check_output(rule)
	return