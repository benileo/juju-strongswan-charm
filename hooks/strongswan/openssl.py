#!/usr/bin/env python3
"""
Generate CA certificate and host certificates using OpenSSL
"""

from OpenSSL import crypto
from random import randint
from math import ceil
from time import time
from strongswan.util import convert_to_seconds
from strongswan.constants import (
	IPSEC_D_PRIVATE,
	IPSEC_D_CACERTS,
	IPSEC_D_CERTS,
	IPSEC_D_REQS,
	CA_KEY,
	CA_CERT,
	SERVER_CERT_NAME
)

def load_ca_cert():
	with open("{0}{1}".format(IPSEC_D_CACERTS, CA_CERT ), 'br' ) as fd:
		cacert = crypto.load_certificate( crypto.FILETYPE_PEM, fd.read() )
	return cacert

def load_ca_key():
	with open("{0}{1}".format(IPSEC_D_PRIVATE, CA_KEY ) , 'br' ) as fd:
		cakey = crypto.load_privatekey( crypto.FILETYPE_PEM, fd.read() )
	return cakey

def dump_ca_key(k):
	with open("{0}{1}".format(IPSEC_D_PRIVATE, CA_KEY ), 'bw') as fd:
		fd.write(crypto.dump_privatekey( crypto.FILETYPE_PEM, k ) )

def dump_ca_cert(c):
	with open("{0}{1}".format(IPSEC_D_CACERTS, CA_CERT ), 'bw' ) as fd:
		fd.write(crypto.dump_certificate( crypto.FILETYPE_PEM, c ) )

def dump_key(pkey,keyname):
	with open("{0}{1}Key.pem".format(IPSEC_D_PRIVATE, keyname ), 'bw' ) as fd :
		fd.write(crypto.dump_privatekey( crypto.FILETYPE_PEM, pkey ) )

def dump_cert(cert, certname):
	with open("{0}{1}Cert.pem".format( IPSEC_D_CERTS, certname ) , 'bw' ) as fd :
		fd.write(crypto.dump_certificate( crypto.FILETYPE_PEM, cert ) )

def create_key_pair( keytype, bits ):
	pkey = crypto.PKey()
	pkey.generate_key( keytype, bits )
	return pkey


def create_cert_request( pkey, subject, digest='sha1' ):
	req = crypto.X509Req()
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
		issuerCert, 
		issuerKey,  
		lifetime,
		digest='sha1' 
	):
	cert = crypto.X509()
	cert.set_serial_number(generate_serial())
	cert.gmtime_adj_notBefore(0)
	cert.gmtime_adj_notAfter( convert_to_seconds(lifetime) )
	cert.set_issuer( issuerCert.get_subject() )
	cert.set_subject( req.get_subject() )
	cert.set_pubkey( req.get_pubkey() )
	cert.sign( issuerKey, digest )
	return cert 


# create and sign our own certificate
def create_root_cert(  
		subject,
		lifetime,
		keysize,
		digest='sha1' 
	):
	
	# create the cakey and cacert
	k = create_key_pair( crypto.TYPE_RSA, keysize )
	r = create_cert_request( k, subject )
	c = create_certificate(r,r,k,lifetime)
	dump_ca_cert(c)
	dump_ca_key(k)

	# create the server key and cert
	create_host_cert(
		subject,
		lifetime,
		keysize,
		SERVER_CERT_NAME
	)

def create_host_cert(
		subject,
		lifetime,
		keysize,
		name=None,
		digest='sha1'
	):
	k = create_key_pair( crypto.TYPE_RSA, keysize )
	r = create_cert_request( k, subject )
	c = create_certificate(
		r, 
		load_ca_cert(),
		load_ca_key(),
		lifetime
	)
	_name = name if name else str( c.get_serial_number() )
	dump_key(k,_name)
	dump_cert(c,_name)



def generate_serial():
	_time = str( ceil( time() ) )
	_rnum = str( randint( 0, 2**100 ) )
	_ser = _rnum + _time
	if ( len(_ser) % 2 ) != 0 :
		_ser += '8' 
	return int(_ser)


