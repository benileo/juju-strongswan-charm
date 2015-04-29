
from re import match
from charmhelpers.core import hookenv
from strongswan.errors import InvalidVersion
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

def install_strongswan_archives():
	"""
	@params None
	@return None
	@description Installs strongswan from the Ubuntu Archives. Runs
	apt-get update, apt-get install. 
	"""
	hookenv.log("Installing Strongswan from the ubuntu archives", level=hookenv.INFO )
	run_apt_command([], apt_cmd='update' )
	#determine the packages to install -> based on config TODO
	run_apt_command(['strongswan'], apt_cmd='install', timeout=300 )
	
	
# installs strongswan from the most recent strongswan tarball
def install_strongswan_version( version ):
	"""
	@params The version number of Strongswan to install. Special value is 'latest'
	@return None
	@description: Installs Strongswan from the tarballs posted by StrongSWan 
	maintainers. Unpacks the tarball and configures. Additional config options
	can be passed as an option in the config file (config_options).
	@exception: InvalidVersion `If the version number is not of valid form or 'latest'
	"""
	if(	version.upper() != 'LATEST'  or not re.match(r'^[1-9]\.[0-9]\.[0-9]$' , version ) ): 
		raise InvalidVersion("Version must be in the format 5.3.1 or 'latest'")

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


def install_pyOpenSSL():
	"""
	@params None
	@return None
	@description Installs the PyOpenSSL Dependencies and Python Pip 
	"""
	hookenv.log("Installing PyOpenSSL Dependencies" , level=hookenv.INFO )
	run_apt_command( PYOPENSSL_DEPENDENCIES )
	_check_call( [ "pip3", "install" , "pyOpenSSL"] , fatal=True, quiet=True )




# install strongswan from github
def install_strongswan_upstream():
	"""
	TODO
	"""
	pass