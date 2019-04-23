#! /usr/bin/env python
"""Script to populate an netbox with device details using pyATS/Genie

Requires Environment Variables to be set for:

NETBOX_TOKEN: API Token for netbox
NETBOX_URL: URL including transport and port. Example http://localhost:8080
NETBOX_SITE: Name of the netbox site to add devices to.

If your pyATS testbed file expects Environment Vars for credentials,
they will be needed as well.

Can take command line arguments to specify the following:
 - testbed
 - device

Run with --help for full details.

Script will add or update Devices in netbox based on the testbed including:
- Device Type based on Testbed Type
- Interfaces and IP Addresses
  - Based on Genie Learn or Testbed Connections if not learn-able
- Device Serial Number and Software Platform if learn-able with Genie

Script also will create Device Types and Platforms within netbox if not found.

Script expects the following to exist in netbox already:
- Manufacturer named "Cisco"

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
        "--testbed",
        help="pyATS testbed file. Uses default_testbed.yaml if not provided",
        required=False,
        default="default_testbed.yaml",
    )
    parser.add_argument(
        "--device",
        help="Which devices to load from. If not provided, will load from all.",
        action="append",
        required=False,
    )

    args = parser.parse_args()
    testbed_file = args.testbed
    devices = args.device

    # Read in the pyATS Testbed file
    testbed = load_testbed(testbed_file)

    # print(testbed)
    # print(devices)

    # Loop over testbed devices
    for device_name, device in testbed.devices.items():
        # Only process selected devices if provided.
        if devices is None or device_name in devices:
            print("Processing Testbed Device {}".format(device.name))

            # Create NetBox Device
            nb_device = netbox_device(device)
            print("  Created NetBox Device")

            # Learn Platform Info with Genie
            try:
                genie_platform = get_platform_info(device)
                nb_device = update_netbox_device(nb_device, genie_platform)
                print("  Updated Platform Info")
            except LookupError:
                print(
                    "Unable to learn platform details about device {}".format(
                        device.name
                    )
                )
            except:
                print(
                    "Some other error on platform details for device {}".format(
                        device.name
                    )
                )

            # Learn Interfaces with Genie
            try:
                genie_interfaces = get_interfaces(device)
                for (
                    genie_interface,
                    genie_interface_details,
                ) in genie_interfaces.items():
                    # Create new interface in netbox
                    nb_interface = netbox_device_interface_genie(
                        nb_device,
                        {
                            "name": genie_interface,
                            "details": genie_interface_details,
                        },
                    )
                    print("  Added Interface {}".format(genie_interface))
            except LookupError:
                # If Genie learn fails, try to populate Interfaces based on topology links
                # ToDo: See about building connections/cables between devices based on links
                # print("Genie Couldn't Learn Interfaces")
                # Add interfaces and info based on topology file
                for link in device.links:
                    # Discover the interfaces connected to the link
                    link_interfaces = link.find_interfaces()
                    for interface in link_interfaces:
                        # Idenfity the interface that is conencted to current device
                        if interface.device.name == device.name:
                            # Create a dictionary of key details about the interface
                            testbed_interface = {
                                "name": interface.name,
                                "details": {
                                    "link": link.alias,
                                    "type": interface.type,
                                },
                            }
                            # See if there is an IP address listed for this interface
                            try:
                                testbed_interface["details"][
                                    "ipv4"
                                ] = interface.ipv4.with_prefixlen
                            except:
                                pass

                            # Create interface in netbox for this testbed interface
                            nb_interface = netbox_device_interface_testbed(
                                nb_device, testbed_interface
                            )
                            print(
                                "  Added Interface {}".format(
                                    nb_interface.name
                                )
                            )

            except:
                print("Something else broke")
