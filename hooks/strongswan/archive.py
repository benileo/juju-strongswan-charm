
from charmhelpers.core import hookenv
from strongswan.util import (
	_check_call, 
	apt_install, 
	get_tarball, 
	configure_install
)
from strongswan.constants import ( 
	BUILD_DEPENDENCIES,
	UPSTREAM_BUILD_DEPENDENCIES
)

def install_strongswan_archives():
	"""
	Install Strongswan and desired plugins from the ubuntu archives 
	"""
	hookenv.log("Installing Strongswan from the ubuntu archives", level=hookenv.INFO )
	apt_install(['strongswan'], apt_update=False)
	
	
def install_strongswan_version( version ):
	"""
	Install Strongswan from a particular release
	:param version: either latest or a release number 
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

def install_strongswan_upstream( repository ):
	"""
	Build and install Strongswan from source
	:param repository: a git repository URL
	"""
	hookenv.log("Installing Strongswan from the upstream Git repo: {}".format(
		repository), level=hookenv.INFO)
	_check_call(["rm", "-Rf", "/tmp/strongswan"], log_cmd=False, quiet=True )
	build_dir = "/tmp/strongswan"
	apt_install( BUILD_DEPENDENCIES + UPSTREAM_BUILD_DEPENDENCIES , apt_update=False)
	_check_call(["git", "clone", repository, build_dir ])
	_check_call("cd {}; ./autogen.sh".format(build_dir) , shell=True, quiet=True, fatal=True)
	configure_install(build_dir)
