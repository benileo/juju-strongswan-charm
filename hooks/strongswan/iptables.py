

from charmhelpers.core import hookenv
from strongswan.util import _check_call
from strongswan.constants import (
	CONFIG, 
	INSERT, 
	APPEND, 
	DELETE, 
	ACCEPT, 
	DROP, 
	SSH, 
	IKE, 
	NAT_T 
)
 
import iptc


def save():
	"""
	save iptables rules
	"""
	_check_call( ["iptables-save"] , quiet=True )

def nat():
	""" 
	Configure nat table
	"""
	hookenv.log("configuring iptables nat table", level=hookenv.INFO )

	# create the NAT table object
	table = Table("NAT")


	


def filter():
	"""
	Configure filter table
	"""
	hookenv.log("configuring iptables filter table", level=hookenv.INFO )

	# create filter table object 
	table = Table("FILTER")

	# allow inbound loopback traffic
	rule = iptc.Rule()
	rule.in_interface = 'lo'
	table.make_rule(rule, table._input, INSERT )

	# allow outbound loopback traffic
	rule = iptc.Rule()
	rule.out_interface = 'lo'
	table.make_rule(rule, table._output, INSERT )

	# allow IKE, inbound & outbound
	rule = iptc.Rule()
	rule.protocol = "udp" 
	match = rule.create_match("udp")
	match.dport = IKE
	match.sport = IKE
	table.make_rule(rule, table._input, INSERT)
	table.make_rule(rule, table._output, INSERT)

	# allow NAT-T, inbound & outbound #review this 
	match.dport = NAT_T
	match.sport = NAT_T
	table.make_rule(rule, table._input, INSERT)
	table.make_rule(rule, table._output, INSERT)

	# esp in and out.
	rule = iptc.Rule()
	rule.protocol = "esp" 
	table.make_rule(rule, table._input, INSERT)
	table.make_rule(rule, table._output, INSERT)

	# ssh in 
	rule = iptc.Rule()
	rule.protocol = "tcp" 
	match = rule.create_match("tcp")
	match.dport = SSH
	table.make_rule(rule, table._input, APPEND)

	# ssh out 
	match.reset()
	match.sport = SSH
	table.make_rule(rule, table._output, APPEND)

	
	if CONFIG.get("public_network") :
		
		# allow all est conns out
		rule = iptc.Rule()
		match = rule.create_match("conntrack")
		match.ctstate = "ESTABLISHED,RELATED,NEW"
		table.make_rule(rule, table._output, APPEND)

		# allow all est conns in
		match.reset()
		match.ctstate = "ESTABLISHED,RELATED"
		table.make_rule(rule, table._input, APPEND)

		# delete all apt-out
		rule = iptc.Rule()
		rule.protocol = "tcp"
		match1 = rule.create_match("tcp")
		match1.dport = "80"
		match2 = rule.create_match("conntrack")
		match2.ctstate = "NEW,ESTABLISHED"
		table.make_rule(rule, table._output, DELETE)

		# delete all apt-in
		match1.reset()
		match1.sport = "80"
		match2.reset()
		match2.ctstate = "ESTABLISHED"
		table.make_rule(rule, table._input, DELETE)

		# delete dns udp in 
		rule = iptc.Rule()
		rule.protocol = "udp"
		match = rule.create_match("udp")
		match.sport = "53"
		match = rule.create_match("conntrack")
		match.ctstate = "ESTABLISHED,RELATED"
		table.make_rule( rule, table._input, DELETE )

		# delete dns udp out
		rule = iptc.Rule()
		rule.protocol = "udp"
		match = rule.create_match("udp")
		match.dport = "53"
		match = rule.create_match("conntrack")
		match.ctstate = "NEW,ESTABLISHED"
		table.make_rule( rule, table._output, DELETE )

		# delete dns tcp in 
		rule = iptc.Rule()
		rule.protocol = "tcp"
		match = rule.create_match("tcp")
		match.sport = "53"
		match = rule.create_match("conntrack")
		match.ctstate = "ESTABLISHED,RELATED"
		table.make_rule( rule, table._input, DELETE )

		# delete dns tcp out 
		rule = iptc.Rule()
		rule.protocol = "tcp"
		match = rule.create_match("tcp")
		match.dport = "53"
		match = rule.create_match("conntrack")
		match.ctstate = "NEW,ESTABLISHED"
		table.make_rule( rule, table._output, DELETE )

	else:
		# dns udp in 
		rule = iptc.Rule()
		rule.protocol = "udp"
		match = rule.create_match("udp")
		match.sport = "53"
		match = rule.create_match("conntrack")
		match.ctstate = "ESTABLISHED,RELATED"
		table.make_rule( rule, table._input, APPEND )

		# dns udp out
		rule = iptc.Rule()
		rule.protocol = "udp"
		match = rule.create_match("udp")
		match.dport = "53"
		match = rule.create_match("conntrack")
		match.ctstate = "NEW,ESTABLISHED"
		table.make_rule( rule, table._output, APPEND )

		# dns tcp in 
		rule = iptc.Rule()
		rule.protocol = "tcp"
		match = rule.create_match("tcp")
		match.sport = "53"
		match = rule.create_match("conntrack")
		match.ctstate = "ESTABLISHED,RELATED"
		table.make_rule( rule, table._input, APPEND )

		# dns tcp out 
		rule = iptc.Rule()
		rule.protocol = "tcp"
		match = rule.create_match("tcp")
		match.dport = "53"
		match = rule.create_match("conntrack")
		match.ctstate = "NEW,ESTABLISHED"
		table.make_rule( rule, table._output, APPEND )

		# allow all apt-out
		rule = iptc.Rule()
		rule.protocol = "tcp"
		match1 = rule.create_match("tcp")
		match1.dport = "80"
		match2 = rule.create_match("conntrack")
		match2.ctstate = "NEW,ESTABLISHED"
		table.make_rule(rule, table._output, APPEND)

		# allow all apt-in
		match1.reset()
		match1.sport = "80"
		match2.reset()
		match2.ctstate = "ESTABLISHED"
		table.make_rule(rule, table._input, APPEND)

		# disallow all est conns out
		rule = iptc.Rule()
		match = rule.create_match("conntrack")
		match.ctstate = "ESTABLISHED,RELATED,NEW"
		table.make_rule(rule, table._output, DELETE)

		# disallow all est conns in
		match.reset()
		match.ctstate = "ESTABLISHED,RELATED"
		table.make_rule(rule, table._input, DELETE )

	# dhcp #this needs to be reviewed
	rule = iptc.Rule()
	rule.protocol = "udp"
	match = rule.create_match("udp")
	match.dport = "67:68"
	match.sport = "67:68"
	table.make_rule(rule, table._input, APPEND)
	table.make_rule(rule, table._output, APPEND)

	
	# set default policy to DROP for filter tables.
	hookenv.log("Setting default policy to drop for all filter rule chains", 
		level=hookenv.INFO)
	table._input.set_policy("DROP")
	table._output.set_policy("DROP")
	table._forward.set_policy("DROP")


