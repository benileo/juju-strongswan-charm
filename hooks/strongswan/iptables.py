#!/usr/bin/env python3
"""
IP Tables
"""
from charmhelpers.core import (
	hookenv
)
from strongswan import * 


# update the rule chains and then save the rules
def configure_iptables():
	_filter()
	_nat()
	_check_output([IPTABLES_SAVE], 
			message="iptables-save has failed in non-fatal mode")



# update filter chain
def _filter():

	# we are creating a SG, lets make it secure....
	# set default policy to DROP for filter tables.
	_check_output( [IPTABLES, POLICY, FORWARD , DROP ] )
	_check_output( [IPTABLES, POLICY, INPUT , DROP ] )
	_check_output( [IPTABLES, POLICY, OUTPUT , DROP ] )

	# allow IKE and NAT-T Inbound and Outbound
	make_rule(ALLOW_IKE, INPUT, INSERT)
	make_rule(ALLOW_IKE, OUTPUT, INSERT )
	make_rule(ALLOW_NAT_T, INPUT, INSERT)
	make_rule(ALLOW_NAT_T, OUTPUT, INSERT)

	# allow either AH or ESP inbound and outbound
	if CHARM_CONFIG.get("ipsec_protocol") == "esp":
		make_rule(ALLOW_ESP, INPUT, INSERT)
		make_rule(ALLOW_AH , INPUT, DELETE )
		make_rule(ALLOW_ESP, OUTPUT, INSERT)
		make_rule(ALLOW_AH , OUTPUT, DELETE )
	else:
		make_rule(ALLOW_AH, INPUT, INSERT )
		make_rule(ALLOW_ESP, INPUT, DELETE )
		make_rule(ALLOW_AH, OUTPUT, INSERT )
		make_rule(ALLOW_ESP, OUTPUT, DELETE )


	# allow ssh inbound and outbound 
	if CHARM_CONFIG.get("allow_ssh"):
		make_rule(ALLOW_SSH, INPUT, APPEND)
		make_rule(ALLOW_SSH, OUTPUT, APPEND)
	else:
		make_rule(ALLOW_SSH, INPUT, DELETE )
		make_rule(ALLOW_SSH, OUTPUT, DELETE )

	
	# all DHCP and DNS
	make_rule(ALLOW_DNS, INPUT, APPEND)
	make_rule(ALLOW_DNS, OUTPUT, APPEND)
	make_rule(ALLOW_DHCP, INPUT, APPEND)
	make_rule(ALLOW_DHCP, OUTPUT, APPEND)

	
	# can we access the rest of the internet?
	if CHARM_CONFIG.get("public_network_enabled") :
		make_rule( ALLOW_EST_CONNS, APPEND )
	else:
		# apt
		pass












def _nat():
	pass
