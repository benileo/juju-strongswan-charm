#!/usr/bin/env python3

import re
import subprocess as sp
from charmhelpers.core import hookenv

# TO DO make this more organized and consistent with the rest of the code

# Make a copy of the /etc/hosts file
def cp_hosts_file():
	cmd = ['cp', '/etc/hosts', '/etc/hosts.original' ]
	sp.call(cmd)
	hookenv.log("Copy of hosts file created: /etc/hosts.original", level=hookenv.INFO )


# flush hosts file of archive/security.ubuntu.com
# TO DO check modification date of file first.......
def flush_hosts_file():
	hookenv.log('Flushing /etc/hosts of entries added during install', level=hookenv.INFO )
	update_hosts_file( '#1.2.3.4', 'archive.ubuntu.com' )
	update_hosts_file( '#1.2.3.4', 'security.ubuntu.com' )


# updates the hosts file with an ip_addr hostname  
def update_hosts_file( ip_addr , hostname ):
	hookenv.log("Adding {0}\t{1} to /etc/hosts".format(ip_addr, hostname ), level=hookenv.INFO )

	aliased_hosts = []
	output_string = ""

	# open the hosts file
	# create string to write to the hosts file
	# add the corresponding entry if it does not exist already.
	with open('/etc/hosts' , 'r') as hosts_file :
		for line in hosts_file:
			elem = re.findall('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\s\S*' , line )
			if elem:
				if elem[0].split()[1] == hostname:
					output_string += "{0}\t{1}\n".format(ip_addr, hostname)
				else:
					output_string += line
				aliased_hosts.append(elem[0].split()[1])
			else:
				output_string += line
		if hostname not in aliased_hosts:
			output_string += "{0}\t{1}\n".format(ip_addr, hostname)

	# write the corresponding changes to the file
	with open('/etc/hosts', 'w') as hosts_file:
		hosts_file.write(output_string)

# returns a list with the result of dig archive.ubuntu.com			
def get_archive_ip_addrs():
	hookenv.log("Running dig command to obtain archive IP addresses", level=hookenv.INFO )
	ip_list = []
	dig = sp.check_output(['dig', 'archive.ubuntu.com'])
	dig = dig.decode('utf-8').split('\n')
	for i in dig:
		i = i.split('\t')
		if i:
			if i[0] == 'archive.ubuntu.com.' :
				ip_list.append(i[4])
	return ip_list

