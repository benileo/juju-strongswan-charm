
from charmhelpers.core import hookenv
from strongswan.constants import (
	CONFIG, FILTER, NAT, INSERT, APPEND, DELETE,
	ACCEPT,
)
from strongswan.util import _check_call 
import iptc


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

	# create filter table object 
	table = Table(FILTER)

	# allow inbound loopback traffic
	rule = iptc.Rule()
	rule.in_interface = 'lo'
	rule.target = create_target(ACCEPT)
	table.make_rule(rule, table._input, INSERT )

	# allow outbound loopback traffic
	rule = iptc.Rule()
	rule.out_interface = 'lo'
	rule.target = create_target(ACCEPT)
	table.make_rule(rule, table._output, INSERT )

	# allow IKE, NAT-T inbound & outbound
	rule = iptc.Rule()
	rule.protocol = "udp"
	match = rule.create_match("udp")
	match.dport = "500"
	rule.add_match(match)
	rule.target = rule.create_target(ACCEPT)
	table.make_rule(rule, table._input, INSERT)
	table.make_rule(rule, table._output, INSERT)





class Table:
	def __init__(self, table):
		if table == FILTER :
			self._input = iptc.Table(iptc.Table.FILTER).chains[0]
			self._forward = iptc.Table(iptc.Table.FILTER).chains[1]
			self._output = iptc.Table(iptc.Table.FILTER).chains[2]
		elif table == NAT :
			self._prerouting = iptc.Table(iptc.Table.NAT).chains[0]
			self._input = iptc.Table(iptc.Table.NAT).chains[1]
			self._output = iptc.Table(iptc.Table.NAT).chains[2]
			self._postrouting = iptc.Table(iptc.Table.NAT).chains[3]

	def exists(self, rule, chain):
		for rules in chain.rules:
			if rules.__eq__(rule):
				return True
		return False

	def make_rule(self, rule, chain, rtype):
		if rtype != DELETE :
			if not self.exists(rule, chain):
				if rtype == APPEND:
					chain.append_rule(rule)
				elif rtype == INSERT:
					chain.insert_rule(rule)
		else:
			if self.exists(rule, chain):
				chain.delete_rule(rule)



# 	# allow IKE and NAT-T Inbound and Outbound
# 	make_rule(ALLOW_IKE, INPUT, INSERT)
# 	make_rule(ALLOW_IKE, OUTPUT, INSERT )
# 	make_rule(ALLOW_NAT_T, INPUT, INSERT)
# 	make_rule(ALLOW_NAT_T, OUTPUT, INSERT)

# 	# allow either AH or ESP inbound and outbound
# 	if CONFIG.get("ipsec_protocol") == "esp":
# 		make_rule(ALLOW_ESP, INPUT, INSERT)
# 		make_rule(ALLOW_AH , INPUT, DELETE )
# 		make_rule(ALLOW_ESP, OUTPUT, INSERT)
# 		make_rule(ALLOW_AH , OUTPUT, DELETE )
# 	else:
# 		make_rule(ALLOW_AH, INPUT, INSERT )
# 		make_rule(ALLOW_ESP, INPUT, DELETE )
# 		make_rule(ALLOW_AH, OUTPUT, INSERT )
# 		make_rule(ALLOW_ESP, OUTPUT, DELETE )

# 	# allow ssh inbound and outbound 
# 	make_rule(ALLOW_SSH_IN, INPUT, APPEND)
# 	make_rule(ALLOW_SSH_OUT, OUTPUT, APPEND)

# 	# all DNS gets through the firewall
# 	if not CONFIG.get("public_network"):
# 		make_rule(ALLOW_DNS_UDP_IN, INPUT, APPEND)
# 		make_rule(ALLOW_DNS_UDP_OUT, OUTPUT, APPEND)
# 		make_rule(ALLOW_DNS_TCP_IN, INPUT, APPEND)
# 		make_rule(ALLOW_DNS_TCP_OUT, OUTPUT, APPEND)

# 	# DHCP 
# 	make_rule(ALLOW_DHCP, INPUT, APPEND)
# 	make_rule(ALLOW_DHCP, OUTPUT, APPEND)

# 	# allow all established outbound connections
# 	# if NO, we must allow apt-ports for install and updates
# 	if CONFIG.get("public_network"):
# 		make_rule(ALLOW_EST_CONN_IN, INPUT, APPEND)
# 		make_rule(ALLOW_EST_CONN_OUT, OUTPUT, APPEND)
# 		make_rule(ALLOW_APT_IN, INPUT, DELETE)
# 		make_rule(ALLOW_APT_OUT, OUTPUT, DELETE)
# 	else:
# 		make_rule(ALLOW_EST_CONN_IN, INPUT, DELETE)
# 		make_rule(ALLOW_EST_CONN_OUT, OUTPUT, DELETE)
# 		make_rule(ALLOW_APT_IN, INPUT, APPEND)
# 		make_rule(ALLOW_APT_OUT, OUTPUT, APPEND)

# 	#set default policy to DROP for filter tables.
# 	hookenv.log("Setting default policy to drop for all filter rule chains", level=hookenv.INFO)
# 	_check_call( [IPTABLES, POLICY, FORWARD , DROP ], log_cmd=False )
# 	_check_call( [IPTABLES, POLICY, INPUT , DROP ], log_cmd=False )
# 	_check_call( [IPTABLES, POLICY, OUTPUT , DROP ], log_cmd=False )


# def _loopback():
# 	"""
# 	Allow all inbound and outbound traffic to the loopback in_interface
# 	"""
# 	rule = iptc.Rule()
# 	rule.in_interface = 'lo'
# 	rule.target = rule.create_target(ACCEPT)
# 	create(rule, filter_table.chains[2]



# 	make_rule( rule, FILTER, INPUT, INSERT )
# 	rule.out_interface = 'lo'
# 	rule.in_interface = None
# 	make_rule( rule, FILTER, OUTPUT, INPUT)
