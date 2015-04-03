#!/usr/bin/env python3
"""
File containing wrapper and helpers functions
"""

import subprocess as sp
from charmhelpers.core import hookenv
import time

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

def ss_apt_update():

	cmd = ['apt-get' , 'update' ]

	apt_retry_count = 0
	apt_retry_max = 0
	apt_retry_wait = 10

	result = None

	while result == None or result == 100 :
		try:
			sp.call( cmd, timeout=30 )
		except sp.CalledProcessError as e:
			apt_retry_count += 1
			if apt_retry_count > apt_retry_max : 
				raise
			result = e.returncode
			hookenv.log("Couldn't aquire DPKG lock trying again in {0}".format(apt_retry_wait) )
			time.sleep(apt_retry_wait)
		except sp.TimeoutExpired as e:
			pass