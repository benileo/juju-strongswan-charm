#!/usr/bin/env python3
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
	IPTABLES_SAVE,
	_check_output
)
from charmhelpers.core import (
	hookenv
)


config = hookenv.config()


def iptables():
	_filter()
	_nat()
	_check_output([IPTABLES_SAVE], message="iptables-save has failed in non-fatal mode")



def _filter():

	# allow IKE no questions asked.
	make_rule( [INPUT, '-p', UDP , '--dport' , IKE , '--sport', IKE, '-j', ACCEPT ], INSERT )
	# NAT-T doesn't ALWAYS originate on port 4500
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
