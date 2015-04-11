#!/usr/bin/env python3
"""
Generate CA certificate and host certificates using OpenSSL
"""


### TO DO PATHS SHOULD BE STORED AS A MACROS


from strongswan import (
	OPENSSL,
	REQ,
	CA,
	IPSEC_D_PRIVATE,
	IPSEC_D_CACERTS,
	IPSEC_D_CERTS,
	IPSEC_D_REQS,
	_check_output
)

from charmhelpers.core import (
	hookenv
)

config = hookenv.config()

def generate_ca():
	cmd = [
		OPENSSL,
		REQ , '-x509',
		'-days', '3650',
		'-newkey', 'rsa:4096',
		'-keyout', '{}cakey.pem'.format(IPSEC_D_PRIVATE),
		'-out', '{}cacert.pem'.format(IPSEC_D_CACERTS),
		'-nodes',
	]
	_check_output( cmd, fatal=True, message="CA generation" )




def generate_csr( identity ):
	cmd = [
		OPENSSL,
		REQ,
		'-newkey', 'rsa:2048',
		'-keyout', '{}{}Key.pem'.format( IPSEC_D_PRIVATE, identity ),  
		'-out', '{}{}Req.pem'.format( IPSEC_D_REQS, identity )
		'-nodes'
	]
	_check_output( cmd, fatal=True, message="CSR generation" )




def sign_cert( identity ):
	# sign the certificate with the CA.
	cmd = [
		OPENSSL,
		CA,
		'-in', '{}{}Req.pem'.format( IPSEC_D_REQS, identity ),
		'-days', '1825',
		'-out', '{}{}Cert.pem'.format( IPSEC_D_CERTS, identity ),
		'-cert', '/etc/ipsec.d/cacerts/caCert.pem',
		'-keyfile', '/etc/ipsec.d/private/caKey.pem',
		'-notext', '-batch'
	]
	_check_output( cmd, fatal=True, message="CA signing" )



#create openssl.cnf for ipsec.
def _create():
	pass
	