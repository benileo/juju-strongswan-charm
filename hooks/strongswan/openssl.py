#!/usr/bin/env python3
"""
Generate CA certificate and host certificates using OpenSSL
"""


### TO DO PATHS SHOULD BE STORED AS A MACROS


from strongswan import (
	OPENSSL,
	REQ,
	CA,
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
		'-days', '1460',
		'-newkey', 'rsa:4096',
		'-keyout', '/etc/ipsec.d/private/caKey.pem',
		'-out', '/etc/ipsec.d/cacerts/caCert.pem',
		'-nodes',
	]

	# append the cert info
	cmd.extend( _cert_info() )

	# create the CA
	_check_output( cmd, fatal=True, message="CA generation" )




def generate_cert( name ):

	# create the host key and cert request
	cmd = [
		OPENSSL,
		REQ,
		'-newkey', 'rsa:2048',
		'-keyout', '/etc/ipsec.d/private/{}Key.pem'.format(name),  
		'-out', 'hostReq.pem',
		'-nodes'
	]
	cmd.extend( _cert_info() )
	_check_output( cmd, fatal=True, message="CSR generation" )


	# sign the certificate with the CA.
	cmd = [
		OPENSSL,
		CA,
		'-in', 'hostReq.pem',
		'-days', '730',
		'-out', '/etc/ipsec.d/certs/{}Cert.pem'.format(name),
		'-cert', '/etc/ipsec.d/cacerts/caCert.pem',
		'-keyfile', '/etc/ipsec.d/private/caKey.pem',
		'-notext', '-batch'
	]
	_check_output( cmd, fatal=True, message="CA signing" )



# obtain DN certificate information prior to creation of the CA.
# honestly not sure I will deal with this.
def _cert_info():

	_subj = ""

	if config.get("fqdn") :
		_subj += '/subjectAltName=DNS:{}'.format( config.get("fqdn") )

	if _subj :
		return [ '-subj' , _subj ]
	else:
		return []