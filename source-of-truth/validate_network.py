from get_from_netbox import devices, vlans

from genie.conf import Genie
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--testbed", dest="testbed")
args, unknown = parser.parse_known_args()

def disconnect():
    for device in testbed.devices:
        testbed.devices[device].disconnect_all()


testbed = Genie.init(args.testbed)

print("Connecting to testbed devices")
for device in testbed.devices:
    testbed.devices[device].connect(log_stdout=False)

# VLAN Test - switches
print("Executing VLAN Test")
nb_vlan_set = set([(vlan.vid, vlan.name) for vlan in vlans])
internal_vlans = {
    (1003, "token-ring-default"),
    (1, "default"),
    (1002, "fddi-default"),
    (1005, "trnet-default"),
    (1004, "fddinet-default"),
}
for device in devices:
    if device.device_role.name in ["Distribution Switch", "Access Switch"]:
        print(
            "Device {}: Verifying VLANs from Netbox are Configured ".format(
                device.name
            )
        )
        testbed.devices[device.name].vlans = testbed.devices[
            device.name
        ].learn("vlan")
        device_vlan_set = set(
            [
                (int(vid), details["name"])
                for vid, details in testbed.devices[device.name]
                .vlans.info["vlans"]
                .items()
            ]
        )

        missing_vlans = nb_vlan_set.difference(device_vlan_set)
        extra_vlans = device_vlan_set.difference(nb_vlan_set).difference(
            internal_vlans
        )
        common_vlans = nb_vlan_set.intersection(device_vlan_set)

        if nb_vlan_set == device_vlan_set:
            print(" - VLANs Match")
        elif nb_vlan_set in device_vlan_set:
            print(" - Source of Truth VLANs are Configured on Device")
        else:
            print(" - Error: Source of Truth VLANs not configured on switch.")
            print("   Missing VLANs: ", missing_vlans)

        if len(extra_vlans) > 0:
            print(" - Extra VLANS: ", extra_vlans)

print("   \n")


