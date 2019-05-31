#! /usr/bin/env python
"""Script to setup NETCONF RBAC using NACM to allow PRIV01 users read access

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
from xml.dom import minidom

device = {
    "address": "ios-xe-mgmt-latest.cisco.com",
    "username": "developer",
    "password": "C1sco12345",
    "netconf_port": 10000,
}

# Make sure needed device connection info was found.
if None in device.values():
    raise Exception("Missing key piece of data to connect to device")

# NETCONF filter to retrieve current NACM policy
filter = """
<filter>
  <nacm xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-acm" />
</filter>
"""

# NETCONF payload adding rule for PRIV01 users read access to all models
data = """
<config>
  <nacm xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
    <rule-list>
      <name>only-get</name>
      <group>PRIV01</group>

      <rule>
        <name>deny-edit-config</name>
        <module-name>ietf-netconf</module-name>
        <rpc-name>edit-config</rpc-name>
        <access-operations>exec</access-operations>
        <action>deny</action>
      </rule>
      <rule>
        <name>allow-get</name>
        <module-name>ietf-netconf</module-name>
        <rpc-name>get</rpc-name>
        <access-operations>exec</access-operations>
        <action>permit</action>
      </rule>
      <rule>
        <name>allow-models</name>
        <module-name>*</module-name>
        <access-operations>read</access-operations>
        <action>permit</action>
      </rule>
    </rule-list>
  </nacm>
</config>
  """

# Connect to the device
with manager.connect(
    host=device["address"],
    port=device["netconf_port"],
    username=device["username"],
    password=device["password"],
    hostkey_verify=False,
) as m:

    # Get current NACM
    r = m.get(filter)
    print("Current NACM Configuration.")
    xml_doc = minidom.parseString(r.xml)
    print(xml_doc.toprettyxml(indent="  "))
    print("")

    # Add new rules
    print("Configuring NACM Rule to allow PRIV01 to GET")
    r = m.edit_config(target="running", config=data)
    print("NETCONF RPC OK: {}".format(r.ok))
