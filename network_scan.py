#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013, Pall Sigurdsson <palli@opensource.is>
#
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This script will is a wrapper around "okconfig network scan" and will print
# to stdout the results of network scan in a json format

# This script was made for Jan Stembera.

import okconfig.network_scan
import simplejson as json
import sys
import paramiko

# map x0* arguments to something meaningful
argmap = {}
argmap['x01'] = 'network'
argmap['x02'] = 'netmask'
argmap['x06'] = 'cust_id'
argmap['x07'] = 'options'

def main():
    """ Main function of the program """
    arguments = parse_arguments()
    network = arguments.get('network') or error('network was not provided')
    netmask = arguments.get('netmask') or error('netmask was not provided')
    cust_id = arguments.get('cust_id') or None
    options = arguments.get('options') or None
    hosts = okconfig.network_scan.get_all_hosts("%s/%s" % (network, netmask))
    result = []
    for i in hosts:
        host = {}
        result.append(host)
        i.check()
        host['ipaddress'] = i.ipaddress
        host['hostname'] = i.hostname
        host['ismonitored'] = i.ismonitored
        host['platform'] = i.platform
        host['nrpe'] = i.nrpe
        host['port80'] = i.port80
        host['cust_id'] = cust_id
        host['options'] = options

    success("network scan completed", json_data={'scan_results':result})


def error(message, json_data=None):
    """ Prints out a json error to the screen and exits the program """
    print_json(False, message, json_data)
    sys.exit(1)


def success(message, json_data=None):
    """ Prints out a json message and exits the program """
    print_json(True, message, json_data)
    sys.exit(0)


def print_json(success, message, json_data=None):
    """ converts success and message to json dictionary and prints to stdout """
    if not json_data:
        json_data = {}
    json_data['success'] = success
    json_data['message'] = message
    print json.dumps(json_data, indent=4)


def parse_arguments(*args):
    """ Parse command line arguments

        Arguments:
            *args : a list of arguments, usually sys.argv
    """
    result = {}  # Dictionary containing the arguments
    if not args:
        args = sys.argv[1:]
    if '--help' in args:
        usage()
    for arg in args:
        if not '=' in arg:
            raise ValueError("Invalid argument: %s" % arg)

        key, value = arg.split('=', 1)
        result[key] = value
        if key in argmap:
            key = argmap[key]
            result[key] = value
    return result


def usage():
    """ Print usage of the program and exit """
    print "Usage: %s x01=network x02=netmask x06=cust_id x07=option"  % sys.argv[0]
    print ""
    print "Example: %s x01=127.0.0.0 x02=25 x06=customer1" % sys.argv[0]
    print """
x01: Network to scan (example 10.0.0.0)
x02: Netmask (example: 24)
x06: Arbitrary string, not used by the program
x07: Option to pass into network scan, not used by the program
    """
    sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except paramiko.AuthenticationException:
        error("Authentication failed")
    except Exception, e:
        error_type = str(type(e))
        error(str(e), json_data={'error_type': error_type})