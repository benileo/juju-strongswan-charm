#!/usr/bin/env python3
"""
File containing wrapper and helpers functions
"""


# returns the essential strongswan packages 
# other packages are added based on initial launch options
# other features can added be added later
# depending on how you want to set up strongswan this can differ
def ss_packages( config ):
	ss_essential = [ "libstrongswan" , "strongswan-ike", "strongswan-plugin-openssl"
	, "strongswan-starter", "strongswan" ]

	# fill as config options 
	ss_extra = []
	
	return (ss_essential + ss_extra)


# based on the config passed to this function
# strongswan will be set up as packet forwarder or not
# what if the config changes?
# w

def ss_sysctl( config ):

	if config['ip_forward'] :
		# modify the sys ctl file
		

