
import re
from os.path import exists
from charmhelpers.core import hookenv
from strongswan.errors import ExportDirDoesNotExist



# First we need the config
CONFIG = hookenv.config()

# Raise an exception if /home/ubuntu doesn't exist.
if not exists('/home/ubuntu/'):
	raise ExportDirDoesNotExist("/home/ubuntu does not exist")

# Set the IKE port - make sure we are not running on a non default port
match = re.match( r'^(.*)(--with-charon-udp-port=[0-9]{1,5})(.*)$', CONFIG.get("configuration") )
if match:
	IKE = match.groups()[1].split('=')[1]
else:
	IKE = "500"

# Same thing for NAT-T
match = re.match( r'^(.*)(--with-charon-natt-port=[0-9]{1,5})(.*)$', CONFIG.get("configuration") )
if match: 
	NAT_T = match.groups()[1].split('=')[1]
else:
	NAT_T = "4500"


EXPORT_DIR 	= '/home/ubuntu/'
DL_BASE_URL = "http://download.strongswan.org/"
DPKG_LOCK_ERROR = 100
IPV4_FORWARD = "net.ipv4.ip_forward"
IPV6_FORWARD = "net.ipv6.conf.all.forwarding"
SYSCTL_PATH = "/etc/sysctl.conf"
IPSEC_D_PRIVATE = '/etc/ipsec.d/private/'
IPSEC_D_CACERTS = '/etc/ipsec.d/cacerts/'
IPSEC_D_CERTS = '/etc/ipsec.d/certs/'
#IPSEC_D_CRLS = '/etc/ipsec.d/crls/'
CA_KEY = 'caKey.pem'
CA_CERT	= 'caCert.pem'
SERVER_CERT_NAME = 'SERVER'
INSERT = 'INSERT'
APPEND = 'APPEND'
ACCEPT = "ACCEPT"


# these may change over time.
PYOPENSSL_DEPENDENCIES = [
	"build-essential",
	"libssl-dev",
	"libffi-dev",
	"python-dev",
	"python3-pip"
]
PIP_DEPENDENCIES = [
	"python-iptables",
	"pyOpenSSL",
	#cryptography
]
BUILD_DEPENDENCIES = [
	"libgmp3-dev",
	"gcc",
	"make"
]
UPSTREAM_BUILD_DEPENDENCIES = [
	"automake",
	"autoconf",
	"git-core",
	"libtool",
	"pkg-config",
	"gettext",
	"perl",
	"python",
	"flex",
	"byacc",
	"bison",
	"gperf"
]
PLUGIN_DEPENDENCIES = {
	"--enable-eap-sim-pcsc" : ["libpcsclite-dev"],
	"--enable-gcrypt" : ["libgcrypt11-dev"],
	"--enable-ldap" : ["libldap2-dev"],
	"--enable-mysql" : ["libmysqlclient-dev"],
	"--enable-sql" : ["libmysqlclient-dev"],	
	"--enable-sqlite" : ["libsqlite3-dev"],
	"--enable-soup" : ["libsoup2.4-dev"],
	"--enable-smp" : ["libxml2"],
	"--enable-tnccs-11" : ["libxml2"],
	"--enable-curl" : ["libcurl"]
}
