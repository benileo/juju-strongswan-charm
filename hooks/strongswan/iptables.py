#!/usr/bin/env python3
"""
IP Tables
"""

import subprocess as sp

from strongswan import (
	INSERT,
	APPEND,
	DELETE,
	IPTABLES_SAVE,
	ALLOW_IKE,
	ALLOW_ESP,
	ALLOW_SSH,
	ALLOW_NAT_T,
	ALLOW_AH,
	ALLOW_EST_CONN,
	ALLOW_DNS,
	ALLOW_DHCP,
	CHARM_CONFIG,
	_check_output,
	make_rule,
)
from charmhelpers.core import (
	hookenv
)

# update the rule chains and then save the rules
def configure_iptables():
	_filter()
	_nat()
	_check_output([IPTABLES_SAVE], 
			message="iptables-save has failed in non-fatal mode")



# update filter chain
def _filter():

	# TODO set default policy to DROP

	# allow IKE and NAT-T
	make_rule(ALLOW_IKE, INSERT)
	make_rule(ALLOW_NAT_T, INSERT)

	# allow either AH or ESP
	if CHARM_CONFIG.get("ipsec_protocol") == "esp":
		make_rule(ALLOW_ESP, INSERT)
		make_rule( ALLOW_AH , DELETE )
	else: 
		make_rule(ALLOW_AH, INSERT )
		make_rule( ALLOW_ESP, DELETE )

	# allow ssh
	if CHARM_CONFIG.get("allow_ssh"):
		make_rule(ALLOW_SSH, APPEND)
	else:
		make_rule(ALLOW_SSH, DELETE )

	
	# all DHCP and DNS allowed
	# from where ....!!?? 
	make_rule(ALLOW_DNS, APPEND)
	make_rule(ALLOW_DHCP, APPEND)

	
	# here it gets a little more complicated
	
	# case 1: ALLOW ACCESS to 0.0.0.0/0
	# anything initiated outbound will be allowed back in 
	if CHARM_CONFIG.get("public_network_enabled"):
		make_rule(ALLOW_EST_CONN)
	else:




	make_rule(ALLOW_EST_CONN, INSERT)
	return 

def _nat():
	pass
