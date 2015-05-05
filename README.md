# Overview

This charm provides [StrongSwan](http://www.strongswan.org). 

# Installation of StrongSwan

1. Install StrongSwan from the Ubuntu archives (this is the default). This will install all necessary packages needed for your particular configuration:

        juju deploy cs:~/jammin-irving/trusty/strongswan

2. Install StrongSwan from [download.strongswan.org](http://download.strongswan.org). This allows you to install any released version of StrongSwan. Use the source option in config.yaml to specify the version of strongswan that you want installed.

        juju deploy cs:~/jammin-irving/trusty/strongswan --config myconfig.yaml
Where myconfig.yaml:
        
        strongswan:
          source: 5.2.0
Or if you want the latest version, change myconfig.yaml to:

        strongswan:
          source: latest

3. Install and build StrongSwan from source [git.strongswan.org](git.strongswan.org):

        juju deploy cs:~/jammin-irving --config myconfig.yaml
Where myconfig.yaml:
        
        strongswan:
          source: upstream

# Configuration

[Configuration Options](https://wiki.strongswan.org/projects/strongswan/wiki/Autoconf)

# Contact Information

- [Strongswan Wiki](https://wiki.strongswan.org)
- [Strongswan Releases](http://downloads.strongswan.org)
- Contact Ben Irving (jammin.irving@gmail.com) for bugs or suggestions.