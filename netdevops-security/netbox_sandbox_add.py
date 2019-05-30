#! /usr/bin/env python
"""Add the IOS XE Latest AO Sandbox to NetBox

Quickly populate a local NetBox dev environment with details for the Sandbox

Setup is:
  - Site: NetDevOps Demos
  - Manufacturer: Cisco
  - Device Role: Router
  - Device Type: CSR1000v
  - Device: csr1000v-1 (IOS XE Latest Always On Sandbox)
    Interfaces:
    - Gig1 with IP 64.103.37.8/32
    - Gig2
    - Gig3

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


import pynetbox

# Token and URL for Dev NetBox
netbox_token = "0123456789abcdef0123456789abcdef01234567"
netbox_url = "http://localhost:8081"

# Create netbox API object
netbox = pynetbox.api(netbox_url, token=netbox_token)

# Create basic objects needed for device
site = netbox.dcim.sites.create(name="NetDevOps Demos", slug="netdevops_demos")
manufacturer = netbox.dcim.manufacturers.create(name="Cisco", slug="cisco", status=1)
device_role = netbox.dcim.device_roles.create(
    name="router", slug="router", color="c0c0c0"
)
device_type = netbox.dcim.device_types.create(
    manufacturer=manufacturer.id, model="CSR1000v", slug="csr1000v", u_height=0
)

# Create device
device = netbox.dcim.devices.create(
    name="csr1000v-1",
    device_type=device_type.id,
    device_role=device_role.id,
    site=site.id,
    status=1,
    tags=[],
)

# Create interfaces
gig1 = netbox.dcim.interfaces.create(
    device=device.id, name="GigabitEthernet1", form_factor=32767, enabled=True
)
gig2 = netbox.dcim.interfaces.create(
    device=device.id, name="GigabitEthernet2", form_factor=32767, enabled=True
)
gig3 = netbox.dcim.interfaces.create(
    device=device.id, name="GigabitEthernet3", form_factor=32767, enabled=True
)
# Yes a loop would work too :-)

# Create the Mgmt IP for the Sandbox
mgmt_ip = netbox.ipam.ip_addresses.create(
    address="64.103.37.8/32", description="IOS XE Latest Always On Sandbox IP"
)
mgmt_ip.interface = gig1.id
mgmt_ip.save()
device.primary_ip4 = mgmt_ip.id
device.save()

# Create a general secret role
secret_role = netbox.secrets.secret_roles.create(name="General", slug="general")