class Table:
	"""
	A container class for holding iptables information
	"""
	def __init__(self, table):
		if table == "FILTER" :
			self._input = iptc.Table(iptc.Table.FILTER).chains[0]
			self._forward = iptc.Table(iptc.Table.FILTER).chains[1]
			self._output = iptc.Table(iptc.Table.FILTER).chains[2]
		elif table == "NAT" :
			self._prerouting = iptc.Table(iptc.Table.NAT).chains[0]
			self._input = iptc.Table(iptc.Table.NAT).chains[1]
			self._output = iptc.Table(iptc.Table.NAT).chains[2]
			self._postrouting = iptc.Table(iptc.Table.NAT).chains[3]

	def exists(self, rule, chain):
		"""
		Does a rule already exists in a chain?

		:param rule: A iptc.Rule() object
		:param chain: An iptc.Chain() object

		:return True if the rule exists, else False 
		"""
		for rules in chain.rules:
			if rules.__eq__(rule):
				return True
		return False

	def make_rule(self, rule, chain, rtype):
		"""
		Make a rule in a given chain

		:param rule: a iptc.Rule() object
		:param chain: a iptc.Chain() object
		:param rtype: rule type
		"""
		rule.target = rule.create_target(ACCEPT)
		if rtype != DELETE :
			if not self.exists(rule, chain):
				if rtype == APPEND:
					chain.append_rule(rule)
				elif rtype == INSERT:
					chain.insert_rule(rule)
		else:
			if self.exists(rule, chain):
				chain.delete_rule(rule)
