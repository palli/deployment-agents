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

# This script will is a wrapper around "okconfig install" and will
# install NRPE on a remote server and minimal amount of plugins
# to satisfy the a typical "okconfig" client.

# This script was made for Jan Stembera.

import okconfig
import simplejson as json
import sys
import paramiko

# map x0* arguments to something meaningful
argmap = {}
argmap['x01'] = 'username'
argmap['x02'] = 'password'
argmap['x03'] = 'not used'
argmap['x04'] = 'host'


def main():
    """ Main function of the program """
    arguments = parse_arguments()
    remote_host = arguments.get('host') or usage('remote host was not provided')
    username = arguments.get('username') or usage('username was not provided')
    password = arguments.get('password') or usage('password was not provided')
    status, stdout, stderr = okconfig.install_okagent(
        remote_host=remote_host,
        username=username,
        password=password,
    )
    if status == 0:
        success(stdout)
    else:
        error(stdout)


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


def usage(message=None):
    """ Print usage of the program and exit """
    if message is not None:
        print message
        print ""

    print "Usage: %s x01=USERNAME x02=PASSWORD x03=? x04=REMOTE_HOST" % sys.argv[0]
    print """
x01: Username used to log into remote server
x02: Password used to log into remote server
x03: Not used
x04: Hostname or IP Address of remote host to deploy on
    """
    sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except paramiko.AuthenticationException:
        error("Authentication failed")
    except Exception, e:
        error(str(e), json_data={'error_type': type(e)})