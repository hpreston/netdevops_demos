""" Sample functions for gathering basic system info using pyATS.

Copyright (c) 2018 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

# from ats.topology import loader
from genie.conf import Genie
from genie.abstract import Lookup
from genie.libs import ops
from genie import parsergen


def genie_prep(dev):
    """
    Connects and looks up platform parsers for device
    Returns an abstract object
    """
    # Device must be connected so that a lookup can be performed
    if not dev.is_connected():
        dev.connect()

    # Load the approprate platform parsers dynamically
    abstract = Lookup.from_device(dev)
    return abstract


def get_platform_info(dev):
    """
    Returns parsed and normalized platform details
    https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/genie_libs/#/models/platform
    """
    abstract = genie_prep(dev)

    # Find the Platform Parsers for this device
    parse = abstract.ops.platform.platform.Platform(dev)

    # Parse required commands, and return structured data
    parse.learn()
    return parse


def get_interfaces(dev):
    """
    Returns parsed and normalized interface details
    https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/genie_libs/#/models/interface
    """
    abstract = genie_prep(dev)

    # Find the Interface Parsers for this device
    parse = abstract.ops.interface.interface.Interface(dev)

    # Parse required commands, and return structured data
    parse.learn()
    return parse.info


def get_routing_info(dev):
    """
    Returns parsed and normalized routing details
    https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/genie_libs/#/models/routing
    """
    abstract = genie_prep(dev)

    # Find the Routing Parsers for this device
    parse = abstract.ops.routing.routing.Routing(dev)

    # Parse required commands, and return structured data
    parse.learn()
    return parse.info


def get_ospf_info(dev):
    """
    Returns parsed and normalized OSPF details
    https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/genie_libs/#/models/ospf
    """
    abstract = genie_prep(dev)

    # Find the Routing Parsers for this device
    parse = abstract.ops.ospf.ospf.Ospf(dev)

    # Parse required commands, and return structured data
    parse.learn()
    try:
        return parse.info
    except AttributeError:
        return False


def get_vlans(dev):
    """
    Returns parsed and normalized VLAN details
    https://pubhub.devnetcloud.com/media/pyats-packages/docs/genie/genie_libs/#/models/vlan
    """
    abstract = genie_prep(dev)

    # Find the Routing Parsers for this device
    parse = abstract.ops.vlan.vlan.Vlan(dev)

    # Parse required commands, and return structured data
    parse.learn()

    # Pull out VLANs from parsed data
    vlans = {}
    for key, value in parse.info["vlans"].items():
        try:
            if int(key):  # indicates a VLAN ID as a key
                vlans[key] = value
        except ValueError:  # This key NOT a vlan info
            pass

    return vlans


def crc_errors(dev):
    """
    Returns a dict of interfaces with CRC errors.
    All counters for interface returned.
    """
    interfaces = get_interfaces(dev)

    error_interfaces = {}
    for interface, details in interfaces.items():
        counters = details.get("counters")
        if counters:
            if "in_crc_errors" in counters:
                counters = details["counters"]
                if counters["in_crc_errors"] > 0:
                    error_interfaces[interface] = counters

    return error_interfaces


def get_arps(dev):
    """Retrieve the ARP entries from the device.
       ** As written only supports NX-OS devices.
    """
    # Output from NX-OS Device
    # Flags: * - Adjacencies learnt on non-active FHRP router
    #        + - Adjacencies synced via CFSoE
    #        # - Adjacencies Throttled for Glean
    #        CP - Added via L2RIB, Control plane Adjacencies
    #        PS - Added via L2RIB, Peer Sync
    #        RO - Re-Originated Peer Sync Entry
    #        D - Static Adjacencies attached to down interface
    #
    # IP ARP Table for all contexts
    # Total number of entries: 1
    # Address         Age       MAC Address     Interface       Flags
    # 10.0.2.2        00:04:55  5254.0012.3502  mgmt0

    abstract = genie_prep(dev)

    nxos_arp_command = "show ip arp vrf all"

    arps = parsergen.oper_fill_tabular(
        device=dev,
        show_command=nxos_arp_command,
        header_fields=["Address", "Age", "MAC Address", "Interface", "Flags"],
    )

    return arps.entries
