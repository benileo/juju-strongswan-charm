
from strongswan.constants import IPSEC_CONF

def open_ipsec_conf():
	return open(IPSEC_CONF, "rw")

def close_ipsec.conf(fd):
	fd.close()

