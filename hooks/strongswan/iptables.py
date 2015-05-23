
from sys import path
if "./lib" not in path:
	path.append("./lib")
	
from charmhelpers.core import hookenv
from strongswan.util import _check_call
from strongswan.constants import (
	CONFIG, 
	INSERT, 
	APPEND,  
	ACCEPT,
	DELETE 
)
 
import lib.iptc as iptc

def flush(table):
	"""
	Flushes iptables rules

	:param table: the table
	"""
	_check_call( ["iptables", "-t", table , "-F"] )



def save():
	"""
	save iptables rules
	"""
	_check_call( ["iptables-save"] , quiet=True )

def nat():
	""" 
	Configures the iptables NAT table
	""" 
	nat_table = Table("NAT")
	access_subnets = [x for x in CONFIG['access_subnets'].split(',') if x]
	virtual_subnets = [x for x in CONFIG['virtual_subnets'].split(',') if x]

	# don't masquerade any traffic from access to virtual subnets
	# masquerade all traffic from virutual to 0.0.0.0/0 
	for anet in access_subnets:
		for vnet in virtual_subnets:
			rule = iptc.Rule()
			if anet == '0.0.0.0/0':
				rule.set_src(vnet)
				rule.target = rule.create_target("MASQUERADE")
				nat_table._postrouting.append_rule(rule)
			else:
				rule.set_src( vnet )
				rule.set_dst( anet )
				nat_table.make_rule(rule, nat_table._postrouting, INSERT)
				rule.set_src( anet )
				rule.set_dst( vnet )
				nat_table.make_rule(rule, nat_table._postrouting, INSERT)

	# don't NAT outbound IPsec traffic
	rule = iptc.Rule()
	match = rule.create_match("policy")
	rule.pol = "ipsec"
	rule.dir = "out"
	nat_table.make_rule(rule, nat_table._postrouting, INSERT)

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
