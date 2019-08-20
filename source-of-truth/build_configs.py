from get_from_netbox import devices, vlans

from jinja2 import Template

with open("templates/vlan_configuration.j2") as f:
    vlan_template = Template(f.read())
with open("templates/interface_configuration.j2") as f:
    interface_template = Template(f.read())


for device in devices:
    print("Device {} of role {}".format(device.name, device.device_role))

    config = "! Source of Truth Generated Configuration\n"

    # Layer 2 VLANs - Only for roles = ["Distribution Switch", "Access Switch"]
    if device.device_role.name in ["Distribution Switch", "Access Switch"]:
        print(" - Building L2 VLAN Configuration for Device")
        config += vlan_template.render(vlans=vlans)

    # Interface Configurations
    print(" - Building Interface Configurations for Device")
    config += interface_template.render(interfaces=device.interfaces)

    # Generate Configuraiton File
    config_file_name = "configs/{}.cfg".format(device.name)
    with open(config_file_name, "w") as f:
        f.write(config)
