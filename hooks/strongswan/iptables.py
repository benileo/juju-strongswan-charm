
from charmhelpers.core import hookenv
from strongswan.constants import * 
from strongswan.util import make_rule, _check_call 


# update the rule chains and then save the rules
def configure_iptables():
	_filter()
	_nat()
	_check_call([IPTABLES_SAVE] , quiet=True,
			message="iptables-save has failed in non-fatal mode")



# update filter chain
def _filter():
	hookenv.log("Configuring iptables firewall for IPsec", level=hookenv.INFO )

	# We should always have loopback available
	make_rule(['-i', 'lo', '-j', ACCEPT], INPUT, INSERT)
	make_rule(['-o', 'lo', '-j', ACCEPT], OUTPUT, INSERT)

	# allow IKE and NAT-T Inbound and Outbound
	make_rule(ALLOW_IKE, INPUT, INSERT)
	make_rule(ALLOW_IKE, OUTPUT, INSERT )
	make_rule(ALLOW_NAT_T, INPUT, INSERT)
	make_rule(ALLOW_NAT_T, OUTPUT, INSERT)

	# allow either AH or ESP inbound and outbound
	if CONFIG.get("ipsec_protocol") == "esp":
		make_rule(ALLOW_ESP, INPUT, INSERT)
		make_rule(ALLOW_AH , INPUT, DELETE )
		make_rule(ALLOW_ESP, OUTPUT, INSERT)
		make_rule(ALLOW_AH , OUTPUT, DELETE )
	else:
		make_rule(ALLOW_AH, INPUT, INSERT )
		make_rule(ALLOW_ESP, INPUT, DELETE )
		make_rule(ALLOW_AH, OUTPUT, INSERT )
		make_rule(ALLOW_ESP, OUTPUT, DELETE )

	# allow ssh inbound and outbound 
	make_rule(ALLOW_SSH_IN, INPUT, APPEND)
	make_rule(ALLOW_SSH_OUT, OUTPUT, APPEND)

	# all DNS gets through the firewall
	if not CONFIG.get("public_network"):
		make_rule(ALLOW_DNS_UDP_IN, INPUT, APPEND)
		make_rule(ALLOW_DNS_UDP_OUT, OUTPUT, APPEND)
		make_rule(ALLOW_DNS_TCP_IN, INPUT, APPEND)
		make_rule(ALLOW_DNS_TCP_OUT, OUTPUT, APPEND)

	# DHCP 
	make_rule(ALLOW_DHCP, INPUT, APPEND)
	make_rule(ALLOW_DHCP, OUTPUT, APPEND)

	# allow all established outbound connections
	# if NO, we must allow apt-ports for install and updates
	if CONFIG.get("public_network"):
		make_rule(ALLOW_EST_CONN_IN, INPUT, APPEND)
		make_rule(ALLOW_EST_CONN_OUT, OUTPUT, APPEND)
		make_rule(ALLOW_APT_IN, INPUT, DELETE)
		make_rule(ALLOW_APT_OUT, OUTPUT, DELETE)
	else:
		make_rule(ALLOW_EST_CONN_IN, INPUT, DELETE)
		make_rule(ALLOW_EST_CONN_OUT, OUTPUT, DELETE)
		make_rule(ALLOW_APT_IN, INPUT, APPEND)
		make_rule(ALLOW_APT_OUT, OUTPUT, APPEND)

	#set default policy to DROP for filter tables.
	hookenv.log("Setting default policy to drop for all filter rule chains", level=hookenv.INFO)
	_check_call( [IPTABLES, POLICY, FORWARD , DROP ], log_cmd=False )
	_check_call( [IPTABLES, POLICY, INPUT , DROP ], log_cmd=False )
	_check_call( [IPTABLES, POLICY, OUTPUT , DROP ] log_cmd=False )


def _nat():
	pass
