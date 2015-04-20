#!/usr/bin/env python3
"""
Generate CA certificate and host certificates using OpenSSL
"""

from strongswan.constants import (
	IPSEC_D_PRIVATE,
	IPSEC_D_CACERTS,
	IPSEC_D_CERTS,
	IPSEC_D_REQS,
	CA_KEY,
	CA_CERT
)

# make sure that we have installed necessary dependencies for pyOpenSSL
from OpenSSL import crypto	


# Generate a CA root certificate and private key 
# Writes private key to /etc/ipsec.d/private/caKey. 
def create_ca_cert(  digest='sha1', **rdn ):
	pkey = crypto.PKey()
	pkey.generate_key( crypto.TYPE_RSA, 4096 )
	req = crypto.X509Req()
	subj = req.get_subject()
	for (key, value) in rdn.items() :
		setattr( subj, key, value )
	req.set_pubkey( pkey )
	req.sign( pkey, digest )
	cert = crypto.X509()
	cert.set_serial_number( 0 )
	cert.gmtime_adj_notBefore( 0 )
	cert.gmtime_adj_notAfter( 60*60*24*365*10 )
	cert.set_issuer( req.get_subject() )
	cert.set_subject( req.get_subject() )
	cert.set_pubkey( req.get_pubkey() )
	cert.sign( pkey, digest )
	with open("{0}{1}".format(IPSEC_D_PRIVATE, CA_KEY ), 'bw') as fd:
		fd.write(crypto.dump_privatekey( crypto.FILETYPE_PEM, pkey ) )
	with open("{0}{1}".format(IPSEC_D_CACERTS, CA_CERT ), 'bw' ) as fd:
		fd.write(crypto.dump_certificate( crypto.FILETYPE_PEM, cert ) )


def create_host_cert( handle , digest='sha1' , **rdn ) :
	pkey = crypto.PKey()
	pkey.generate_key( crypto.TYPE_RSA, 2048 )
	req = crypto.X509Req()
	subj = req.get_subject()
	for (key, value) in rdn.items():
		setattr(subj,key,value)
	req.set_pubkey(pkey)
	req.sign( pkey, digest )
	cert = crypto.X509()
	cert.set_serial_number( 1 )
	cert.gmtime_adj_notBefore( 0 )
	cert.gmtime_adj_notAfter( 60*60*24*365*5 )
	with open("{0}{1}".format(IPSEC_D_CACERTS, CA_CERT ), 'br' ) as fd:
		cacert = crypto.load_certificate( crypto.FILETYPE_PEM, fd.read() )
	cert.set_issuer( cacert.get_subject() )
	cert.set_subject( req.get_subject() )
	cert.set_pubkey( req.get_pubkey() )
	with open("{0}{1}".format(IPSEC_D_PRIVATE, CA_KEY ) , 'br' ) as fd:
		cakey = crypto.load_privatekey( crypto.FILETYPE_PEM, fd.read() )
	cert.sign(cakey, digest)
	with open("{0}{1}Key.pem".format(IPSEC_D_PRIVATE, handle ), 'bw' ) as fd :
		fd.write(crypto.dump_privatekey( crypto.FILETYPE_PEM, pkey ) )
	with open("{0}{1}Cert.pem".format( IPSEC_D_CERTS, handle ) , 'bw' ) as fd :
		fd.write(crypto.dump_certificate( crypto.FILETYPE_PEM, cert ) )