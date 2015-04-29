
from re import match
from charmhelpers.core import hookenv
from strongswan.errors import InvalidVersion
from strongswan.util import (
	_check_call, 
	apt_install, 
	get_tarball, 
	configure_install
)
from strongswan.constants import (
	APT_DEPENDENCIES, 
	BUILD_DEPENDENCIES,
	PIP_DEPENDENCIES
)

def install_strongswan_archives():
	"""
	@params None
	@return None
	@description Installs strongswan from the Ubuntu Archives. Runs
	apt-get update, apt-get install. 
	"""
	hookenv.log("Installing Strongswan from the ubuntu archives", level=hookenv.INFO )
	apt_install(['strongswan'])
	
	
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
	if(	version.upper() != 'LATEST' and not match(r'^[1-9]\.[0-9]\.[0-9]$' , version ) ): 
		raise InvalidVersion("Version must be in the format 5.3.1 or 'latest'")
	
	apt_install(BUILD_DEPENDENCIES)
	
	#dl and unpack tarball into tmp directory
	_check_call(["tar", "-xzf", get_tarball(version), "--directory", "/tmp/" ] , fatal=True )

	#get the base dir path
	if version.upper() == "LATEST":
		cmd = "ls -d /tmp/*strongswan*/"
		base_dir = _check_call(cmd, shell=True, check_output=True ).decode('utf-8').split('\n')[0]
	else:
		base_dir = '/tmp/strongswan-{}/'.format(version)
	
	#configure install 
	configure_install(base_dir)

	#install
	_check_call( 'cd {}; make'.format(base_dir), shell=True, fatal=True, timeout=300, quiet=True )
	_check_call( 'cd {}; make install'.format(base_dir), shell=True, fatal=True, timeout=300, quiet=True )

	# register strongswan as a service 
	_check_call(['cp', '../scripts/strongswan.conf', '/etc/init/strongswan.conf' ])


def install_dep():
	"""
	@params None
	@return None
	@description Installs the PyOpenSSL Dependencies and Python-Pip then installs
	python-iptables and PyOpenSSL into Python 3 installation
	"""
	hookenv.log("Installing dependencies" , level=hookenv.INFO )
	apt_install( APT_DEPENDENCIES )
	for dep in PIP_DEPENDENCIES :
		_check_call( [ "pip3", "install" , dep ] , fatal=True, quiet=True )




# install strongswan from github
def install_strongswan_upstream():
	"""
	TODO
	"""
	pass
