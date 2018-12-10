#!/bin/env python

# To get a logger for the script
import logging
import json

# To build the table at the end
from tabulate import tabulate

# Needed for aetest script
from ats import aetest
from ats.log.utils import banner

# Genie Imports
from genie.conf import Genie
from genie.abstract import Lookup

# import the genie libs
from genie.libs import ops  # noqa

# Get your logger for your script
log = logging.getLogger(__name__)


###################################################################
#                  COMMON SETUP SECTION                           #
###################################################################


class common_setup(aetest.CommonSetup):
    """ Common Setup section """

    # CommonSetup have subsection.
    # You can have 1 to as many subsection as wanted

    # Connect to each device in the testbed
    @aetest.subsection
    def connect(self, testbed):
        genie_testbed = Genie.init(testbed)
        self.parent.parameters["testbed"] = genie_testbed
        device_list = []

        # Attempt to establish connection with each device
        for device in genie_testbed.devices.values():
            log.info(banner("Connect to device '{d}'".format(d=device.name)))
            try:
                device.connect()
            # If unable to connect, fail test
            except Exception as e:
                self.failed(
                    "Failed to establish connection to '{}'".format(
                        device.name
                    )
                )

            device_list.append(device)

        # Pass list of devices the to testcases
        self.parent.parameters.update(dev=device_list)


###################################################################
#                     TESTCASES SECTION                           #
###################################################################


class OSPF_Verify(aetest.Testcase):
    """ Test if OSPF is functioning properly """

    # First test section
    @aetest.test
    def learn_ospf(self):
        """ For each device in testbex, learn OSPF state.  OSPF details used in later tests. """

        self.all_ospf_sessions = {}
        for dev in self.parent.parameters["dev"]:
            log.info(
                banner("Gathering OSPF Information from {}".format(dev.name))
            )
            abstract = Lookup.from_device(dev)
            ospf = abstract.ops.ospf.ospf.Ospf(dev)
            ospf.learn()
            self.all_ospf_sessions[dev.name] = ospf

    @aetest.test
    def check_ospf_enabled(self):
        """ Verify that OSPF is enabled on the devices. """

        failed_dict = {}
        mega_tabular = []
        for device, ospf in self.all_ospf_sessions.items():
            # Create list for report row
            tr = []
            tr.append(device)

            # See if any OSPF data was learned from the device.
            try:
                default = ospf.info["vrf"]["default"]
                ipv4 = default["address_family"]["ipv4"]
                instance = ipv4["instance"][list(ipv4["instance"].keys())[0]]
                areas = instance["areas"]
                tr.append("Passed")
            # If OSPF information not available, OSPF is NOT configured on device
            except:
                failed_dict[device] = device
                tr.append("Failed")

            # Add row to log table
            mega_tabular.append(tr)

        # Log the test details
        log.info(
            tabulate(
                mega_tabular,
                headers=["Device", "Pass/Fail"],
                tablefmt="orgtbl",
            )
        )

        # If any devices failed, report error and fail test.
        if failed_dict:
            log.error(json.dumps(failed_dict, indent=3))
            self.failed("Testbed has devies with OSPF not enabled")

        else:
            self.passed("All devices are running OSPF")

    @aetest.test
    def check_ospf_neighbors_established(self):
        """ Verify all non-Passive interfaces have learned neighbors. """

        failed_dict = {}
        mega_tabular = []

        # Log table headers
        table_headers = [
            "Device",
            "Area",
            "Interface",
            "Neighbors",
            "Pass/Fail",
        ]

        # Loop over each device
        for device, ospf in self.all_ospf_sessions.items():

            # Attempt to look for neighbors on device. Exceptions indicate OSPF errors
            try:
                # Convenience variables for device
                default = ospf.info["vrf"]["default"]
                ipv4 = default["address_family"]["ipv4"]
                instance = ipv4["instance"][list(ipv4["instance"].keys())[0]]
                areas = instance["areas"]

                # Test each area configured on device
                for area, details in areas.items():
                    # Test each interface within the area
                    for interface, idetails in details["interfaces"].items():
                        # Row for device, area, and interface
                        tr = []
                        tr.append(device)
                        tr.append(area)
                        tr.append(interface)

                        # Only look for neighbors on non-Passive interfaces
                        if not idetails["passive"]:
                            # See if any neighbors are known on the interface
                            if "neighbors" in idetails.keys():
                                # Create a list of learned neighbors
                                neighbor_list = list(
                                    idetails["neighbors"].keys()
                                )  # [neighbor for neighbor in idetails["neighbors"]]
                                tr.append(",".join(neighbor_list))
                                tr.append("Passed")
                            # If not neighbors are found, fail test
                            else:
                                tr.append("NO NEIGHBORS FOUND")
                                tr.append("Failed")
                                failed_dict[
                                    "{device} {area} {interface}".format(
                                        device=device,
                                        area=area,
                                        interface=interface,
                                    )
                                ] = idetails
                        # Passive interfaces do NOT need to have neighbors
                        else:
                            tr.append("Passive Interface")
                            tr.append("Passed")

                        # Add row to table
                        mega_tabular.append(tr)
            # Exception indicate OSPF error
            except:
                failed_dict[device] = ""
                tr = []
                tr.append(device)
                tr.append("")
                tr.append("")
                tr.append("")
                tr.append("Failed")

                # Add row to table
                mega_tabular.append(tr)

        # Add results table to log
        log.info(
            tabulate(mega_tabular, headers=table_headers, tablefmt="orgtbl")
        )

        if failed_dict:
            log.error(json.dumps(failed_dict, indent=3))
            self.failed(
                "Testbed has devices with non-passive interfaces lacking OSPF neighbors"
            )

        else:
            self.passed("All all non-passive interfaces have OSPF neighbors")


# #####################################################################
# ####                       COMMON CLEANUP SECTION                 ###
# #####################################################################


# This is how to create a CommonCleanup
# You can have 0 , or 1 CommonCleanup.
# CommonCleanup can be named whatever you want :)
class common_cleanup(aetest.CommonCleanup):
    """ Common Cleanup for Sample Test """

    # CommonCleanup follow exactly the same rule as CommonSetup regarding
    # subsection
    # You can have 1 to as many subsections as wanted
    # here is an example of 1 subsection

    @aetest.subsection
    def clean_everything(self):
        """ Common Cleanup Subsection """
        log.info("Aetest Common Cleanup ")


if __name__ == "__main__":  # pragma: no cover
    aetest.main()
