#!/usr/bin/env python
"""
IP Tables
"""

import subprocess as sp

from strongswan import (
	IKE,
	INPUT,
	ACCEPT,
	INSERT,
	UDP,
	ESP,
	AH,
	IPTABLES,
	NAT_T,
	IPTABLES_SAVE
)
from charmhelpers.core import (
	hookenv
)


config = hookenv.config()


def iptables():
	_filter()
	_nat()
	sp.check_call([IPTABLES_SAVE])
	return


def _filter():

	# allow NAT-T and IKE no questions asked.
	make_rule( [INPUT, '-p', UDP , '--dport' , IKE , '--sport', IKE, '-j', ACCEPT ], INSERT )
	make_rule( [INPUT, '-p', UDP, '--dport', NAT_T , '-j', ACCEPT ] , INSERT)

	# allow either AH or ESP
	if config.get("ipsec_protocol") == "esp":
		make_rule( [INPUT, '-p', ESP, '-j', ACCEPT ] , INSERT)
	else:
		make_rule( [INPUT, '-p', AH, '-j', ACCEPT ] , INSERT )
		
	return 

def _nat():
	pass



# if the rule does not already exist, make the rule.
def make_rule(rule, rule_type):
	try:
		rule.insert(0, "-C")
		rule.insert(0, IPTABLES)
		rval = sp.check_call( rule, stdout=sp.DEVNULL, stderr=sp.DEVNULL )
	except sp.CalledProcessError:
		rule[1] = rule_type
		sp.call(rule)
	return