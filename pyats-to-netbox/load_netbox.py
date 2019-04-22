#! /usr/bin/env python
"""
"""

from genie_utils import *
from netbox_utils import *

# Script Entry Point
if __name__ == "__main__":
    # Use Arg Parse to retrieve device details
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--testbed", help="pyATS testbed file ", required=False, default="default_testbed.yaml"
    )
    parser.add_argument(
        "--device", help="Which devices to load from. If not provided, will load from all.", action="append", required=False
    )

    args = parser.parse_args()
    testbed_file = args.testbed
    devices = args.device

    testbed = load_testbed(testbed_file)

    print(testbed)
    print(devices)

    for device_name, device in testbed.devices.items():
        if devices is None or device_name in devices:
            print("Processing Testbed Device {}".format(device.name))

            # Create NetBox Device
            nb_device = netbox_device(device)
            print("  Created NetBox Device")

            # Learn Interfaces
            try:
                genie_interfaces = get_interfaces(device)
                for (
                    genie_interface,
                    genie_interface_details,
                ) in genie_interfaces.items():
                    nb_interface = netbox_device_interface_genie(
                        nb_device,
                        {"name": genie_interface, "details": genie_interface_details},
                    )
                    print("  Added Interface {}".format(genie_interface))
            except LookupError:
                # ToDo: See about building connections/cables between devices based on links
                # print("Genie Couldn't Learn Interfaces")
                # Add interfaces and info based on topology file
                for link in device.links:
                    link_interfaces = link.find_interfaces()
                    for interface in link_interfaces:
                        if interface.device.name == device.name:
                            testbed_interface = {
                                "name": interface.name,
                                "details": {
                                    "link": link.alias,
                                    "type": interface.type,
                                },
                            }
                            try:
                                testbed_interface["details"][
                                    "ipv4"
                                ] = interface.ipv4.with_prefixlen
                            except:
                                pass

                            nb_interface = netbox_device_interface_testbed(
                                nb_device, testbed_interface
                            )
                            print("  Added Interface {}".format(nb_interface.name))

            except:
                print("Something else broke")
