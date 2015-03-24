#!/usr/bin/env python3
"""
File containing wrapper and helpers functions
"""

import os
import subprocess as sp
from charmhelpers.core import hookenv


def ss_apt_pkgs( config ):
	avail_pkgs = ss_apt_cache()

	if len(avail_pkgs) > 0 :
		hookenv.log('Strongswan Packages:')
		for pkg in avail_pkgs:
			hookenv.log(pkg)
	else:
		hookenv.log('No packages........Something is up....Not throwing exception though')

	hookenv.log('installing packages: ')
	hookenv.log('strongswan')
	return [ "strongswan" ]

def ss_apt_cache():
	avail_pkgs = []

	cmd = ["apt-cache", "search", "strongswan"]
	try:
		handler = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE )
		data = handler.communicate()[0].decode('utf-8') 
	except (OSError, sp.TimeoutExpired, ValueError) as error : 
		hookenv.log(error)

	for s in ( data.split('\n') ):
		t = s.split(' ')
		avail_pkgs.append(t[0])

	return avail_pkgs