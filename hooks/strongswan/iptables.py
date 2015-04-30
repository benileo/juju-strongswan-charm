
from charmhelpers.core import hookenv
from strongswan.constants import (
	CONFIG, INPUT, OUTPUT, 
)
from strongswan.util import _check_call 
import iptc

filter_table = iptc.Table(iptc.Table.FILTER)
nat_table = iptc.Table(iptc.Table.NAT)

def save():
	"""
	@description: saves iptables rules
	"""
	_check_call( ["iptables-save"] , quiet=True )

def nat():
	"""
	@description: configures 
	Configures IPtables nat table
	"""
	pass


def filter():
	"""
	@description: configures filter table
	"""
	hookenv.log("Configuring iptables firewall for IPsec", level=hookenv.INFO )
	_loopback()


	# allow IKE and NAT-T Inbound and Outbound
	make_rule(ALLOW_IKE, INPUT, INSERT)
	make_rule(ALLOW_IKE, OUTPUT, INSERT )
	make_rule(ALLOW_NAT_T, INPUT, INSERT)
	make_rule(ALLOW_NAT_T, OUTPUT, INSERT)

	# allow either AH or ESP inbound and outbound
	if CONFIG.get("ipsec_protocol") == "esp":
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
	make_rule(ALLOW_SSH_IN, INPUT, APPEND)
	make_rule(ALLOW_SSH_OUT, OUTPUT, APPEND)

	# all DNS gets through the firewall
	if not CONFIG.get("public_network"):
		make_rule(ALLOW_DNS_UDP_IN, INPUT, APPEND)
		make_rule(ALLOW_DNS_UDP_OUT, OUTPUT, APPEND)
		make_rule(ALLOW_DNS_TCP_IN, INPUT, APPEND)
		make_rule(ALLOW_DNS_TCP_OUT, OUTPUT, APPEND)

	# DHCP 
	make_rule(ALLOW_DHCP, INPUT, APPEND)
	make_rule(ALLOW_DHCP, OUTPUT, APPEND)

	# allow all established outbound connections
	# if NO, we must allow apt-ports for install and updates
	if CONFIG.get("public_network"):
		make_rule(ALLOW_EST_CONN_IN, INPUT, APPEND)
		make_rule(ALLOW_EST_CONN_OUT, OUTPUT, APPEND)
		make_rule(ALLOW_APT_IN, INPUT, DELETE)
		make_rule(ALLOW_APT_OUT, OUTPUT, DELETE)
	else:
		make_rule(ALLOW_EST_CONN_IN, INPUT, DELETE)
		make_rule(ALLOW_EST_CONN_OUT, OUTPUT, DELETE)
		make_rule(ALLOW_APT_IN, INPUT, APPEND)
		make_rule(ALLOW_APT_OUT, OUTPUT, APPEND)

	#set default policy to DROP for filter tables.
	hookenv.log("Setting default policy to drop for all filter rule chains", level=hookenv.INFO)
	_check_call( [IPTABLES, POLICY, FORWARD , DROP ], log_cmd=False )
	_check_call( [IPTABLES, POLICY, INPUT , DROP ], log_cmd=False )
	_check_call( [IPTABLES, POLICY, OUTPUT , DROP ], log_cmd=False )


def _loopback():
	rule = iptc.Rule()
	rule.in_interface = 'lo'
	rule.target = rule.create_target(ACCEPT)
	make_rule( rule, FILTER, INPUT, INSERT )
	rule.out_interface = 'lo'
	rule.in_interface = None
	make_rule( rule, FILTER, OUTPUT, INPUT)

def make_rule(rule, table, chain, rtype ) :
	if table == FILTER :
		if rtype == INSERT :
			iptc.Chain(iptc.Table(iptc.Table.FILTER), chain ).insert_rule(rule)
		elif rtype == APPEND :
			iptc.Chain(iptc.Table(iptc.Table.FILTER), chain ).append_rule(rule)
		elif rtype == DELETE :
			iptc.Chain(iptc.Table(iptc.Table.FILTER), chain ).delete_rule(rule)
	elif table == NAT :
		if rtype == INSERT :
			iptc.Chain(iptc.Table(iptc.Table.NAT), chain ).insert_rule(rule)
		elif rtype == APPEND :
			iptc.Chain(iptc.Table(iptc.Table.NAT), chain ).append_rule(rule)
		elif rtype == DELETE :
			iptc.Chain(iptc.Table(iptc.Table.NAT), chain ).delete_rule(rule)


		





