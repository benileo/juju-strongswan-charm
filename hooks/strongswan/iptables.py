
from charmhelpers.core import hookenv
from strongswan.constants import (
	CONFIG, FILTER, NAT, INSERT, APPEND, DELETE,
	ACCEPT, DROP, SSH, IKE, NAT_T, 
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

	# allow IKE, inbound & outbound
	rule = iptc.Rule()
	rule.protocol = "udp"
	match = rule.create_match("udp")
	match.dport = IKE
	rule.add_match(match)
	rule.target = rule.create_target(ACCEPT)
	table.make_rule(rule, table._input, INSERT)
	table.make_rule(rule, table._output, INSERT)

	# allow NAT-T, inbound & outbound
	rule = iptc.Rule()
	rule.protocol = "udp"
	match = rule.create_match("udp")
	match.dport = NAT_T
	rule.add_match(match)
	rule.target = rule.create_target(ACCEPT)
	table.make_rule(rule, table._input, INSERT)
	table.make_rule(rule, table._output, INSERT)

	# esp 
	rule = iptc.Rule()
	rule.protocol = "esp"
	rule.target = rule.create_target(ACCEPT)
	table.make_rule(rule, table._input, INSERT)
	table.make_rule(rule, table._output, INSERT)

	# ssh in 
	rule = iptc.Rule()
	rule.protocol = "tcp"
	match = rule.create_match("tcp")
	match.sport = SSH
	match.dport = "49152:65535"
	rule.add_match(match)
	rule.target = rule.create_target(ACCEPT)
	table.make_rule(rule, table._input, APPEND)

	# ssh out
	rule = iptc.Rule()
	rule.protocol = "tcp"
	match = rule.create_match("tcp")
	match.dport = SSH 
	match.sport = "49152:65535"
	rule.add_match(match)
	rule.target = rule.create_target(ACCEPT)
	table.make_rule(rule, table._output, APPEND)

	
	if CONFIG.get("public_network") :
		# allow all est conns out
		rule = ipt
		# delete dns udp in 
		rule = iptc.Rule()
		rule.protocol = "udp"
		match = rule.create_match("udp")
		match.sport = "53"
		match.state = "ESTABLISHED,RELATED"
		rule.add_match(match)
		rule.target = rule.create_target(ACCEPT)
		table.make_rule( rule, table._input, DELETE )

		# delete dns udp out
		rule = iptc.Rule()
		rule.protocol = "udp"
		match = rule.create_match("udp")
		match.dport = "53"
		match.state = "NEW,ESTABLISHED"
		rule.add_match(match)
		rule.target = rule.create_target(ACCEPT)
		table.make_rule( rule, table._output, DELETE )

		# delete dns tcp in 
		rule = iptc.Rule()
		rule.protocol = "tcp"
		match = rule.create_match("tcp")
		match.sport = "53"
		match.state = "ESTABLISHED,RELATED"
		rule.add_match(match)
		rule.target = rule.create_target(ACCEPT)
		table.make_rule( rule, table._input, DELETE )

		# delete dns tcp out 
		rule = iptc.Rule()
		rule.protocol = "tcp"
		match = rule.create_match("tcp")
		match.dport = "53"
		match.state = "NEW,ESTABLISHED"
		rule.add_match(match)
		rule.target = rule.create_target(ACCEPT)
		table.make_rule( rule, table._output, DELETE )

	else:
		# dns udp in 
		rule = iptc.Rule()
		rule.protocol = "udp"
		match = rule.create_match("udp")
		match.sport = "53"
		match.state = "ESTABLISHED,RELATED"
		rule.add_match(match)
		rule.target = rule.create_target(ACCEPT)
		table.make_rule( rule, table._input, APPEND )

		# udp out
		rule = iptc.Rule()
		rule.protocol = "udp"
		match = rule.create_match("udp")
		match.dport = "53"
		match.state = "NEW,ESTABLISHED"
		rule.add_match(match)
		rule.target = rule.create_target(ACCEPT)
		table.make_rule( rule, table._output, APPEND )

		#tcp in 
		rule = iptc.Rule()
		rule.protocol = "tcp"
		match = rule.create_match("tcp")
		match.sport = "53"
		match.state = "ESTABLISHED,RELATED"
		rule.add_match(match)
		rule.target = rule.create_target(ACCEPT)
		table.make_rule( rule, table._input, APPEND )

		#tcp out 
		rule = iptc.Rule()
		rule.protocol = "tcp"
		match = rule.create_match("tcp")
		match.dport = "53"
		match.state = "NEW,ESTABLISHED"
		rule.add_match(match)
		rule.target = rule.create_target(ACCEPT)
		table.make_rule( rule, table._output, APPEND )

	#dhcp #this needs to be reviewed
	rule = iptc.Rule()
	rule.protocol = "udp"
	match = create_match("udp")
	match.dport = "67:68"
	match.sport = "67:68"
	rule.add_match(match)
	rule.target = rule.create_target(ACCEPT)
	table.make_rule(rule, table._input, APPEND)
	table.make_rule(rule, table._output, APPEND)

	#





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

