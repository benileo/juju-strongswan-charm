#!/usr/bin/env python3
"""
IP Tables
"""

import subprocess as sp

from strongswan import (
	INSERT,
	APPEND,
	DELETE,
	IPTABLES,
	IPTABLES_SAVE,
	ALLOW_IKE,
	ALLOW_ESP,
	ALLOW_SSH,
	ALLOW_NAT_T,
	ALLOW_AH,
	ALLOW_EST_CONN,
	CHARM_CONFIG,
	_check_output,
	make_rule,
	rule_exists
)
from charmhelpers.core import (
	hookenv
)

# update the rule chains and then save the rules
def configure_iptables():
	_filter()
	_nat()
	_check_output([IPTABLES_SAVE], message="iptables-save has failed in non-fatal mode")



# update filter chain
def _filter():

	# allow IKE and NAT-T
	if not rule_exists( ALLOW_IKE ) :
		make_rule(ALLOW_IKE, INSERT)
	if not rule_exists( ALLOW_NAT_T ):
		make_rule( ALLOW_NAT_T, INSERT)

	# allow either AH or ESP
	if CHARM_CONFIG.get("ipsec_protocol") == "esp":
		if not rule_exists( ALLOW_ESP ):
			make_rule(ALLOW_ESP, INSERT)
		if rule_exists( ALLOW_AH ):
			make_rule( ALLOW_AH , DELETE )
	else:
		if not rule_exists( ALLOW_AH ) : 
			make_rule(ALLOW_AH, INSERT )
		if rule_exists( ALLOW_ESP ) :
			make_rule( ALLOW_ESP, DELETE )

	# allow ssh
	if CHARM_CONFIG.get("allow_ssh"):
		if not rule_exists( ALLOW_SSH )
			make_rule(ALLOW_SSH, APPEND)
	else:
		if rule_exists( ALLOW_SSH ) :
			make_rule( ALLOW_SSH, DELETE )


	# allow established connection back in, non-ipsec.
	# this is only necessary in 2 cases
	# 1. we are not a site to site VPN, in this case, 0.0.0.0/0
	# should not be allowed
	# 2. we are forwarding traffic (after IPsec headers are removed)
	# to the public internet. 
	if CHARM_CONFIG.get("public_network_enabled"):
		make_rule(ALLOW_EST_CONN, INSERT)


	
	return 

def _nat():
	pass
