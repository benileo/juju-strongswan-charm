
from sys import path
if "./lib" not in path:
	path.append("./lib")

from strongswan.constants import IPSEC_CONF
from ipsecparse import load, dumps


class IpsecConfig(object):
	def __init__(self):
		with open(IPSEC_CONF, "r") as fd:
			self.ipsec_config = load(fd.read())