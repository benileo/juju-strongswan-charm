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
	ALLOW_DNS,
	ALLOW_DHCP,
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

	# allow dns and dhcp
	if not rule_exists( ALLOW_DNS ) : 
		make_rule( ALLOW_DNS , APPEND )
	if not rule_exists( ALLOW_DHCP ) : 
		make_rule( ALLOW_DHCP, APPEND )


	# PUBLIC + [ INTERNAL ]
	if CHARM_CONFIG.get("public_internet"):
		if not rule_exists( ALLOW_EST_CONN ) :
			make_rule( ALLOW_EST_CONN, APPEND )

	# INTERNAL ONLY #
	else:

		# NO VIRTUAL IP #
		if not CHARM_CONFIG.get("virtual_ip_enabled"):

			# ALLOW INBOUND TRAFFIC FROM INTERNAL SUBNETS #
			for subnet in CHARM_CONFIG.get('internal_network_subnets').split(',') :
				if subnet :
					rule = ['INPUT', '-s', subnet , '-j', 'ACCEPT']
						if not rule_exists( rule ) :
							make_rule( rule, INSERT )

		# VIRTUAL IP #
		else:
			pass











def _nat():
	pass
