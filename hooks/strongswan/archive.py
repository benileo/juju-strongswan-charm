
from charmhelpers.core import hookenv
from time import sleep
from strongswan.constants import PYOPENSSL_DEPENDENCIES, CONFIG
from strongswan.util import _check_call, run_apt_command
from urllib.request import urlretrieve


# installs the strongswan packages from the archives.
def install_strongswan_archives():
	hookenv.log("Installing Strongswan from the archives" , level=hookenv.INFO )
	run_apt_command([], apt_cmd='update' )
	run_apt_command(['strongswan'], apt_cmd='install', timeout=300 )
	
	
# installs strongswan from the most recent strongswan tarball
def install_strongswan_version( version ):
	pass


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
