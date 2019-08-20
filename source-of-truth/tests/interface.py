from pyats import aetest
from genie.conf import Genie
import logging
import os
import sys
from tabulate import tabulate
import pynetbox
import ipaddress

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
    def connect_to_devices(self, steps, testbed):
        for device in testbed.devices:
            with steps.start("Connecting to {}".format(device)):
                # print("CONNECTED (not really)")
                testbed.devices[device].connect(log_stdout=False)

    @aetest.subsection
    def load_netbox(self, testbed, steps):
        # testbed = self.parameters["testbed"]
        netbox_token = os.getenv("NETBOX_TOKEN")
        netbox_url = os.getenv("NETBOX_URL")

        site_name = os.getenv("NETBOX_SITE")
        tenant_name = os.getenv("NETBOX_TENANT")

        netbox = pynetbox.api(netbox_url, token=netbox_token)

        tenant = netbox.tenancy.tenants.get(name=tenant_name)
        mgmt_tenant = netbox.tenancy.tenants.get(name="Management")
        site = netbox.dcim.sites.get(name=site_name)

        for device in testbed.devices:
            with steps.start(
                "Pulling Device and Interface Info from Netbox."
            ) as step:
                testbed.devices[device].netbox = AttrDict()
                testbed.devices[
                    device
                ].netbox.device = netbox.dcim.devices.get(
                    site_id=site.id, tenant_id=tenant.id, name=device
                )
                if not testbed.devices[device].netbox.device is None:
                    testbed.devices[
                        device
                    ].netbox.device.interfaces = netbox.dcim.interfaces.filter(
                        device_id=testbed.devices[device].netbox.device.id
                    )
                    if (
                        not testbed.devices[device].netbox.device.interfaces
                        is None
                    ):
                        for interface in testbed.devices[
                            device
                        ].netbox.device.interfaces:
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
                # print("NETBOX-DEVICE: ", testbed.devices[device].netbox.device.__dict__)
                # print("Device {} interface {} ip {}".format(
                #     device,
                #     testbed.devices[device].netbox.device.interfaces[0].name,
                #     testbed.devices[device].netbox.device.interfaces[0].ip_addresses[0].ip
                # ))


# @aetest.loop(device = self.parent.testbed.devices)
class InterfaceTestCase(aetest.Testcase):
    @aetest.setup
    def setup(self, testbed):
        # testbed = self.parameters["testbed"]
        # netbox = self.parameters["netbox"]

        aetest.loop.mark(self.execute_test, uids=testbed.devices)
        # aetest.loop.mark(self.netbox_vlans_exist, uids=netbox.devices)

    @aetest.test
    def execute_test(self, section, steps, testbed):
        # print("Inside Test for {}".format(section.uid))
        device = testbed.devices[section.uid]
        # print("Interfaces: ", device.netbox.device.interfaces)

        enabled_interfaces = [
            interface
            for interface in device.netbox.device.interfaces
            if interface.enabled
        ]
        shutdown_interfaces = [
            interface
            for interface in device.netbox.device.interfaces
            if not interface.enabled
        ]

        routed_interfaces = [
            interface
            for interface in device.netbox.device.interfaces
            if interface.mode is None and interface.ip_addresses is not None
        ]

        trunk_interfaces = [
            interface
            for interface in device.netbox.device.interfaces
            if interface.mode is not None
            and interface.mode.label in ["Tagged All", "Tagged"]
        ]

        access_interfaces = [
            interface
            for interface in device.netbox.device.interfaces
            if interface.mode is not None and interface.mode.label == "Access"
        ]

        # print("Enabled interfaces: ", enabled_interfaces)
        # print("Trunk interfaces: ", trunk_interfaces)
        # print("Access interfaces: ", access_interfaces)
        # print("Routed interfaces:", routed_interfaces)

        # Preperation: Learn Operational State
        with steps.start("Learning operational state.") as step:
            device.learned_interfaces = device.learn("interface")
            # device.learned_trunks = device.parse("show interfaces trunk")
            if device.netbox.device.device_role.name in [
                "Distribution Switch",
                "Access Switch",
            ]:
                device.learned_switchport = device.parse(
                    "show interfaces switchport"
                )

        # TEST Verify Defined Interfaces Exist
        test_name = "Interface Exists Test"
        for interface in device.netbox.device.interfaces:
            with steps.start(
                "{}: {}".format(test_name, interface.name), continue_=True
            ) as step:
                if not interface.name in device.learned_interfaces.info:
                    step.failed("Interface doesn't exist")

        # TEST Enabled Interfaces are Operational
        test_name = "Interface Operational Test"
        for interface in enabled_interfaces:
            with steps.start(
                "{}: {}".format(test_name, interface.name), continue_=True
            ) as step:
                # print("Testing Interface {}".format(interface.name))
                if interface.name in device.learned_interfaces.info:
                    if not device.learned_interfaces.info[interface.name][
                        "enabled"
                    ]:
                        step.failed("Interface not enabled.")
                else:
                    step.skipped("Interface doesn't exist")

        # TEST Disabled Interfaces are Shutdown
        test_name = "Disabled Interface Test"
        for interface in shutdown_interfaces:
            with steps.start(
                "{}: {}".format(test_name, interface.name), continue_=True
            ) as step:
                # print("Testing Interface {}".format(interface.name))
                if interface.name in device.learned_interfaces.info:
                    if device.learned_interfaces.info[interface.name][
                        "enabled"
                    ]:
                        step.failed("Interface not Shutdown.")
                else:
                    step.skipped("Interface doesn't exist")

        # TEST Trunk Interfaces are Trunks (plus VLAN checks)
        if device.netbox.device.device_role.name in [
                "Distribution Switch",
                "Access Switch",
            ]:        
            test_name = "VLAN Trunks Test"
            for interface in trunk_interfaces:
                with steps.start(
                    "{}: {}".format(test_name, interface.name), continue_=True
                ) as step:
                    if interface.name in device.learned_switchport:
                        if (
                            not device.learned_switchport[interface.name][
                                "operational_mode"
                            ]
                            == "trunk"
                        ):
                            step.failed("Interface not currently trunking.")
                        # TODO - TEST TRUNKED VLAN
                        # elif :

                    else:
                        step.failed("Interface not configured as a switchport.")

        # TEST Access Interfaces are Access (plus Native VLAN)
        if device.netbox.device.device_role.name in [
                "Distribution Switch",
                "Access Switch",
            ]:        
            test_name = "Access Ports Test"
            for interface in access_interfaces:
                with steps.start(
                    "{}: {}".format(test_name, interface.name), continue_=True
                ) as step:
                    # print("Testing Interface {}".format(interface.name))
                    if interface.name in device.learned_switchport:
                        if (
                            not device.learned_switchport[interface.name][
                                "operational_mode"
                            ]
                            == "static access"
                        ):
                            step.failed("Interface not operating as access port.")
                        # TODO - TEST ACCESS VLAN
                        # elif :

                    else:
                        step.failed("Interface not configured as a switchport.")

        # TEST Routed Interfaces are Routed (plus IP Address)
        test_name = "Routed Interface Test"
        for interface in routed_interfaces:
            with steps.start(
                "{}: {}".format(test_name, interface.name), continue_=True
            ) as step:
                print("Testing Interface {}".format(interface.name))

                if interface.name in device.learned_interfaces.info:
                    if device.learned_interfaces.info[interface.name][
                        "switchport_enable"
                    ]:
                        step.failed("Interface configured as switchport.")
                    # TODO - Test for IP Address Configuration
                    # else:
                else:
                    step.skipped("Interface doesn't exist")


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
