#!/usr/bin/env python3
"""
Code for strongswan sysctl 
"""

from strongswan import (
	IPV6_FORWARD,
	IPV4_FORWARD,
	SYSCTL_PATH,
	CHARM_CONFIG,
	_check_output
)
from charmhelpers.core.sysctl import (
	create
)
from charmhelpers.core import (
	hookenv
)
from json import (
	dumps
)

def configure_sysctl():
	_dict = {}
	
	if CHARM_CONFIG.get("ip_forward") :
		_dict[IPV4_FORWARD] = 1
	
	if CHARM_CONFIG.get("ip6_forward") :
		_dict[IPV6_FORWARD] = 1
	
	create( dumps(_dict) , SYSCTL_PATH )

# Make copy of sysctl.conf and /etc/hosts for sys admin reference
def cp_sysctl_file():
	_check_output(['cp', '/etc/sysctl.conf', '/etc/sysctl.conf.original'])
	hookenv.log("Copy of sysctl file created: /etc/sysctl.conf.original", level=hookenv.INFO )
	