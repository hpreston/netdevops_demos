#! /usr/bin/env python
"""Sample script pulling secrets from NetBox to connect to device with NETCONF

*** Assumes you've setup NETBOX per the instructions in the demo README ***

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

from getpass import getpass
import pynetbox
from ncclient import manager
import xmltodict

# Assumes NetBox running localling on port 8081, update if needed
nb_url = "http://localhost:8081"

# Ask user for details about the device in question
device_name = input("What is your device name?\n")
nb_token = getpass("What is your NetBox API Token?\n")
private_key_file = input("Where is your Private Key for Secret Access?\n")

print("Retrieving device information and secrets from NetBox.")

# Create a NetBox API connection
nb = pynetbox.api(nb_url, token=nb_token, private_key_file=private_key_file)

# Retrieve device details
nb_device = nb.dcim.devices.get(name=device_name)

# Gather needed connection details for the device
# username, password and netconf_port being retrieved from NetBox Secret Store
device = {
    "address": nb_device.primary_ip.address.split("/")[0],
    "username": nb.secrets.secrets.get(
        device_id=nb_device.id, name="username"
    ).plaintext,
    "password": nb.secrets.secrets.get(
        device_id=nb_device.id, name="password"
    ).plaintext,
    "netconf_port": nb.secrets.secrets.get(
        device_id=nb_device.id, name="netconf_port"
    ).plaintext,
}

print("Connecting to device to retrieve interface list.")

# Connect to device with NETCONF
with manager.connect(
    host=device["address"],
    port=device["netconf_port"],
    username=device["username"],
    password=device["password"],
    hostkey_verify=False,
) as m:

    # NETCONF Filter for interfaces
    filter = """
    <filter>
      <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces" />
    </filter>
    """

    # <get-config>
    r = m.get_config("running", filter)

# Process XML and retrieve interface list
interfaces = xmltodict.parse(r.xml)["rpc-reply"]["data"]["interfaces"]["interface"]

# Print out list of interface names
print("Here are the interfaces from device {}".format(device["address"]))
for interface in interfaces:
    print(interface["name"])
