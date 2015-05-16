

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

	# don't NAT outbound ipsec traffic
	rule = iptc.Rule()
	match = rule.create_match("policy")
	rule.pol = "ipsec"
	rule.dir = "out"
	make_rule( rule, table._postrouting, INSERT )


	# And this is where I hit the wall on ideas for the charm........


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
