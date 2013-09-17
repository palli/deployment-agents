Deployment scripts for Jan Stembera
===================================

This directory contains scripts and utilities made for Jan Stembera. They are wrappers around okconfig install agent
and network scan features, modified so that output is json and input meets Jan's needs.

Files in this directory
=======================

* install_nagios_agent  - Installs NRPE and the typical okconfig plugins on a remote RHEL/Centos 6 server
* network_scan          - Ping scans a network, and returns in json format discovered hosts


Prerequisites
=============

The nagios server will need the following dependencies:

* Fully functional RHEL6 or Centos6 server
* okconfig
* pynag
* nagios-plugins-fping


Additionally the okconfig rpm has the following dependencies which should be automatically installed
via yum:
```
Requires: pynag python-paramiko winexe
Requires: nagios nagios-plugins-nrpe  nagios-plugins-ping nagios-plugins-ssh
Requires: nagios-okplugin-apc nagios-okplugin-brocade nagios-okplugin-mailblacklist
Requires: nagios-okplugin-check_disks nagios-okplugin-check_time nagios-plugins-fping
```

Install instructions
====================

The following instructions will show how to get the software up and running.

```
# Install the OK repositories which contain okconfig
rpm -ihv http://opensource.is/repo/ok-release.rpm
yum install okconfig

# If not using standard nagios paths (for example if using icinga) you need to
# edit okconfig.conf so that it points to your icinga.cfg
vim /etc/okconfig.conf

# Go to a directory of your choice and download the latest set of scripts
# from github
yum install -y git
cd /opt
git clone https://github.com/palli/deployment-agents
```

Deploying a nagios agent to a remote server
===========================================
To deploy the NRPE agent to a remote server, the nagios server will need ssh root access to the remote server. The
agent supports both logging in via ssh key or via password authentication.

After the agent has been installed, the access needed from the nagios server varies, but typically the nagios server needs
at the very least access on port 5666 so it can talk with the NRPE agent.

When the deploy script runs it will log into the remote server and execute a custom shell script designed to install NRPE
agent and configure it so it is compatible with the default okconfig linux package. The shell script can be reviewed here:
https://github.com/opinkerfi/okconfig/blob/master/usr/share/okconfig/client/linux/install_okagent.sh

install_nagios_agent usage
==========================
Here are all the valid arguments to install_nagios_agent:

```
s$ ./install_nagios_agent.py --help
Usage: ./install_nagios_agent.py x01=USERNAME x02=PASSWORD x03=? x04=REMOTE_HOST

x01: Username used to log into remote server
x02: Password used to log into remote server
x03: Not used
x04: Hostname or IP Address of remote host to deploy on
```

Here is an example usage of the install_nagios_agent script

```
bash # ./install_nagios_agent x01=root x02=root_password x03=xxx x04=localhost
{
  'success': true,
  'msg': 'Client successfully installed'
}
```

In the case of a failure it will return:
```
{
  'success': false,
  'msg': 'An error message saying that something went wrong'
}
```

network_scan usage
==================

Here are all the valid arguments for network_scan:
```
$ ./network_scan.py --help
Usage: ./network_scan.py x01=network x02=netmask x06=cust_id x07=option

Example: ./network_scan.py x01=127.0.0.0 x02=25 x06=customer1

x01: Network to scan (example 10.0.0.0)
x02: Netmask (example: 24)
x06: Arbitrary string, not used by the program
x07: Option to pass into network scan, not used by the program
```

Here is an example usage of the network scan script scanning 127.0.0.1

```
$ ./network_scan.py x01=127.0.0.1 x02=32 x06=customer_id x07=options
{
    "message": "network scan completed",
    "scan_results": [
        {
            "nrpe": "NRPE running but does not respond to us",
            "hostname": "localhost.localdomain",
            "port80": "yes",
            "platform": "Linux",
            "cust_id": "customer_id",
            "ipaddress": "127.0.0.1",
            "options": "options",
            "ismonitored": true
        }
    ],
    "success": true
}
```

When no hosts are found the network scan looks like this
```
$ ./network_scan.py x01=5.5.5.5 x02=32 x06=customer_id x07=options
{
    "message": "network scan completed",
    "scan_results": [],
    "success": true
}
```

On invalid input, the script will return success=False with indicators in the message field as to what the problem might be:

```
$ ./network_scan.py x01=127.0.0.1 x02=invalid x06=customer_id x07=options
{
    "message": "Error running fping -t 50 -i 10 -a  -g 127.0.0.1/invalid: \nUsage: fping [options] [targets...]\n   -a         show targets that are alive\n   -A         show targets by address\n   -b n       amount of ping data to send, in bytes (default 68)\n   -B f       set exponential backoff factor to f\n   -c n       count of pings to send to each target (default 1)\n   -C n       same as -c, report results in verbose format\n   -e         show elapsed time on return packets\n   -f file    read list of targets from a file ( - means stdin) (only if no -g specified)\n   -g         generate target list (only if no -f specified)\n                (specify the start and end IP in the target list, or supply a IP netmask)\n                (ex. fping -g 192.168.1.0 192.168.1.255 or fping -g 192.168.1.0/24)\n   -i n       interval between sending ping packets (in millisec) (default 10)\n   -l         loop sending pings forever\n   -m         ping multiple interfaces on target host\n   -n         show targets by name (-d is equivalent)\n   -p n       interval between ping packets to one target (in millisec)\n                (in looping and counting modes, default 1000)\n   -q         quiet (don't show per-target/per-ping results)\n   -Q n       same as -q, but show summary every n seconds\n   -r n       number of retries (default 3)\n   -s         print final stats\n   -S addr    set source address\n   -t n       individual target initial timeout (in millisec) (default 50)\n   -T n       set select timeout (default 10)\n   -u         show targets that are unreachable\n   -v         show version\n   targets    list of targets to check (if no -f specified)\n\n",
    "error_type": "<type 'exceptions.Exception'>",
    "success": false
}

```
