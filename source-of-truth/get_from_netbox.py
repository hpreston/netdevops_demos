import pynetbox
import os
import ipaddress

netbox_token = os.getenv("NETBOX_TOKEN")
netbox_url = os.getenv("NETBOX_URL")

site_name = os.getenv("NETBOX_SITE")
tenant_name = os.getenv("NETBOX_TENANT")

netbox = pynetbox.api(netbox_url, token=netbox_token)

tenant = netbox.tenancy.tenants.get(name=tenant_name)
mgmt_tenant = netbox.tenancy.tenants.get(name="Management")
site = netbox.dcim.sites.get(name=site_name)

prod_vlan_group = netbox.ipam.vlan_groups.get(
    site_id=site.id, name="Production"
)

# Get devices for site
devices = netbox.dcim.devices.filter(site_id=site.id, tenant_id=tenant.id)

# Fill in details
for device in devices:
    device.interfaces = netbox.dcim.interfaces.filter(device_id=device.id)
    for interface in device.interfaces:
        interface.ip_addresses = netbox.ipam.ip_addresses.filter(
            interface_id=interface.id
        )
        for ip_address in interface.ip_addresses:
            ip_address.ip = ipaddress.ip_address(
                ip_address.address.split("/")[0]
            )
            ip_address.network = ipaddress.ip_network(
                ip_address.address, strict=False
            )

# Get VLAN Info from Netbox
vlans = netbox.ipam.vlans.filter(site_id=site.id, group_id=prod_vlan_group.id)

# Retrieve Prefixes for VLANs
for vlan in vlans:
    try:
        vlan.prefix = netbox.ipam.prefixes.get(vlan_id=vlan.id)
    except Exception as e:
        print(e)
    # print("VLAN ID: {} Name {}".format(vlan.vid, vlan.name))
