#!/usr/bin/env python3
"""
IP Tables
"""

import subprocess as sp

from strongswan import (
	INSERT,
	IPTABLES,
	IPTABLES_SAVE,
	ALLOW_IKE,
	ALLOW_ESP,
	ALLOW_SSH,
	ALLOW_NAT_T,
	ALLOW_AH,
	ALLOW_EST_CONN,
	_check_output,
	CHARM_CONFIG
)
from charmhelpers.core import (
	hookenv
)

# update the rule chains and then save the rules
def configure_iptables():
	_filter()
	_nat()
	_check_output([IPTABLES_SAVE], message="iptables-save has failed in non-fatal mode")



# update filter
def _filter():

	# allow IKE and NAT-T 
	make_rule(ALLOW_IKE, INSERT)
	make_rule(ALLOW_NAT_T, INSERT) 

	# allow either AH or ESP
	if CHARM_CONFIG.get("ipsec_protocol") == "esp":
		make_rule(ALLOW_ESP, INSERT)
	else:
		make_rule(ALLOW_AH, INSERT)

	# allow ssh
	if CHARM_CONFIG.get("allow_ssh"):
		make_rule(ALLOW_SSH, INSERT)

	# allow established connection back in, non-ipsec.
	if CHARM_CONFIG.get("public_network_enabled"):
		make_rule(ALLOW_EST_CONN, INSERT)

		
	
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
