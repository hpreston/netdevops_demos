#! /usr/bin/env python
"""Example script using Genie
Intended to be ran interactively (ie from iPython)

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

# Import Genie
from genie.conf import Genie

# Initialize a Testbed File
testbed = Genie.init("testbed.yml")

# Create variable for specific testbed device
device = testbed.devices["sbx-n9kv-ao"]

# Conenct to the device
device.connect()

# Learn the vlans using Genie model
vlans = device.learn("vlan")

# Print out VLAN ids and names.
print("Here are the vlans from device {}".format(device.name))
for key, details in vlans.info["vlans"].items():
    # The model for vlans.info has an oddity where the vlans are
    # mixed together with vlan configuration info so need a bit of
    # logic to just target the VLAN details and not config info.
    # See the model here: https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/_models/vlan.pdf

    # Ignore the config details by exclusing configuration keys
    if key in ["interface_vlan_enabled", "configuration", "vn_segment_vlan_based_enabled"]:
        # these aren't vlans, move along
        continue

    # Print details on vlans
    print("VLAN ID {} with name {}".format(details["vlan_id"], details["name"]))

device.disconnect()
