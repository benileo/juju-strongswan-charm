
from OpenSSL import crypto
from random import randint
from math import ceil
from time import time
from os.path import exists
from strongswan.util import convert_to_seconds, _check_call
from strongswan.constants import (
	IPSEC_D_PRIVATE	,
	IPSEC_D_CACERTS,
	IPSEC_D_CERTS,
	IPSEC_D_REQS,
	CA_KEY,
	CA_CERT,
	SERVER_CERT_NAME,
	EXPORT_DIR
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

def dump_key(pkey, keyname, directory):
	with open("{0}{1}Key.pem".format(directory, keyname ), 'bw' ) as fd :
		fd.write(crypto.dump_privatekey( crypto.FILETYPE_PEM, pkey ) )

def dump_cert(cert, certname, directory):
	with open("{0}{1}Cert.pem".format( directory , certname ) , 'bw' ) as fd :
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


def create_pkcs12( pkey, cert ):
	p12 = crypto.PKCS12()
	p12.set_certificate(cert)
	p12.set_privatekey(pkey)
	cacert = load_ca_cert()
	p12.set_ca_certificates([cacert])
	return ( p12.export() )



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
	k = create_key_pair( crypto.TYPE_RSA, keysize )
	r = create_cert_request( k, subject )
	c = create_certificate( r, 
		load_ca_cert(),
		load_ca_key(),
		lifetime
	)

	#dump the key and server certificate to appropriate directories 
	dump_key(k, SERVER_CERT_NAME, IPSEC_D_PRIVATE)
	dump_cert(c, SERVER_CERT_NAME, IPSEC_D_CERTS)

def create_host_cert(
		subject,
		lifetime,
		keysize,
		out,
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
	return ( create_outfile( out, k, c ) )  


def generate_serial():
	_time = str( ceil( time() ) )
	_rnum = str( randint( 0, 2**100 ) )
	_ser = _rnum + _time
	if ( len(_ser) % 2 ) != 0 :
		_ser += '8' 
	return int(_ser)


def create_outfile( out, key, cert ):
	"""
	@params
	out - the type of output, valid values are tar.gz or pkcs12
	key - a PKey object containing a keypair 
	cert - a X509 object
	@returns
	The path to the newly created file. In the case of the tarball, it will 
	contain the private key, certificate and the CA cert, the pkcs12 will 
	contain all three bundled in a .p12 file.  
	"""	
	outpath = out_path()

	if out == 'pkcs12':
		pkcs12 = create_pkcs12( key, cert )
		outpath = "{}.p12".format( outpath )
		with open( outpath, 'bw' ) as fd:
			fd.write( pkcs12 )

	elif out == 'tar.gz' or out == 'gzip' :
		temp_dir = "/tmp/__tmp__/"
		outpath += ".tar.gz"
		_check_call([ "mkdir", temp_dir ])
		_check_call([ "cp", IPSEC_D_CACERTS + CA_CERT, temp_dir ])
		dump_cert(cert, "", temp_dir)
		dump_key(key, "", temp_dir)
		_check_call(["tar", "-czpf", outpath, temp_dir])
		_check_call(["rm", "-Rf", temp_dir ])

	else:
		outpath = ""
		 
	return outpath 


def out_path():
	"""
	@return 
	A file path to write either the tarball or the pkcs12 file. Simply creates a name with a
	random number between zero and 1 million and checks to make sure that it does not 
	exist already in the /home/ubuntu/ directory (where the files are placed). 
	"""
	_exists = False
	while not _exists :
		_rnum = str( randint( 0, 1000000 ) )
		if ( exists("{}{}.tar.gz".format(EXPORT_DIR, _rnum) ) or
			exists("{}{}.p12".format(EXPORT_DIR, _rnum ) ) ):
			continue
		else:
			_exists = True
	return (EXPORT_DIR + _rnum)
