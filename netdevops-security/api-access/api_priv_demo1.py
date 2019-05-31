#! /usr/bin/env python
"""Script to retrieve interface list using NETCONF

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
import xmltodict
from getpass import getpass

# Retrieve device details from environment variables
device = {
    "address": "ios-xe-mgmt-latest.cisco.com",
    "username": input("Network Username?\n"),
    "password": getpass("Network Password?\n"),
    "netconf_port": 10000,
}

# Make sure needed device connection info was found.
if None in device.values():
    raise Exception("Missing key piece of data to connect to device")

# Connect to device
with manager.connect(
    host=device["address"],
    port=device["netconf_port"],
    username=device["username"],
    password=device["password"],
    hostkey_verify=False,
) as m:

    # NETCONF filter for ietf-interfaces
    filter = """
    <filter>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces" />
    </filter>
    """

    # Send <get> operation
    r = m.get(filter)

# Get interface list from XML body
interfaces = xmltodict.parse(r.xml)["rpc-reply"]["data"]["interfaces"]["interface"]

# Print out interface list
print("Here are the interfaces from device {}".format(device["address"]))
for interface in interfaces:
    print(interface["name"])
