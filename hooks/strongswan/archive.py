
from subprocess import check_output
from charmhelpers.core import hookenv
from time import sleep
from urllib.request import urlretrieve
from hashlib import md5
from strongswan.util import _check_call, run_apt_command
from strongswan.errors import InvalidHashError
from strongswan.constants import (
	PYOPENSSL_DEPENDENCIES, 
	CONFIG,
	DL_BASE_URL,
	BUILD_DEPENDENCIES
)

# installs the strongswan packages from the archives.
def install_strongswan_archives():
	hookenv.log("Installing Strongswan from the archives" , level=hookenv.INFO )

	#update
	run_apt_command([], apt_cmd='update' )

	#determine the packages to install -> based on config
	#TODO

	#install
	run_apt_command(['strongswan'], apt_cmd='install', timeout=300 )
	
	
# installs strongswan from the most recent strongswan tarball
def install_strongswan_version( version ):
	hookenv.log("Installing Strongswan from http://download.strongswan.org\n\tVersion:\n{}".format( 
		version ) , level=hookenv.INFO )

	#install dependencies
	run_apt_command([], apt_cmd='update' )
	run_apt_command(BUILD_DEPENDENCIES, apt_cmd='install', timeout=300 )


	# build urls
	if version == 'latest' :
		tarball = "strongswan.tar.gz"
		md5_hash_file = "strongswan.tar.gz.md5"
	else:
		tarball = "strongswan-{}.tar.gz".format(version)
		md5_hash_file = "strongswan-{}.tar.gz.md5".format(version)
	

	#retrieve urls
	try:
		hookenv.log("Retrieving {}{}".format(DL_BASE_URL, tarball), 
			level=hookenv.INFO)
		urlretrieve( "{}{}".format(DL_BASE_URL, tarball ),
			"/tmp/{}".format(tarball) 
		)
		urlretrieve( "{}{}".format(DL_BASE_URL, md5_hash_file ),
			"/tmp/{}".format(md5_hash_file)
		)
	except Exception as err:
		hookenv.log(err)
		raise


	#check hash
	with open("/tmp/{}".format(md5_hash_file), 'r' ) as fd :
		original_hash = fd.read().split()[0]
	with open("/tmp/{}".format(tarball), 'rb' ) as fd :
		tarball_hash = md5( fd.read() ).hexdigest()
	if original_hash != tarball_hash :
		raise InvalidHashError("Invalid hash of {}".format(tarball) )
	
	#unpack
	cmd = [
		"tar", "-xzf",
		"/tmp/{}".format(tarball),
		"--directory", "/tmp/"
	]
	_check_call(cmd, fatal=True)

	#configure
	# base_dir = '/tmp/strongswan/' if version == 'latest' else '/tmp/strongswan-{}/'.format(version)
	# this is not ideal.... but if we want 'latest'.....
	base_dir = check_output( "ls -d /tmp/*strongswan*/", shell=True ).decode('utf-8').split('\n')[0]
	cmd  = 	(
		'cd {}; '
		'./configure '
		'--prefix=/usr '
		'--sysconfdir=/etc'.format(base_dir)
	)
	_check_call(cmd, shell=True, fatal=True, quiet=True )


	#install
	_check_call( 'cd {}; make'.format(base_dir) , shell=True, fatal=True, quiet=True )
	_check_call( 'cd {}; make install'.format(base_dir), shell=True, fatal=True )




# install strongswan from github
def install_strongswan_github():
	pass


# Installs the PyOpenssl Package into Python 3
def install_pyOpenSSL():
	hookenv.log("Installing PyOpenSSL Dependencies" , level=hookenv.INFO )
	
	#update apt if not done already
	if CONFIG.get("source") != "archives" :
		run_apt_command([], apt_cmd='update')

	#install dependencies
	run_apt_command( PYOPENSSL_DEPENDENCIES, apt_cmd='install', timeout=300 )

	# install into python3 
	_check_call( [ "pip3", "install" , "pyOpenSSL"] , 
		fatal=True, 
		message="Installing pyOpenSSL into Python 3 installation", 
		quiet=True
	)
