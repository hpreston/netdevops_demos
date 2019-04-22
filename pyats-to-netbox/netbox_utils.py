import pynetbox
import os

device_roles = {
    "CSR1000v": "router",
    "ASAv": "firewall",
    "NX-OSv 9000": "switch",
    "IOSvL2": "switch",
}

FF_1000BASE_T = 1000
FF_SFPPLUS = 1200
FF_OTHER = 32767

netbox_token = os.getenv("NETBOX_TOKEN")
netbox_url = os.getenv("NETBOX_URL")
netbox_site = os.getenv("NETBOX_SITE")

netbox = pynetbox.api(netbox_url, token=netbox_token)


def netbox_device(genie_device):
    # See if device exists
    nb_device = netbox.dcim.devices.get(name=genie_device.name)
    if nb_device is None:
        # Verify Device Type Exists
        nb_device_type = netbox.dcim.device_types.get(model=genie_device.type)
        if nb_device_type is None:
            nb_device_type = netbox.dcim.device_types.create(
                manufacturer=netbox.dcim.manufacturers.get(name="Cisco").id,
                model=genie_device.type,
                slug=str(genie_device.type).lower(),
                u_height=1,
            )
        nb_device = netbox.dcim.devices.create(
            name=genie_device.name,
            device_type=netbox.dcim.device_types.get(
                model=genie_device.type
            ).id,
            device_role=netbox.dcim.device_roles.get(
                name=device_roles[genie_device.type]
            ).id,
            site=netbox.dcim.sites.get(name=netbox_site).id,
            status=1,
            tags=[],
        )
    return nb_device


def netbox_interface(
    nb_device, interface_name, interface_description="", mgmt_only=False
):
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
    # Get vrf if present
    # Look for Managenment VRFs
    if vrf_name in ["Mgmt-intf", "Mgmt-vrf", "management"]:
        vrf = "oob_mgmt"
    else:
        vrf = vrf_name

    # Get a nb_vrf
    nb_vrf = netbox.ipam.vrfs.get(name=vrf)
    if nb_vrf is None:
        nb_vrf = netbox.ipam.vrfs.create(name=vrf)

    return nb_vrf


def netbox_ip4(
    address=None, prefix_len=None, prefix=None, nb_vrf=None, description=""
):
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
    if "description" in genie_interface["details"].keys():
        description = genie_interface["details"]["description"]
    else:
        description = ""

    # ToDO: Managmenet Check
    mgmt_only = False

    # ToDo: Add other details MTU, MAC
    # ToDo: For port-channels, bring in LAG info

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
            nb_ip4 = netbox_ip4(
                prefix=prefix,
                nb_vrf=nb_vrf,
                description="Configured on {} interface {}".format(
                    nb_device.name, nb_interface.name
                ),
            )

            nb_ip4.interface = nb_interface.id
            nb_ip4.save()

            # Identify Primary IPs
            if nb_vrf is not None and nb_vrf.name == "oob_mgmt":
                nb_device.primary_ip4 = nb_ip4.id
                nb_device.save()
            # ToDo: Add looking for address listed in Testbed file - VIRL uses console

    # return the nb_interface
    return nb_interface


def netbox_device_interface_testbed(nb_device, testbed_interface):
    """Mostly for ASAv"""
    description = testbed_interface["details"]["link"]

    # ToDO: Managmenet Check
    mgmt_only = False

    nb_interface = netbox_interface(
        nb_device,
        interface_name=testbed_interface["name"],
        interface_description=description,
        mgmt_only=mgmt_only,
    )

    if (
        "management" in testbed_interface["name"].lower()
        or "mgmt" in testbed_interface["name"].lower()
    ):
        nb_vrf = netbox_vrf("management")
    else:
        nb_vrf = None

    # If IP listed on interface, add to it
    if "ipv4" in testbed_interface["details"].keys():
        nb_ip4 = netbox_ip4(
            prefix=testbed_interface["details"]["ipv4"],
            nb_vrf=nb_vrf,
            description="Configured on {} interface {}".format(
                nb_device.name, nb_interface.name
            ),
        )

        nb_ip4.interface = nb_interface.id
        nb_ip4.save()

        # Identify Primary IPs
        if nb_vrf is not None and nb_vrf.name == "oob_mgmt":
            nb_device.primary_ip4 = nb_ip4.id
            nb_device.save()

    # return the nb_interface
    return nb_interface
