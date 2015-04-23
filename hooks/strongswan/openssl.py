#!/usr/bin/env python3
"""
Generate CA certificate and host certificates using OpenSSL
"""

from OpenSSL import crypto
from strongswan.util import convert_to_seconds
from strongswan.constants import (
	IPSEC_D_PRIVATE,
	IPSEC_D_CACERTS,
	IPSEC_D_CERTS,
	IPSEC_D_REQS,
	CA_KEY,
	CA_CERT
)

def create_key_pair( keytype, bits ):
	pkey = crypto.PKey()
	pkey.generate_key( keytype, bits )
	return pkey


def create_cert_request( pkey, subject, digest='sha1' ):
	req = X509Req()
	subj = req.get_subject()
	for key, value in subject.items():
		if key == "e":
			setattr(subj, "emailAddress", value )
		else:
			setattr(subj, key.upper(), value )
	req.set_pubkey(pkey)
	req.sign(pkey, digest )
	return req


def create_certificate( 
		req, 
		(issuerCert, issuerKey), 
		serial, 
		(notBefore, notAfter),
		lifetime,
		digest='sha1' 
	):
	cert = crypto.X509()
	cert.set_serial_number(serial)
	cert.gmtime_adj_notBefore(0)
	cert.gmtime_adj_notAfter( convert_to_seconds(lifetime) )
	cert.set_issuer( issuerCert.get_subject() )
	cert.set_subject( req.get_subject() )
	cert.set_pubkey( req.get_pubkey() )
	cert.sign( issuerKey, digest )
	return cert 

	

def create_root_cert(  
		subject,
		lifetime,
		keysize,
		digest='sha1' 
	):
	
	k = create_key_pair( crypto.TYPE_RSA, keysize )
	r = create_cert_request( k, subject )
	c = create_certificate(r, (r,k), 0, (0, lifetime) )

	# write the key and cert to the proper IPsec directories
	with open("{0}{1}".format(IPSEC_D_PRIVATE, CA_KEY ), 'bw') as fd:
		fd.write(crypto.dump_privatekey( crypto.FILETYPE_PEM, k ) )
	
	with open("{0}{1}".format(IPSEC_D_CACERTS, CA_CERT ), 'bw' ) as fd:
		fd.write(crypto.dump_certificate( crypto.FILETYPE_PEM, c ) )



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