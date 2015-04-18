#!/usr/bin/env python3
"""
Code for strongswan sysctl 
"""

from strongswan.constants import (
	IPV6_FORWARD,
	IPV4_FORWARD,
	SYSCTL_PATH,
	CONFIG,
)
from strongswan.util import _check_call
from charmhelpers.core.sysctl import create
from json import dumps



def configure_sysctl():
	_dict = {}
	
	if CONFIG.get("ip_forward") :
		_dict[IPV4_FORWARD] = 1
	
	if CONFIG.get("ip6_forward") :
		_dict[IPV6_FORWARD] = 1
	
	create( dumps(_dict) , SYSCTL_PATH )



# Make copy of sysctl.conf and /etc/hosts for sys admin reference
def cp_sysctl_file():
	_check_call(['cp', '/etc/sysctl.conf', '/etc/sysctl.conf.original'] )	