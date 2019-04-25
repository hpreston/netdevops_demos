"""Library of functions used to work with netbox.
"""

import pynetbox
import os

# Common mappings for device types and roles
device_roles = {
    "CSR1000v": "router",
    "ASAv": "firewall",
    "NX-OSv 9000": "switch",
    "IOSvL2": "switch",
    "OTHER": "other",
}

# Constants for Interface Form Factor IDs
FF_1000BASE_T = 1000
FF_SFPPLUS = 1200
FF_OTHER = 32767

# Pull in details about the netbox environment to use
netbox_token = os.getenv("NETBOX_TOKEN")
netbox_url = os.getenv("NETBOX_URL")
netbox_site_name = os.getenv("NETBOX_SITE")

# Create netbox API object
netbox = pynetbox.api(netbox_url, token=netbox_token)

def netbox_manufacturer(name):
    nb_manufacturer = netbox.dcim.manufacturers.get(name=name)
    if nb_manufacturer is None:
        # Create a slug from the name
        slug = (
            name.lower()
            .replace(" ", "-")
            .replace(",", "-")
            .replace(".", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        nb_manufacturer = netbox.dcim.manufacturers.create(
            name=name, slug=slug
        )
    return nb_manufacturer


def netbox_device(genie_device):
    """Get or Create a device in netbox based on a genie device object.
    """
    # See if device exists, if not create one.
    nb_device = netbox.dcim.devices.get(name=genie_device.name)
    if nb_device is None:
        nb_manufacturer = netbox_manufacturer("Cisco")

        # Verify Device Type Exists, if not create one.
        # ToDo: refactor to function
        nb_device_type = netbox.dcim.device_types.get(model=genie_device.type)
        if nb_device_type is None:
            device_slug=(
                str(genie_device.type).lower()
                .replace(" ", "-")
                .replace(",", "-")
                .replace(".", "_")
                .replace("(", "_")
                .replace(")", "_")
            )

            nb_device_type = netbox.dcim.device_types.create(
                manufacturer=nb_manufacturer.id,
                model=genie_device.type,
                slug=device_slug,
                u_height=1,
            )

        # Get the device role based on type. If not defined, set to "OTHER"
        if genie_device.type in device_roles:
            nb_device_role = netbox_device_role(
                device_roles[genie_device.type]
            )
        else:
            nb_device_role = netbox_device_role(device_roles["OTHER"])

        nb_site = netbox_site(netbox_site_name)

        # Create the device in netbox
        nb_device = netbox.dcim.devices.create(
            name=genie_device.name,
            device_type=netbox.dcim.device_types.get(
                model=genie_device.type
            ).id,
            device_role=nb_device_role.id,
            site=nb_site.id,
            status=1,
            tags=[],
        )
    return nb_device

def netbox_site(name):
    """Get or Create a netbox site object."""
    nb_site = netbox.dcim.sites.get(name=name)
    if nb_site is None:
        # Create a slug from the name
        slug = (
            name.lower()
            .replace(" ", "-")
            .replace(",", "-")
            .replace(".", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        nb_site = netbox.dcim.sites.create(
            name=name, slug=slug, status=1
        )
    return nb_site


def netbox_device_role(name):
    """Get or Create a netbox device role."""
    nb_role = netbox.dcim.device_roles.get(name=name)
    if nb_role is None:
        # Create a slug from the name
        slug = (
            name.lower()
            .replace(" ", "-")
            .replace(",", "-")
            .replace(".", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        nb_role = netbox.dcim.device_roles.create(
            name=name, slug=slug, color="c0c0c0"
        )
    return nb_role


def update_netbox_device(nb_device, genie_platform):
    """Update device details in netbox based on Genie platform info.
    """
    # Deice serial number
    nb_device.serial = genie_platform.chassis_sn

    # Device Platform - That is OS and Version
    platform_name = "{} {}".format(genie_platform.os, genie_platform.version)
    nb_platform = netbox_device_platform(platform_name)
    nb_device.platform = nb_platform.id

    # Save changes to netbox
    nb_device.save()

    return nb_device


def netbox_device_platform(name):
    """Get or Create a netbox Device Platform"""
    nb_platform = netbox.dcim.platforms.get(name=name)
    if nb_platform is None:
        # Create slug from name
        slug = (
            name.lower()
            .replace(" ", "-")
            .replace(",", "-")
            .replace(".", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
        nb_platform = netbox.dcim.platforms.create(name=name, slug=slug)
    return nb_platform


def netbox_interface(
    nb_device, interface_name, interface_description="", mgmt_only=False
):
    """Create and update a netbox interface object for a device."""
    # See if the interface exists
    nb_interface = netbox.dcim.interfaces.filter(
        device=nb_device.name, name=interface_name
    )
    # See if single item returned, if so, set to value
    if len(nb_interface) == 1:
        nb_interface = nb_interface[0]
    # Create Interface
    elif nb_interface is None or len(nb_interface) == 0:
        # Create New Interface
        nb_interface = netbox.dcim.interfaces.create(
            device=nb_device.id,
            name=interface_name,
            form_factor=FF_OTHER,
            enabled=True,
            mgmt_only=mgmt_only,
            description=interface_description,
        )
    else:
        print("More than one interface found.. that is odd.")
    return nb_interface


def netbox_vrf(vrf_name):
    """Get or Create a netbox VRF."""
    # Managmenet VRFs are named different things on Platforms
    # For lack of better option, creating a common "oob_mgmt" vrf to use
    if vrf_name in ["Mgmt-intf", "Mgmt-vrf", "management"]:
        vrf = "oob_mgmt"
    else:
        vrf = vrf_name

    # Get vrf if present, create if not
    nb_vrf = netbox.ipam.vrfs.get(name=vrf)
    if nb_vrf is None:
        nb_vrf = netbox.ipam.vrfs.create(name=vrf)

    return nb_vrf


def netbox_ip4(
    address=None, prefix_len=None, prefix=None, nb_vrf=None, description=""
):
    """Get or Create a netbox IP address object."""
    # Normalize input to slash notation
    if prefix is None:
        if address is not None and prefix_len is not None:
            prefix = "{}/{}".format(address, prefix_len)
        else:
            raise (
                ValueError("Need address and prefix_len if prefix not given")
            )

    # See if IP exists already
    # Question: What about tenant?
    # Question: Searches across VRFs?  Global?
    # Process if more than one is returned
    nb_ip4 = netbox.ipam.ip_addresses.get(address=prefix)

    # VRF Id
    try:
        vrf_id = nb_vrf.id
    except:
        vrf_id = None

    if nb_ip4 is None:
        # Create it
        nb_ip4 = netbox.ipam.ip_addresses.create(
            address=prefix, vrf=vrf_id, description=description
        )
    return nb_ip4


def netbox_device_interface_genie(nb_device, genie_interface):
    """Get or Create and Update device interface based on Genie model"""
    # If no description present, set to blank string
    if "description" in genie_interface["details"].keys():
        description = genie_interface["details"]["description"]
    else:
        description = ""

    # ToDO: Managmenet Check
    mgmt_only = False

    # ToDo: Add other details MTU, MAC
    # ToDo: For port-channels, bring in LAG info

    # Get a netbox interface object
    nb_interface = netbox_interface(
        nb_device,
        interface_name=genie_interface["name"],
        interface_description=description,
        mgmt_only=mgmt_only,
    )

    # Get vrf if present
    if "vrf" in genie_interface["details"].keys():
        nb_vrf = netbox_vrf(genie_interface["details"]["vrf"])
    else:
        nb_vrf = None

    # If IP listed on interface, add to it
    if "ipv4" in genie_interface["details"].keys():
        for prefix, prefix_details in genie_interface["details"][
            "ipv4"
        ].items():
            # Get netbox IP object
            nb_ip4 = netbox_ip4(
                prefix=prefix,
                nb_vrf=nb_vrf,
                description="Configured on {} interface {}".format(
                    nb_device.name, nb_interface.name
                ),
            )

            # Update IP with interface link
            nb_ip4.interface = nb_interface.id
            nb_ip4.save()

            # Identify Primary IPs - based on presence of Mgmt VRF
            if nb_vrf is not None and nb_vrf.name == "oob_mgmt":
                nb_device.primary_ip4 = nb_ip4.id
                nb_device.save()
            # ToDo: Add looking for address listed in Testbed file - VIRL uses console

    # return the nb_interface
    return nb_interface


def netbox_device_interface_testbed(nb_device, testbed_interface):
    """Get or Create and Update Device Interface based on Testbed details
        - Mostly for ASAv until ASA parsers/models available
    """
    description = testbed_interface["details"]["link"]

    # ToDO: Managmenet Check
    mgmt_only = False

    # Get netbox interface object
    nb_interface = netbox_interface(
        nb_device,
        interface_name=testbed_interface["name"],
        interface_description=description,
        mgmt_only=mgmt_only,
    )

    # Identify management interface to set VRF
    if (
        "management" in testbed_interface["name"].lower()
        or "mgmt" in testbed_interface["name"].lower()
    ):
        nb_vrf = netbox_vrf("management")
    else:
        nb_vrf = None

    # If IP listed on interface, add to it
    if "ipv4" in testbed_interface["details"].keys():
        # Get netbox IP object
        nb_ip4 = netbox_ip4(
            prefix=testbed_interface["details"]["ipv4"],
            nb_vrf=nb_vrf,
            description="Configured on {} interface {}".format(
                nb_device.name, nb_interface.name
            ),
        )

        # Add interface to ip object
        nb_ip4.interface = nb_interface.id
        nb_ip4.save()

        # Identify Primary IPs
        if nb_vrf is not None and nb_vrf.name == "oob_mgmt":
            nb_device.primary_ip4 = nb_ip4.id
            nb_device.save()

    # return the nb_interface
    return nb_interface
