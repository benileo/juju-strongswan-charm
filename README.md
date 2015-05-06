# Overview

This charm provides [StrongSwan](http://www.strongswan.org). This charm will install StrongSwan, do 'basic' VPN configurations and provide actions to create and manage x509 certificates. 

# StrongSwan Install Options

1. Install StrongSwan from the Ubuntu archives (this is the default). This will install all necessary packages needed for your particular configuration:

        juju deploy cs:~/jammin-irving/trusty/strongswan

2. Install StrongSwan from [download.strongswan.org](http://download.strongswan.org). This repository contains all releases of strongSwan IPsec project. Use the source option in config.yaml to specify the version of strongswan that you want installed.

        juju deploy cs:~/jammin-irving/trusty/strongswan --config myconfig.yaml
Where myconfig.yaml:
        
        strongswan:
          source: 5.2.0
Or if you want the latest version, change myconfig.yaml to:

        strongswan:
          source: latest

3. Install and build StrongSwan from source, pass URL of git repository. :

        juju deploy cs:~/jammin-irving/trusty/strongswan --config myconfig.yaml
Where myconfig.yaml:
        
        strongswan:
          source: https://github.com/strongswan/strongswan.git
          verbose_logging: true


###Note: 
For install options 2 and 3, refer to [https://wiki.strongswan.org/projects/strongswan/wiki/Autoconf](https://wiki.strongswan.org/projects/strongswan/wiki/Autoconf) if you need to specify additional configuration options, as this must be done before building StrongSwan. Add the options as a comma separated list (option dependencies will be installed automatically by the charm).

    strongswan:
      source: latest
      configuration: --enable-android,--enable-mysql,--with-charon-udp-port=80,--with-charon-natt-port=443
# Configuration



# Contact Information

- [Strongswan Wiki](https://wiki.strongswan.org)
- [Strongswan Releases](http://downloads.strongswan.org)
- Contact Ben Irving (jammin.irving@gmail.com) for bugs or suggestions.