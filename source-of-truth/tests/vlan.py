from pyats import aetest
from genie.conf import Genie
import logging
import os
import sys
from tabulate import tabulate

# from get_from_netbox import devices, vlans
from pyats.datastructures import AttrDict

log = logging.getLogger(__name__)

sys.path.insert(1, os.path.join(sys.path[0], ".."))


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def load_testbed(self, testbed):
        # add them to testscript parameters
        self.parent.parameters.update(testbed=testbed)

    @aetest.subsection
    def load_netbox(self, steps):
        with steps.start("Loading Devices and VLANs from Netbox."):
            from get_from_netbox import devices, vlans

            netbox = AttrDict()
            netbox.devices = devices
            netbox.vlans = vlans
            self.parent.parameters.update(netbox=netbox)

    @aetest.subsection
    def connect_to_devices(self, steps, testbed):
        for device in testbed.devices:
            with steps.start("Connecting to {}".format(device)):
                # print("CONNECTED (not really)")
                testbed.devices[device].connect(log_stdout=False)


# @aetest.loop(device = self.parent.testbed.devices)
class VlanTestCase(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        self.internal_vlans = {
            (1003, "token-ring-default"),
            (1, "default"),
            (1002, "fddi-default"),
            (1005, "trnet-default"),
            (1004, "fddinet-default"),
        }
        # testbed = self.parameters["testbed"]
        netbox = self.parameters["netbox"]

        # aetest.loop.mark(self.execute_test, uids=netbox.devices)
        aetest.loop.mark(self.execute_test, uids=testbed.devices)
        # aetest.loop.mark(self.netbox_vlans_exist, uids=netbox.devices)

    @aetest.test
    def execute_test(self, section, steps):
        testbed = self.parameters["testbed"]
        netbox = self.parameters["netbox"]

        device = testbed.devices[section.uid]
        for d in netbox.devices:
            if section.uid == d.name:
                nb_device = d
                break

        nb_vlan_set = set([(vlan.vid, vlan.name) for vlan in netbox.vlans])

        table = []
        table_headers = ["VLAN ID", "VLAN Name", "Status"]

        if nb_device.device_role.name in [
            "Distribution Switch",
            "Access Switch",
        ]:
            with steps.start("Learn VLANs on Device"):
                device.vlans = device.learn("vlan")
                device_vlan_set = set(
                    [
                        (int(vid), details["name"])
                        for vid, details in device.vlans.info["vlans"].items()
                    ]
                )

            with steps.start(
                "Verify Netbox VLANs exist", continue_=True
            ) as step:
                missing_vlans = nb_vlan_set.difference(device_vlan_set)
                if len(missing_vlans) > 0:
                    for v in missing_vlans:
                        table.append([v[0], v[1], "Missing"])
                    step.failed()
                else:
                    log.info("Device {} has all required vlans.")

            with steps.start(
                "Look for extra VLANs on device", continue_=True
            ) as step:
                extra_vlans = device_vlan_set.difference(
                    nb_vlan_set
                ).difference(self.internal_vlans)
                if len(extra_vlans) > 0:
                    for v in extra_vlans:
                        table.append([v[0], v[1], "Extra"])
                    step.failed()

            if len(table) > 0:
                log.error(
                    tabulate(table, headers=table_headers, tablefmt="orgtbl")
                )

        else:
            self.skipped("VLANs not required on this type of device.")


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect(self, steps, testbed):
        for device in testbed.devices:
            with steps.start("Disconnecting from {}".format(device)):
                # print("DISCONNECTED (not really)")
                testbed.devices[device].disconnect()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--testbed", dest="testbed", type=Genie.init)

    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))
