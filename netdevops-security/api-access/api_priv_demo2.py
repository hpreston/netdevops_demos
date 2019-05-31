#! /usr/bin/env python
"""Script to add new loopback interface using NETCONF

This script will retrieve information from a device.

Copyright (c) 2018 Cisco and/or its affiliates.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
from ncclient import manager
from ncclient.operations.rpc import RPCError
import xmltodict
from getpass import getpass

# Get interface details from env_vars and user prompt
device = {
    "address": "ios-xe-mgmt-latest.cisco.com",
    "username": input("Network Username?\n"),
    "password": getpass("Network Password?\n"),
    "netconf_port": 10000,
}

# Make sure all details available
if None in device.values():
    raise Exception("Missing key piece of data to connect to device")

# XML payload template to add loopback
config_data = """
<config>
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
      <interface>
        <name>{int_name}</name>
        <description>{description}</description>
        <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">
          ianaift:softwareLoopback
        </type>
        <enabled>true</enabled>
        <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
          <address>
            <ip>{ip}</ip>
            <netmask>{netmask}</netmask>
          </address>
        </ipv4>
      </interface>
  </interfaces>
</config>
"""

# Get loopback details from User
print("Let's create a new loopback interface.")
# New Loopback Details
loopback = {
    "int_name": "Loopback{}".format(input("What loopback number?\n")),
    "description": input("What interface description?\n"),
    "ip": input("What IP address?\n"),
    "netmask": input("What subnet mask?\n"),
}

# Connect with NETCONF
with manager.connect(
    host=device["address"],
    port=device["netconf_port"],
    username=device["username"],
    password=device["password"],
    hostkey_verify=False,
) as m:

    # Create desired NETCONF config payload and <edit-config>
    config = config_data.format(**loopback)
    try:
        r = m.edit_config(target="running", config=config)
    except RPCError as e:
        # Look for RPC error indicating access denied (or something else)
        print("There was an error ({}) with your transaction.".format(e.tag))
        exit(1)

    # Print OK status
    print("NETCONF RPC OK: {}".format(r.ok))
