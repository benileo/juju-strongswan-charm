
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
	CA_KEY,
	CA_CERT,
	SERVER_CERT_NAME,
	EXPORT_DIR
)

def load_ca_cert():
	"""
	Loads the CA Cert from /etc/ipsec.d/cacerts/caCert.pem
	"""
	with open("{0}{1}".format(IPSEC_D_CACERTS, CA_CERT ), 'br' ) as fd:
		cacert = crypto.load_certificate( crypto.FILETYPE_PEM, fd.read() )
	return cacert

def load_ca_key():
	"""
	Loads the CA Key from /etc/ipsec.d/private/caKey.pem
	""" 
	with open("{0}{1}".format(IPSEC_D_PRIVATE, CA_KEY ) , 'br' ) as fd:
		cakey = crypto.load_privatekey( crypto.FILETYPE_PEM, fd.read() )
	return cakey

def dump_ca_key(k):
	"""
	Writes the CA key to /etc/ipsec.d/private/caKey.pem
	:param k: instance of crypto.PKey object
	"""
	with open("{0}{1}".format(IPSEC_D_PRIVATE, CA_KEY ), 'bw') as fd:
		fd.write(crypto.dump_privatekey( crypto.FILETYPE_PEM, k ) )

def dump_ca_cert(c):
	"""
	Writes the CA cert to /etc/ipsec.d/cacerts/caCert.pem
	:param c: instance of crypto.X509() object
	"""
	with open("{0}{1}".format(IPSEC_D_CACERTS, CA_CERT ), 'bw' ) as fd:
		fd.write(crypto.dump_certificate( crypto.FILETYPE_PEM, c ) )

def dump_key(pkey, keyname, directory):
	"""
	Writes the key to a given filepath
	
	:param pkey: an instance of crypto.PKey()
	:param keyname: the name of the file will be (keyname)Key.pem
	:param directory: directory to write key 
	"""
	with open("{0}{1}Key.pem".format(directory, keyname ), 'bw' ) as fd :
		fd.write(crypto.dump_privatekey( crypto.FILETYPE_PEM, pkey ) )

def dump_cert(cert, certname, directory):
	"""
	Writes the cert to a given filepath

	:param pkey: an instance of crypto.X509()
	:param keyname: the name of the file will be (certname)Cert.pem
	:param directory: directory to write certificate
	"""
	with open("{0}{1}Cert.pem".format( directory , certname ) , 'bw' ) as fd :
		fd.write(crypto.dump_certificate( crypto.FILETYPE_PEM, cert ) )

def create_key_pair( keytype, keysize ):
	"""
	Create a public/private key pair using RSA/DSA

	:param keytype: crypto.TYPE_RSA or crypto_TYPE_DSA
	:param keysize: keysize in bytes
	
	:return: an instance of PKey 
	"""
	pkey = crypto.PKey()
	pkey.generate_key( keytype, keysize )
	return pkey


def create_cert_request( pkey, subject, digest='sha1' ):
	"""
	Creates a Certificate Signing Request (CSR)
	
	:param	pkey: instance of crypto.PKey()
	:param subject: the subject of the certificate in a python dictionary
	:param digest: the digest to use
	
	:return: crypto.X509Req() object
	"""
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
	"""
	Creates an X509() certificate
	
	:param req: an instance of crypto.X509Req()
	:param issuerCert: the CA cert, an instance of crypto.X509()
	:param issuerKey: the CA key, an instance of crypto.PKey()
	:param lifetime: time from now that the certificate is valid
	:param digest: digest used
	
	:return: signed certificate, an instance of crypto.X509()
	"""
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
	"""
	Creates a PKCS12 file format
	
	:param pkey: an instance of PKey()
	:param cert: an instance of X509()
	
	:return: PKCS12 object as a string
	"""
	p12 = crypto.PKCS12()
	p12.set_certificate(cert)
	p12.set_privatekey(pkey)
	cacert = load_ca_cert()
	p12.set_ca_certificates([cacert])
	return ( p12.export() )


def create_root_cert(  
		subject,
		lifetime,
		keysize,
		digest='sha1' 
	):
	"""
	Create your own self-signed certificate
	"""
	
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
	dump_key(k, SERVER_CERT_NAME, IPSEC_D_PRIVATE)
	dump_cert(c, SERVER_CERT_NAME, IPSEC_D_CERTS)

def create_host_cert(
		subject,
		lifetime,
		keysize,
		out,
		digest='sha1'
	):
	"""
	Creates a host/user certificate
	"""
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
	"""
	:return: a unique serial number
	"""
	_time = str( ceil( time() ) )
	_rnum = str( randint( 0, 2**100 ) )
	_ser = _rnum + _time
	if ( len(_ser) % 2 ) != 0 :
		_ser += '8' 
	return int(_ser)


def create_outfile( out, key, cert ):
	"""
	Creates a file archive in either .p12 or .tar.gz format

	:param out: the type of output, valid values are tar.gz or pkcs12
	:param key: instance of PKey()  
	:param cert: instance of X509() 
	
	:return: path to archive file 
	"""	
	outpath = out_path()

	if out == 'pkcs12':
		pkcs12 = create_pkcs12( key, cert )
		outpath = "{}.p12".format( outpath )
		with open( outpath, 'bw' ) as fd:
			fd.write( pkcs12 )

	elif out == 'tar.gz' or out == 'gzip' :
		temp_dir = "/tmp/certs/"
		outpath += ".tar.gz"
		_check_call([ "mkdir", temp_dir ])
		_check_call([ "cp", IPSEC_D_CACERTS + CA_CERT, temp_dir ])
		dump_cert(cert, "", temp_dir)
		dump_key(key, "", temp_dir)
		cmd = """cd /tmp/; tar -czpf {} {}""".format( outpath, "certs" )
		_check_call( cmd , shell=True )
		_check_call(["rm", "-Rf", temp_dir ])

	else:
		outpath = ""
		 
	return outpath 


def out_path():
	"""
	:return: a unique output path in the /home/ubuntu directory 
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
