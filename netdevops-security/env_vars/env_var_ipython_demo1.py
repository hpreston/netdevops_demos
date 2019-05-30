#! /usr/bin/env python
"""Simple script exploring Environment Variables with Python
Intended to be ran interactively (ie from iPython)

Before beginning, must set a series of environment variables from bash
  These reference a DevNet Always On Sandbox

# before ipython in bash
export SBX_ADDRESS=ios-xe-mgmt-latest.cisco.com
export SBX_NETCONF_PORT=10000
export SBX_USER=developer
export SBX_PASS=C1sco12345

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

# Execute all of the following from iPython

# Import the OS library
import os

# Print out all environment variables
os.environ

# Get value of relevant device information
os.environ["SBX_ADDRESS"]
os.environ["SBX_USER"]
os.environ["SBX_PASS"]

# See what happens when you try to access an ENVAR that doesn't exist
os.environ["SBX_MISSING"]

# Use os.getenv to lookup value or return None
address = os.getenv("SBX_ADDRESS")
missing = os.getenv("SBX_MISSING")

# See what values are
address
missing

# You can test if an env_var existed
missing is None

# Creating our Device information from EnvVars
device = {
    "address": os.getenv("SBX_ADDRESS"),
    "username": os.getenv("SBX_USER"),
    "password": os.getenv("SBX_PASS"),
    "netconf_port": os.getenv("SBX_NETCONF_PORT"),
}

device["address"]
device["username"]

# Creating a device where some infromation not available
bad_device = {
    "address": os.getenv("SBX_ADDRESS"),
    "username": os.getenv("SBX_USER"),
    "password": os.getenv("SBX_MISSING"),
    "netconf_port": os.getenv("SBX_NETCONF_PORT"),
}

# How we can verify all details exist
None in device.values()
None in bad_device.values()

# Great if check before continuing
if None in device.values():
    raise Exception("Missing key piece of data to connect to device")

# Import our Network Autoamtion libraries
from ncclient import manager
import xmltodict

# Use NETCONF to connect to device and retrieve interface list
with manager.connect(
    host=device["address"],
    port=device["netconf_port"],
    username=device["username"],
    password=device["password"],
    hostkey_verify=False,
) as m:

    filter = """
    <filter>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces" />
    </filter>
    """

    r = m.get_config("running", filter)

# Convert XML data into interface list
interfaces = xmltodict.parse(r.xml)["rpc-reply"]["data"]["interfaces"]["interface"]

# How many we get?
len(interfaces)

# Print out and process
for interface in interfaces:
    print(interface["name"])
