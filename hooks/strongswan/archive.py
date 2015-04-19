

from charmhelpers.core import hookenv
from strongswan.util import (
	_check_call, 
	run_apt_command, 
	get_tarball, 
	configure_install
)
from strongswan.constants import (
	PYOPENSSL_DEPENDENCIES, 
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
	hookenv.log("Installing Strongswan from http://download.strongswan.org. Version: {}".format( 
		version ) , level=hookenv.INFO )

	#install dependencies
	run_apt_command([], apt_cmd='update' )
	run_apt_command(BUILD_DEPENDENCIES, apt_cmd='install', timeout=300 )
	
	#dl and unpack tarball into tmp directory
	_check_call(["tar", "-xzf", get_tarball(version),
		"--directory", "/tmp/" ], fatal=True )

	#configure
	base_dir = (_check_call( "ls -d /tmp/*strongswan*/", shell=True, 
		check_output=True ).decode('utf-8').split('\n')[0] ) if version == 'latest' else '/tmp/strongswan-{}/'.format(version)
	configure_install(base_dir)

	#install
	_check_call( 'cd {}; make'.format(base_dir) , shell=True, 
		fatal=True, timeout=300, quiet=True )
	_check_call( 'cd {}; make install'.format(base_dir), shell=True, 
		fatal=True, timeout=300, quiet=True )

	# register strongswan as a service 
	_check_call(['cp', '../scripts/strongswan.conf', '/etc/init/strongswan.conf' ])




# install strongswan from github
def install_strongswan_github():
	pass


# Installs the PyOpenssl Package into Python 3
def install_pyOpenSSL():
	hookenv.log("Installing PyOpenSSL Dependencies" , level=hookenv.INFO )

	#install dependencies
	run_apt_command( PYOPENSSL_DEPENDENCIES, apt_cmd='install', timeout=300 )

	# install into python3 
	_check_call( [ "pip3", "install" , "pyOpenSSL"] , 
		fatal=True, 
		message="Installing pyOpenSSL into Python 3 installation", 
		quiet=True
	)
