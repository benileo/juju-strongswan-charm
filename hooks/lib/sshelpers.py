#!/usr/bin/env python3
"""
File containing wrapper and helpers functions
"""


# returns the essential strongswan packages 
# other packages are added based on initial launch options
# other features can added be added later
# depending on how you want to set up strongswan this can differ
def ss_packages():
	ss_essential = [ "libstrongswan" , "strongswan-ike", "strongswan-plugin-openssl"
	, "strongswan-starter", "strongswan" ]

	# fill as config options 
	ss_extra = []
	
	return (ss_essential + ss_extra)

