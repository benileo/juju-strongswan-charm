
from charmhelpers.core import hookenv
from strongswan.util import (
	_check_call, 
	apt_install, 
	get_tarball, 
	configure_install
)
from strongswan.constants import (
	PYOPENSSL_DEPENDENCIES, 
	BUILD_DEPENDENCIES,
	PIP_DEPENDENCIES,
	UPSTREAM_BUILD_DEPENDENCIES, 
	STRONGSWAN_GIT_REPO
)

def install_strongswan_archives():
	"""
	@params None
	@return None
	@description Installs strongswan from the Ubuntu Archives. Runs
	apt-get update, apt-get install. 
	"""
	hookenv.log("Installing Strongswan from the ubuntu archives", level=hookenv.INFO )
	apt_install(['strongswan'], apt_update=False)
	
	
def install_strongswan_version( version ):
	"""
	@params The version number of Strongswan to install. Special value is 'latest'
	@return None
	@description: Installs Strongswan from the tarballs posted by StrongSWan 
	maintainers. Unpacks the tarball and configures. Additional config options
	can be passed as an option in the config file (config_options) 
	"""
	apt_install(BUILD_DEPENDENCIES, apt_update=False)
	
	#dl and unpack tarball into tmp directory
	_check_call(["tar", "-xzf", get_tarball(version), "--directory", "/tmp/" ] , fatal=True )

	#get the base dir path #todo make sure no strongswan dir already exists here....
	if version.upper() == "LATEST":
		cmd = "ls -d /tmp/*strongswan*/"
		base_dir = _check_call(cmd, shell=True, check_output=True ).decode('utf-8').split('\n')[0]
	else:
		base_dir = '/tmp/strongswan-{}/'.format(version)
	
	# configure and install 
	configure_install(base_dir)


def install_dep():
	"""
	@params None
	@return None
	@description Installs the PyOpenSSL Dependencies and Python-Pip then installs
	python-iptables and PyOpenSSL into Python 3 installation
	"""
	hookenv.log("Installing dependencies" , level=hookenv.INFO )
	apt_install( PYOPENSSL_DEPENDENCIES )
	for dep in PIP_DEPENDENCIES :
		_check_call( [ "pip3", "install" , dep ] , fatal=True, quiet=True )




# install strongswan from github
def install_strongswan_upstream( repository ):
	"""
	@params None
	@return None
	@description
	Installs Strongswan from the Git repository. Extra dependencies are needed to do so, 
	including git. The install process is the same except autogen.sh must be ran first.
	"""
	hookenv.log("Installing Strongswan from the upstream Git repo: {}".format(
		repository), level=hookenv.INFO)
	_check_call(["rm", "-Rf", "/tmp/strongswan"], log_cmd=False, quiet=True )
	build_dir = "/tmp/strongswan"
	apt_install( BUILD_DEPENDENCIES + UPSTREAM_BUILD_DEPENDENCIES , apt_update=False)
	_check_call(["git", "clone", repository, build_dir ])
	_check_call("cd {}; ./autogen.sh".format(build_dir) , shell=True, quiet=True, fatal=True)
	configure_install(build_dir)
